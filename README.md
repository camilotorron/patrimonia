# 📊 Patrimonia

**Aplicación de gestión de patrimonio personal** — Trackea y monitoriza tu patrimonio: cuentas corrientes, acciones, ETFs, fondos y criptomonedas con precios en tiempo real, cálculos automáticos de rentabilidad y gráficos de evolución.

## ✨ Features

### Gestión financiera
- 💼 **Cuentas** — Cuentas corrientes, de ahorro e inversión en múltiples bancos y monedas, con histórico de saldos
- 📈 **Activos** — Acciones, ETFs, fondos y criptos con precios automáticos vía yfinance
- 🔄 **Operaciones** — Registro de compras/ventas que actualizan automáticamente saldos y posiciones
  - Compra: activo existente o nuevo, cantidad por unidades o por importe (€)
  - Venta: solo activos existentes, validación de cantidad disponible
- 💹 **Rentabilidad** — Ganancias realizadas, no realizadas y totales por activo y global
- 📊 **Reportes** — Composición del portafolio, rentabilidad y analytics

### Gráficos y Dashboard
- 📊 **Dashboard con KPIs** — Patrimonio total, rentabilidad, valor de inversiones y efectivo
- 📉 **Evolución del Patrimonio Total** — Gráfico de líneas con 3 series: Total, Inversiones y Efectivo
- 📉 **Evolución de Inversiones por Tipo** — Desglose por ETF, Acciones, Fondos y Cripto
- 📉 **Evolución por Banco** — Patrimonio total (efectivo + inversiones) agrupado por banco
- 🥧 **Composición** — Doughnut charts de patrimonio (efectivo vs inversiones) y por tipo de activo
- 📉 **Evolución de Saldos por Cuenta** — Una línea por cuenta + línea total
- ⏱️ **Selector de escala temporal** — 1 semana, 1 mes, 6 meses, 1 año, 2 años, 5 años y Total (sincronizado entre gráficos)
- 🎨 **Código de color en Activos** — Agrupación por banco, orden de mayor a menor valor, filas en verde (+5%) o rojo (-5%)

### Operativa
- 🔄 **Importación CSV** — Carga masiva de operaciones históricas
- 🐳 **Docker** — Despliegue con Docker y Docker Compose
- ⏰ **Scheduler** — Actualización automática de precios y limpieza de cache (APScheduler)
- 🔒 **Audit Log** — Registro de auditoría de cambios
- ✅ **Tests** — Cobertura con pytest

## 🛠️ Tech Stack

| Capa | Tecnología |
|------|-----------|
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| **Database** | SQLite (dev), PostgreSQL (prod) |
| **Frontend** | HTML5, CSS3, JavaScript vanilla, Chart.js 4 + date-fns adapter |
| **External API** | yfinance (precios en tiempo real) |
| **Cache** | cachetools (TTLCache con TTL por tipo de activo) |
| **Scheduler** | APScheduler (actualización de precios automática) |
| **DevOps** | Docker, Docker Compose |
| **Code Quality** | Ruff (lint + format) |
| **Testing** | pytest, pytest-cov, httpx |
| **Package Manager** | Poetry |

## 🚀 Quick Start

### Opción 1: Docker (recomendado)

```bash
git clone https://github.com/yourusername/patrimonia.git
cd patrimonia
cp .env.example .env
docker-compose up -d
# App en http://localhost:8000
```

### Opción 2: Desarrollo local con Poetry

```bash
poetry install
make migrate
make seed        # opcional: datos de ejemplo interactivos
make run
# App en http://localhost:8000
# API docs en http://localhost:8000/docs
```

## 📁 Estructura del Proyecto

