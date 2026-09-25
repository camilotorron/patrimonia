"""Servicio de cálculos financieros del portafolio.

Toda la lógica de cálculo de patrimonio, rentabilidad y composición vive aquí.
Recibe un :class:`~sqlalchemy.orm.Session` en el constructor para que las
operaciones sean testables y transaccionales.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dto import (
    AccountSummaryDTO,
    AssetSnapshotDTO,
    HoldingsDTO,
    PortfolioValueDTO,
    ReturnDTO,
)
from app.models.account import Account
from app.models.enums import OperationType
from app.models.operation import Operation
from app.repositories.account_repository import AccountRepository
from app.repositories.asset_repository import AssetRepository
from app.repositories.operation_repository import OperationRepository
from app.utils.helpers import safe_divide


class CalculationService:
    """Encapsula todos los cálculos financieros del portafolio."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.account_repo = AccountRepository(db)
        self.asset_repo = AssetRepository(db)
        self.operation_repo = OperationRepository(db)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _get_holdings(self, asset_id: int) -> tuple[Decimal, Decimal]:
        """Retorna (cantidad total, costo total) para un activo."""
        ops = self.operation_repo.get_by_asset(asset_id)
        quantity = Decimal("0")
        cost = Decimal("0")
        for op in ops:
            if op.operation_type == OperationType.BUY:
                quantity += op.quantity
                cost += op.quantity * op.unit_price + op.commission
            else:
                quantity -= op.quantity
                # Reducir el costo proporcionalmente
                if quantity > 0:
                    avg_cost = safe_divide(cost, quantity + op.quantity)
                    cost -= avg_cost * op.quantity
        return quantity, cost

    # ------------------------------------------------------------------ #
    # Cálculos por activo
    # ------------------------------------------------------------------ #
    def calculate_asset_value(
        self, quantity: Decimal, current_price: Decimal | None
    ) -> Decimal:
        """Valor de mercado de una posición."""
        if current_price is None:
            return Decimal("0")
        return quantity * current_price

    def calculate_cost_basis(self, asset_id: int) -> Decimal:
        """Costo total de compra (sin ventas)."""
        _, cost = self._get_holdings(asset_id)
        return cost

    def calculate_weighted_average_price(self, asset_id: int) -> Decimal:
        """Precio medio ponderado de compra."""
        quantity, cost = self._get_holdings(asset_id)
        return safe_divide(cost, quantity)

    def calculate_unrealized_return(
        self, asset_id: int, current_price: Decimal | None
    ) -> dict[str, Decimal]:
        """Ganancia/pérdida no realizada."""
        quantity, cost = self._get_holdings(asset_id)
        current_value = self.calculate_asset_value(quantity, current_price)
        gain = current_value - cost
        percentage = safe_divide(gain, cost) * Decimal("100")
        return {
            "total": gain,
            "percentage": percentage,
            "quantity_held": quantity,
            "current_value": current_value,
        }

    def calculate_realized_return(self, asset_id: int) -> dict[str, Decimal]:
        """Ganancia/pérdida realizada en ventas."""
        ops = self.operation_repo.get_by_asset(asset_id)
        holdings_qty = Decimal("0")
        holdings_cost = Decimal("0")
        realized = Decimal("0")
        trades = 0

        for op in ops:
            if op.operation_type == OperationType.BUY:
                holdings_qty += op.quantity
                holdings_cost += op.quantity * op.unit_price + op.commission
            else:  # SELL
                if holdings_qty > 0:
                    avg_cost = safe_divide(holdings_cost, holdings_qty)
                    proceeds = op.quantity * op.unit_price - op.commission
                    cost_portion = avg_cost * op.quantity
                    realized += proceeds - cost_portion
                    holdings_cost -= cost_portion
                    holdings_qty -= op.quantity
                    trades += 1

        return {"total": realized, "percentage": Decimal("0"), "trades_count": trades}

    def calculate_total_return(self, asset_id: int) -> ReturnDTO:
        """Rentabilidad total (realizada + no realizada)."""
        asset = self.asset_repo.get(asset_id)
        if asset is None:
            raise ValueError(f"Asset {asset_id} not found")

        realized = self.calculate_realized_return(asset_id)["total"]
        unreal = self.calculate_unrealized_return(asset_id, asset.current_price)
        total_gain = realized + unreal["total"]

        _, cost = self._get_holdings(asset_id)
        total_cost = cost + realized if realized < 0 else cost
        percentage = safe_divide(total_gain, total_cost) * Decimal("100")

        return ReturnDTO(
            asset_id=asset_id,
            ticker=asset.ticker,
            realized_gain=realized,
            unrealized_gain=unreal["total"],
            total_gain=total_gain,
            return_percentage=percentage,
        )

    def get_holdings(self, asset_id: int) -> HoldingsDTO:
        """Posición actual de un activo."""
        asset = self.asset_repo.get(asset_id)
        if asset is None:
            raise ValueError(f"Asset {asset_id} not found")

        quantity, cost = self._get_holdings(asset_id)
        current_value = self.calculate_asset_value(quantity, asset.current_price)
        gain = current_value - cost
        gain_pct = safe_divide(gain, cost) * Decimal("100")

        return HoldingsDTO(
            asset_id=asset_id,
            ticker=asset.ticker,
            quantity=quantity,
            average_price=safe_divide(cost, quantity),
            total_invested=cost,
            current_value=current_value,
            gain=gain,
            gain_percentage=gain_pct,
        )

    # ------------------------------------------------------------------ #
    # Cálculos de portafolio
    # ------------------------------------------------------------------ #
    def calculate_portfolio_value(
        self, account_id: int | None = None
    ) -> PortfolioValueDTO:
        """Valor del portafolio (opcionalmente filtrado por cuenta)."""
        if account_id is not None:
            ops = self.operation_repo.get_by_account(account_id)
        else:
            ops = self.operation_repo.get_all(limit=100000)

        invested = Decimal("0")
        current = Decimal("0")

        assets_seen: set[int] = set()
        for op in ops:
            if op.asset_id not in assets_seen:
                assets_seen.add(op.asset_id)

        for asset_id in assets_seen:
            h = self.get_holdings(asset_id)
            invested += h.total_invested
            current += h.current_value

        gain = current - invested
        pct = safe_divide(gain, invested) * Decimal("100")
        return PortfolioValueDTO(
            total_invested=invested,
            current_value=current,
            gain=gain,
            gain_percentage=pct,
        )

    def calculate_total_wealth(self) -> Decimal:
        """Patrimonio total = efectivo en cuentas + valor de activos."""
        accounts = self.account_repo.get_active()
        cash = sum((a.current_balance for a in accounts), Decimal("0"))
        portfolio = self.calculate_portfolio_value()
        return cash + portfolio.current_value

    def calculate_portfolio_composition(self) -> list[dict[str, Any]]:
        """Composición del portafolio agrupada por tipo de activo."""
        assets = self.asset_repo.get_active()
        by_type: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
        total = Decimal("0")

        for asset in assets:
            h = self.get_holdings(asset.id)
            by_type[asset.asset_type.value] += h.current_value
            total += h.current_value

        result = []
        for asset_type, value in by_type.items():
            result.append(
                {
                    "type": asset_type,
                    "value": value,
                    "percentage": safe_divide(value, total) * Decimal("100"),
                }
            )
        return result

    def get_all_assets_snapshot(self) -> list[AssetSnapshotDTO]:
        """Snapshot de todos los activos con datos actuales."""
        assets = self.asset_repo.get_active()
        snapshots = []
        for asset in assets:
            h = self.get_holdings(asset.id)
            snapshots.append(
                AssetSnapshotDTO(
                    asset_id=asset.id,
                    ticker=asset.ticker,
                    name=asset.name,
                    asset_type=asset.asset_type.value,
                    current_price=asset.current_price,
                    quantity=h.quantity,
                    current_value=h.current_value,
                    cost_basis=h.total_invested,
                    gain=h.gain,
                    gain_percentage=h.gain_percentage,
                )
            )
        return snapshots

    def get_account_summary(self, account_id: int) -> AccountSummaryDTO:
        """Resumen financiero de una cuenta."""
        account = self.account_repo.get(account_id)
        if account is None:
            raise ValueError(f"Account {account_id} not found")

        ops = self.operation_repo.get_by_account(account_id)
        asset_ids = {op.asset_id for op in ops}
        assets_value = Decimal("0")
        for asset_id in asset_ids:
            h = self.get_holdings(asset_id)
            assets_value += h.current_value

        total = account.current_balance + assets_value
        currencies = {account.currency: total}
        return AccountSummaryDTO(
            account_id=account_id,
            balance=account.current_balance,
            assets_value=assets_value,
            total=total,
            currencies=currencies,
        )

    def get_wealth_evolution(self) -> list[dict[str, Any]]:
        """Reconstruye la evolución histórica del patrimonio total.

        Combina dos fuentes de datos:
        - **Efectivo**: histórico de saldos de cuentas (AccountBalance) con un
          punto inicial que usa el ``current_balance`` actual.
        - **Inversiones**: cantidad acumulada de cada activo en cada fecha ×
          precio en esa fecha (de Price histórico o current_price si no hay).

        Retorna una lista de puntos ordenados por fecha, cada uno con:
        ``{"date", "cash", "investments", "total"}``
        """
        from app.models.account_balance import AccountBalance
        from app.models.price import Price

        # —— 1. Recopilar todas las fechas relevantes ——
        # Fechas de operaciones (cambian la cantidad de activos)
        all_ops = self.operation_repo.get_all(limit=100000)
        op_dates = {op.operation_date for op in all_ops}

        # Fechas de cambios de saldo (AccountBalance)
        balance_stmt = select(AccountBalance.recorded_at).order_by(
            AccountBalance.recorded_at
        )
        balance_dates = set(self.db.execute(balance_stmt).scalars().all())

        # Fechas de precios históricos
        price_stmt = select(Price.price_date).distinct().order_by(Price.price_date)
        price_dates = set(self.db.execute(price_stmt).scalars().all())

        # Combinar y ordenar todas las fechas — incluimos un punto inicial
        start_date = datetime(2024, 1, 1)
        all_dates = sorted(op_dates | balance_dates | price_dates | {start_date})
        if not all_dates:
            now = datetime.utcnow()
            return [
                {
                    "date": now,
                    "cash": self.calculate_total_wealth()
                    - self.calculate_portfolio_value().current_value,
                    "investments": self.calculate_portfolio_value().current_value,
                    "total": self.calculate_total_wealth(),
                }
            ]

        # —— 2. Pre-cargar datos para acceso eficiente ——
        assets = self.asset_repo.get_active()
        asset_ids = [a.id for a in assets]

        # Operaciones ordenadas por fecha, agrupadas por asset
        ops_by_asset: dict[int, list] = defaultdict(list)
        for op in sorted(all_ops, key=lambda o: o.operation_date):
            ops_by_asset[op.asset_id].append(op)

        # Precios históricos por asset: {asset_id: [(date, price), ...]}
        prices_by_asset: dict[int, list[tuple[datetime, Decimal]]] = {}
        if asset_ids:
            price_hist_stmt = (
                select(Price)
                .where(Price.asset_id.in_(asset_ids))
                .order_by(Price.price_date)
            )
            for price in self.db.execute(price_hist_stmt).scalars().all():
                prices_by_asset.setdefault(price.asset_id, []).append(
                    (price.price_date, price.price)
                )

        # Saldos de cuentas por fecha
        accounts = self.account_repo.get_all(limit=10000)
        account_ids = [a.id for a in accounts]

        balance_records: list = []
        if account_ids:
            bal_stmt = (
                select(AccountBalance)
                .where(AccountBalance.account_id.in_(account_ids))
                .order_by(AccountBalance.recorded_at)
            )
            balance_records = list(self.db.execute(bal_stmt).scalars().all())

        # —— 3. Estado acumulado que vamos avanzando en el tiempo ——
        # Cantidad acumulada de cada activo en cada momento.
        # Inicializamos con las cantidades actuales (holdings actuales) para que
        # el punto inicial (1 ene 2024) refleje el mismo valor que hoy.
        holdings_qty: dict[int, Decimal] = {}
        for aid in asset_ids:
            h = self._get_holdings(aid)
            holdings_qty[aid] = h[0]  # cantidad actual
        # Saldo de cada cuenta: punto inicial usa current_balance (igual que
        # balance-evolution). Los registros de AccountBalance sobrescriben
        # cuando existen, y las operaciones ajustan el flujo entre medias.
        account_balances: dict[int, Decimal] = {
            a.id: a.current_balance for a in accounts
        }

        # Pre-ordenar
        sorted_ops_all = sorted(all_ops, key=lambda o: o.operation_date)
        sorted_balances = sorted(balance_records, key=lambda b: b.recorded_at)

        # Iterar fechas combinadas, actualizando estado
        points: list[dict[str, Any]] = []

        # Si la primera fecha es muy posterior al inicio, añadir un punto inicial
        # con saldo 0 para que el gráfico empiece bien
        first_date = all_dates[0]
        # Punto inicial: antes de cualquier operación o saldo, todo es 0
        # Pero si hay saldos de cuenta iniciales, usarlos

        # Función auxiliar: precio de un asset en una fecha dada
        def get_price_at(asset_id: int, date: datetime) -> Decimal | None:
            """Mejor precio disponible en o antes de `date`."""
            # Buscar en históricos
            hist = prices_by_asset.get(asset_id, [])
            best = None
            for pd, pp in hist:
                if pd <= date:
                    best = pp
                else:
                    break
            if best is not None:
                return best
            # Fallback: current_price del asset
            asset = next((a for a in assets if a.id == asset_id), None)
            return asset.current_price if asset else None

        # —— 4. Recorrer fechas de hoy hacia atrás ——
        # Empezamos con el estado actual (cantidades y saldos de hoy) y
        # retrocedemos en el tiempo deshaciendo operaciones. Así el punto
        # más reciente tiene el valor real de hoy y los anteriores se
        # reconstruyen restando el impacto de cada operación.
        # IMPORTANTE: solo deshacemos operaciones cuando la fecha actual es
        # >= la fecha de la primera operación real. Para fechas anteriores
        # (ej. 2024-01-01), mantenemos el estado actual, ya que no hay datos
        # históricos para reconstruir un valor diferente.
        sorted_ops_desc = sorted(all_ops, key=lambda o: o.operation_date, reverse=True)

        # La primera operación real marca el límite: antes de ella, el estado
        # se mantiene igual que hoy.
        first_op_date = min(op.operation_date for op in all_ops) if all_ops else None

        op_ptr = 0
        # Snapshot del estado inicial (para fechas anteriores a la 1ª operación)
        initial_holdings = dict(holdings_qty)
        initial_cash = sum(account_balances.values(), Decimal("0"))

        # Iterar fechas de más reciente a más antigua
        for current_date in reversed(all_dates):
            # Solo deshacer operaciones si estamos en o después de la primera
            # operación real. Antes de esa fecha, el estado es el actual.
            if first_op_date and current_date >= first_op_date:
                while (
                    op_ptr < len(sorted_ops_desc)
                    and sorted_ops_desc[op_ptr].operation_date > current_date
                ):
                    op = sorted_ops_desc[op_ptr]
                    if op.operation_type == OperationType.BUY:
                        # Deshacer compra: restar cantidad
                        holdings_qty[op.asset_id] = (
                            holdings_qty.get(op.asset_id, Decimal("0")) - op.quantity
                        )
                    else:
                        # Deshacer venta: devolver cantidad
                        holdings_qty[op.asset_id] = (
                            holdings_qty.get(op.asset_id, Decimal("0")) + op.quantity
                        )
                    op_ptr += 1

            # Para fechas anteriores a la primera operación, usar estado inicial
            if first_op_date and current_date < first_op_date:
                qty_snapshot = initial_holdings
                cash = initial_cash
            else:
                qty_snapshot = holdings_qty
                cash = sum(account_balances.values(), Decimal("0"))

            investments = Decimal("0")
            # Desglose de inversiones por tipo de activo
            by_type: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
            # Desglose de patrimonio por banco (cash + investments de ese banco)
            by_bank: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))

            for aid in asset_ids:
                qty = qty_snapshot.get(aid, Decimal("0"))
                if qty > 0:
                    price = get_price_at(aid, current_date)
                    if price is not None:
                        val = qty * price
                        investments += val
                        asset = next((a for a in assets if a.id == aid), None)
                        if asset:
                            by_type[asset.asset_type.value] += val

            # Desglose por banco: cash de cada cuenta + investments de esa cuenta
            # Asignar investments al banco de la cuenta donde se compraron
            # Para simplificar: usar el banco de cada cuenta para el cash,
            # y para investments sumamos por tipo de cuenta.
            for acc in accounts:
                bank_name = acc.bank or "Sin banco"
                bank_cash = account_balances.get(acc.id, Decimal("0"))
                by_bank[bank_name] += bank_cash

            # Para investments por banco: asignar al banco de la cuenta de cada operación
            # Reconstruir investments por banco a partir de las ops ya procesadas
            # Simplificación: calcular investments por banco usando las cuentas
            # que tienen operaciones con cada activo
            if first_op_date and current_date >= first_op_date:
                # Estado reconstruido: usar ops hasta current_date
                ops_up_to_date = [
                    op for op in sorted_ops_all if op.operation_date <= current_date
                ]
            else:
                # Estado inicial: usar todas las ops (estado actual)
                ops_up_to_date = sorted_ops_all

            # Calcular investments por banco
            bank_investments: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
            # Agrupar holdings por cuenta/banco
            holdings_by_account: dict[int, dict[int, Decimal]] = defaultdict(
                lambda: dict(holdings_qty)
            )
            # En realidad, para asignar investments a bancos, necesitamos saber
            # qué cantidad de cada activo está en qué cuenta.
            # Aproximación: calcular por cuenta sumando sus operaciones
            for acc in accounts:
                bank_name = acc.bank or "Sin banco"
                acc_ops = [op for op in ops_up_to_date if op.account_id == acc.id]
                acc_holdings: dict[int, Decimal] = defaultdict(lambda: Decimal("0"))
                for op in acc_ops:
                    if op.operation_type == OperationType.BUY:
                        acc_holdings[op.asset_id] += op.quantity
                    else:
                        acc_holdings[op.asset_id] -= op.quantity
                acc_inv = Decimal("0")
                for aid, qty in acc_holdings.items():
                    if qty > 0:
                        price = get_price_at(aid, current_date)
                        if price is not None:
                            acc_inv += qty * price
                bank_investments[bank_name] += acc_inv

            for bank_name, inv_val in bank_investments.items():
                by_bank[bank_name] += inv_val

            points.append(
                {
                    "date": current_date,
                    "cash": cash,
                    "investments": investments,
                    "total": cash + investments,
                    "by_type": dict(by_type),
                    "by_bank": dict(by_bank),
                }
            )

        # Los puntos se generaron de más reciente a más antiguo; invertir
        points.reverse()
        return points