```
patrimonia/
├── backend/                     # API FastAPI + lógica de negocio
│   ├── app/
│   │   ├── main.py              # Punto de entrada de FastAPI
│   │   ├── config.py            # Configuración (pydantic-settings)
│   │   ├── database.py          # SQLAlchemy engine/session
│   │   ├── models/              # Modelos ORM (SQLAlchemy)
│   │   │   ├── account.py       # Cuenta bancaria
│   │   │   ├── account_balance.py  # Histórico de saldos
│   │   │   ├── asset.py         # Activo financiero
│   │   │   ├── operation.py     # Compra/venta
│   │   │   ├── price.py         # Precio histórico
│   │   │   ├── audit_log.py     # Log de auditoría
│   │   │   └── enums.py         # Enumeraciones (tipos, fuentes)
│   │   ├── schemas/             # Schemas de validación (Pydantic)
│   │   ├── dto/                 # Dataclasses (transfer objects)
│   │   ├── repositories/        # Capa de acceso a datos (Repository pattern)
│   │   ├── services/            # Lógica de negocio
│   │   │   ├── calculation_service.py   # Cálculos financieros y evolución
│   │   │   ├── operation_service.py     # Creación/reversión de operaciones
│   │   │   ├── price_service.py         # Gestión de precios
│   │   │   ├── price_provider.py        # Conector yfinance
│   │   │   ├── cache_service.py         # Cache TTL por tipo de activo
│   │   │   ├── scheduler.py             # Jobs programados (APScheduler)
│   │   │   ├── csv_importer.py          # Importación masiva
│   │   │   ├── account_service.py       # Gestión de cuentas
│   │   │   └── asset_service.py         # Gestión de activos
│   │   ├── routes/              # Endpoints REST
│   │   │   ├── accounts.py      # CRUD + evolución de saldos
│   │   │   ├── assets.py        # CRUD + snapshot + holdings
│   │   │   ├── operations.py    # CRUD + import CSV
│   │   │   ├── prices.py        # Histórico + refresh
│   │   │   ├── reports.py       # Summary, composition, returns, wealth-evolution
│   │   │   └── pages.py         # Páginas HTML (redirects)
│   │   └── utils/               # Helpers, constantes, decoradores
│   └── tests/                   # Tests unitarios e integración
├── frontend/                    # Frontend independiente (HTML/CSS/JS)
│   ├── dashboard.html           # KPIs + 5 gráficos de evolución
│   ├── accounts.html            # Tabla de cuentas + evolución de saldos
│   ├── assets.html              # Tabla de activos agrupada por banco
│   ├── operations.html          # Tabla de operaciones + modal compra/venta
│   ├── reports.html             # Composición, rentabilidad e histórico
│   ├── css/                     # Hojas de estilo (design system)
│   └── js/
│       ├── api.js               # Cliente API (fetch wrapper)
│       ├── app.js               # Lógica de UI y renderizado
│       └── charts.js            # Gráficos reutilizables (Chart.js)
├── init_data/                   # Datos iniciales (JSON)
│   ├── accounts.json
│   ├── etfs.json
│   ├── funds.json
│   └── stock.json
├── scripts/                     # Scripts de utilidad
│   ├── init_db.py               # Crear tablas
│   ├── import_initial_data.py   # Importar datos desde JSON
│   ├── seed_data.py             # Wizard interactivo de datos
│   └── backup.py                # Backup de BD
├── docs/                        # Documentación
│   ├── ARCHITECTURE.md
│   └── DEPLOYMENT.md
├── pyproject.toml               # Dependencias y configuración
├── Dockerfile                   # Imagen Docker multi-stage
├── docker-compose.yml           # Docker Compose (dev)
├── docker-compose.prod.yml      # Docker Compose (prod)
└── Makefile                     # Comandos comunes
```

## 🧑‍💻 Desarrollo

```bash
make help        # Ver todos los comandos disponibles
make install     # Instalar dependencias con Poetry
make dev         # Instalar dependencias de desarrollo
make run         # Levantar servidor de desarrollo (uvicorn --reload)
make test        # Ejecutar tests con cobertura
make lint        # Lint con ruff
make format      # Formatear código con ruff
make check       # Verificar formato y lint sin modificar
make migrate     # Crear tablas en la base de datos
make seed        # Wizard interactivo: registrar tu patrimonio
make import      # Importar datos iniciales desde init_data/*.json
make setup       # Configuración inicial: crear BD + importar datos
make backup      # Backup de la base de datos
make docker-up   # Levantar contenedores
make docker-down # Detener contenedores
```

## 📡 API Endpoints

### Cuentas
| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/v1/accounts` | Listar cuentas (filtros: skip, limit, active) |
| `POST` | `/api/v1/accounts` | Crear cuenta |
| `GET` | `/api/v1/accounts/{id}` | Obtener cuenta |
| `PUT` | `/api/v1/accounts/{id}` | Actualizar cuenta |
| `DELETE` | `/api/v1/accounts/{id}` | Eliminar cuenta |
| `GET` | `/api/v1/accounts/balance-evolution` | Evolución de saldos (para gráficos) |
| `GET` | `/api/v1/accounts/{id}/balance` | Saldo actual |
| `POST` | `/api/v1/accounts/{id}/balance` | Actualizar saldo |
| `GET` | `/api/v1/accounts/{id}/balance/history` | Histórico de saldos |
| `GET` | `/api/v1/accounts/{id}/summary` | Resumen financiero de una cuenta |

### Activos
| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/v1/assets` | Listar activos (filtros: skip, limit, type, active) |
| `POST` | `/api/v1/assets` | Crear activo |
| `GET` | `/api/v1/assets/{id}` | Obtener activo |
| `PUT` | `/api/v1/assets/{id}` | Actualizar activo |
| `DELETE` | `/api/v1/assets/{id}` | Desactivar activo (soft delete) |
| `GET` | `/api/v1/assets/overview/snapshot` | Snapshot con banco, cantidad, valor y rentabilidad |
| `GET` | `/api/v1/assets/search` | Buscar activos por ticker o nombre |
| `GET` | `/api/v1/assets/ticker/{ticker}` | Buscar activo por ticker |
| `GET` | `/api/v1/assets/{id}/holdings` | Posición actual: cantidad, precio medio, valor, ganancia |

### Operaciones
| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/v1/operations` | Listar operaciones (filtros: skip, limit, asset_id, account_id, type, dates) |
| `POST` | `/api/v1/operations` | Crear compra o venta (actualiza saldo automáticamente) |
| `GET` | `/api/v1/operations/{id}` | Obtener operación |
| `PUT` | `/api/v1/operations/{id}` | Actualizar operación (solo <7 días) |
| `DELETE` | `/api/v1/operations/{id}` | Eliminar operación (revierte el efecto en el saldo) |
| `POST` | `/api/v1/operations/import` | Importar CSV de operaciones |

### Precios
| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/v1/prices/asset/{id}` | Histórico de precios |
| `GET` | `/api/v1/prices/asset/{id}/latest` | Último precio registrado |
| `GET` | `/api/v1/prices/asset/{id}/current` | Precio actual |
| `POST` | `/api/v1/prices` | Crear precio manual |
| `POST` | `/api/v1/prices/refresh/{id}` | Actualizar precio de un activo |
| `POST` | `/api/v1/prices/refresh-all` | Actualizar todos los precios |
| `GET` | `/api/v1/prices/search` | Buscar precios |

### Reportes
| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/v1/reports/summary` | Resumen: patrimonio total, ganancia, efectivo, inversiones |
| `GET` | `/api/v1/reports/composition` | Composición por tipo de activo y por cuenta |
| `GET` | `/api/v1/reports/returns` | Rentabilidad por activo (realizada + no realizada) |
| `GET` | `/api/v1/reports/history` | Histórico de patrimonio |
| `GET` | `/api/v1/reports/wealth-evolution` | Evolución histórica: efectivo, inversiones y total con desglose por tipo y banco |

### Sistema
| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/health` | Health check básico |
| `GET` | `/health/detailed` | Health check con verificación de servicios |
| `GET` | `/version` | Nombre y versión de la aplicación |
| `GET` | `/docs` | Documentación Swagger UI |

## 🏗️ Arquitectura

La aplicación sigue una **arquitectura por capas** con separación clara de responsabilidades:

```
HTTP Request → Route (validación Pydantic) → Service (lógica de negocio)
    → Repository (aceso a datos) → Model (ORM) → Database
```

- **Repository Pattern**: `BaseRepository[T]` genérico para CRUD
- **DTO Pattern**: Dataclasses inmutables para transferencia entre capas
- **Service Layer**: Toda la lógica financiera en `CalculationService`
- Ver [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) para más detalle

## 📄 Licencia

MIT License — ver [LICENSE](LICENSE).