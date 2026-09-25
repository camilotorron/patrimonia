# Plan de Desarrollo: Patrimonio Tracker
**Versión:** 1.0  
**Fecha:** 2026-09-25  
**Estado:** Planificación

---

## 📋 Índice
1. [Visión y Alcance](#visión-y-alcance)
2. [Fases del Proyecto](#fases-del-proyecto)
3. [Tareas Detalladas por Fase](#tareas-detalladas-por-fase)
4. [Estimaciones y Dependencias](#estimaciones-y-dependencias)
5. [Criterios de Aceptación](#criterios-de-aceptación)

---

## 🎯 Visión y Alcance

### Objetivo General
Crear una aplicación web para trackear y monitorizar el patrimonio personal, permitiendo gestionar múltiples tipos de activos (cuentas corrientes, ETFs, acciones, fondos) con cálculos automáticos de valor y rentabilidad.

### Alcance del MVP (Mínimo Producto Viable)
- ✅ Gestión de activos (crear, editar, eliminar)
- ✅ Registro de operaciones (compra/venta)
- ✅ Obtención de precios (integración yfinance)
- ✅ Cálculos de valor patrimonial y rentabilidad
- ✅ Reportes básicos y dashboards
- ✅ Interfaz web simple
- ✅ Despliegue con Docker

### Fuera del Alcance (Fase 2+)
- ❌ Integración bancaria automática
- ❌ Alertas y notificaciones
- ❌ Análisis técnico avanzado
- ❌ Importación masiva de datos
- ❌ Multi-usuario/autenticación

### Stack Tecnológico
- **Backend**: Python 3.11+, FastAPI
- **BD**: SQLite (dev), PostgreSQL (prod)
- **Frontend**: HTML5, CSS3, JavaScript vanilla + Chart.js
- **APIs Externas**: yfinance (precios)
- **DevOps**: Docker, Docker Compose
- **Testing**: pytest, pytest-cov
- **VCS**: Git/GitHub

---

## 📅 Fases del Proyecto

| Fase | Duración Estimada | Hitos |
|------|-------------------|-------|
| **Fase 1: Setup Inicial** | 2 días | Repo, estructura, CI/CD |
| **Fase 2: Backend Core** | 4 días | Modelos, API, lógica |
| **Fase 3: Integración de Datos** | 2 días | yfinance, caché, precios |
| **Fase 4: Frontend Básico** | 3 días | Páginas, formularios, tablas |
| **Fase 5: Reportes y Analytics** | 2 días | Dashboards, gráficos |
| **Fase 6: Testing y QA** | 2 días | Unit tests, integration tests |
| **Fase 7: DevOps y Deploy** | 2 días | Docker, scripts, documentación |
| **TOTAL** | ~17 días | MVP listo para producción |

---

## 🔧 Tareas Detalladas por Fase

---

## FASE 1: SETUP INICIAL (2 días)

### TAREA 1.1: Creación del repositorio y estructura base
**Objetivo**: Establecer la estructura de carpetas y archivos base del proyecto.

**Subtareas**:
- [ ] 1.1.1 Crear repositorio en GitHub
  - Nombre: `patrimonio-tracker`
  - Descripción: "Personal wealth management application"
  - Añadir .gitignore (Python)
  - Inicializar con README.md
  - Añadir CONTRIBUTING.md

- [ ] 1.1.2 Clonar repo localmente y crear estructura de carpetas
  ```
  patrimonio-tracker/
  ├── app/
  │   ├── __init__.py
  │   ├── main.py
  │   ├── config.py
  │   ├── models/
  │   │   ├── __init__.py
  │   │   ├── account.py
  │   │   ├── asset.py
  │   │   ├── operation.py
  │   │   └── price.py
  │   ├── schemas/
  │   │   ├── __init__.py
  │   │   ├── account.py
  │   │   ├── asset.py
  │   │   ├── operation.py
  │   │   └── price.py
  │   ├── routes/
  │   │   ├── __init__.py
  │   │   ├── accounts.py
  │   │   ├── assets.py
  │   │   ├── operations.py
  │   │   ├── prices.py
  │   │   └── reports.py
  │   ├── services/
  │   │   ├── __init__.py
  │   │   ├── price_service.py
  │   │   ├── calculation_service.py
  │   │   ├── operation_service.py
  │   │   └── cache_service.py
  │   ├── utils/
  │   │   ├── __init__.py
  │   │   ├── decorators.py
  │   │   ├── helpers.py
  │   │   └── constants.py
  │   └── database.py
  ├── tests/
  │   ├── __init__.py
  │   ├── conftest.py
  │   ├── test_models.py
  │   ├── test_routes.py
  │   ├── test_services.py
  │   └── fixtures/
  │       └── sample_data.py
  ├── static/
  │   ├── css/
  │   │   ├── style.css
  │   │   └── dashboard.css
  │   ├── js/
  │   │   ├── app.js
  │   │   ├── charts.js
  │   │   └── api.js
  │   └── images/
  ├── templates/
  │   ├── base.html
  │   ├── index.html
  │   ├── dashboard.html
  │   ├── accounts.html
  │   ├── assets.html
  │   ├── operations.html
  │   ├── reports.html
  │   └── components/
  │       ├── navbar.html
  │       ├── sidebar.html
  │       └── modals.html
  ├── docs/
  │   ├── API.md
  │   ├── DATABASE.md
  │   ├── ARCHITECTURE.md
  │   └── DEPLOYMENT.md
  ├── scripts/
  │   ├── init_db.py
  │   ├── seed_data.py
  │   └── migrate.py
  ├── .github/
  │   └── workflows/
  │       ├── ci.yml
  │       └── tests.yml
  ├── requirements.txt
  ├── requirements-dev.txt
  ├── pytest.ini
  ├── Dockerfile
  ├── docker-compose.yml
  ├── .env.example
  ├── .gitignore
  ├── README.md
  ├── CONTRIBUTING.md
  └── LICENSE
  ```

**Criterios de aceptación**:
- ✅ Repo visible en GitHub
- ✅ Todas las carpetas creadas localmente
- ✅ .gitignore configurado correctamente
- ✅ Primer commit realizado

---

### TAREA 1.2: Configuración de dependencias y virtual environment
**Objetivo**: Establecer el entorno Python y las dependencias del proyecto.

**Subtareas**:
- [ ] 1.2.1 Crear y activar virtual environment
  ```bash
  python -m venv venv
  source venv/bin/activate  # Linux/Mac
  # o: venv\Scripts\activate  # Windows
  ```

- [ ] 1.2.2 Crear `requirements.txt` con dependencias principales
  ```
  # Framework web
  fastapi==0.104.1
  uvicorn[standard]==0.24.0
  
  # Base de datos
  sqlalchemy==2.0.23
  alembic==1.13.0
  psycopg2-binary==2.9.9  # PostgreSQL adapter
  
  # Validación y schemas
  pydantic==2.5.0
  pydantic-settings==2.1.0
  
  # APIs externas
  yfinance==0.2.32
  requests==2.31.0
  
  # Utilidades
  python-dotenv==1.0.0
  python-dateutil==2.8.2
  pytz==2023.3
  
  # Testing
  pytest==7.4.3
  pytest-asyncio==0.21.1
  pytest-cov==4.1.0
  httpx==0.25.2
  
  # Desarrollo
  black==23.12.0
  flake8==6.1.0
  isort==5.13.2
  ```

- [ ] 1.2.3 Crear `requirements-dev.txt` con dependencias de desarrollo
  ```
  -r requirements.txt
  pytest-watch==4.2.0
  jupyter==1.0.0
  ipython==8.18.1
  ```

- [ ] 1.2.4 Instalar todas las dependencias
  ```bash
  pip install -r requirements-dev.txt
  ```

- [ ] 1.2.5 Crear archivo `.env.example` con variables de configuración
  ```
  # Database
  DATABASE_URL=sqlite:///./patrimonio.db
  # DATABASE_URL=postgresql://user:password@localhost/patrimonio
  
  # API
  API_HOST=0.0.0.0
  API_PORT=8000
  API_DEBUG=True
  
  # yFinance
  YFINANCE_TIMEOUT=10
  PRICE_CACHE_TTL=3600
  
  # Logging
  LOG_LEVEL=INFO
  ```

- [ ] 1.2.6 Crear `.gitignore` adicional (si no existe)
  ```
  venv/
  __pycache__/
  *.pyc
  .pytest_cache/
  .coverage
  htmlcov/
  dist/
  build/
  *.egg-info/
  .env
  .env.local
  *.db
  *.log
  .DS_Store
  ```

**Criterios de aceptación**:
- ✅ Virtual environment creado y activado
- ✅ Todas las dependencias instaladas sin errores
- ✅ `pip freeze` muestra versiones correctas
- ✅ `.env.example` presente y válido
- ✅ Archivos importables desde Python (`import fastapi` funciona)

---

### TAREA 1.3: Configuración de FastAPI y estructura base
**Objetivo**: Crear la aplicación FastAPI base y configuración principal.

**Subtareas**:
- [ ] 1.3.1 Crear `app/config.py` con configuración centralizada
  ```python
  # Leer variables de entorno, tipos, valores por defecto
  # Enum para ENVIRONMENT (dev, test, prod)
  # Configuración de logging
  # Configuración de BD
  # Configuración de cache
  ```

- [ ] 1.3.2 Crear `app/main.py` con la aplicación FastAPI base
  ```python
  # Instanciar FastAPI
  # Configurar CORS
  # Configurar eventos de startup/shutdown
  # Incluir routers (vacíos por ahora)
  # Health check endpoint GET /health
  # Endpoint de versión GET /version
  ```

- [ ] 1.3.3 Crear `app/__init__.py` con exports principales

- [ ] 1.3.4 Crear `app/database.py` con configuración SQLAlchemy
  ```python
  # Base declarativa
  # SessionLocal factory
  # Funciones de conectividad (test connection)
  # Soporte para SQLite y PostgreSQL
  ```

- [ ] 1.3.5 Crear script de inicio `run.py` en raíz
  ```python
  # Punto de entrada para dev
  # uvicorn.run con auto-reload
  ```

**Criterios de aceptación**:
- ✅ `python run.py` levanta servidor en localhost:8000
- ✅ GET /health retorna `{"status": "ok"}`
- ✅ GET /version retorna versión actual
- ✅ Documentación automática en /docs
- ✅ No hay errores de import

---

### TAREA 1.4: Configuración de Docker y docker-compose
**Objetivo**: Preparar contenedores para desarrollo y producción.

**Subtareas**:
- [ ] 1.4.1 Crear `Dockerfile` multi-stage
  ```dockerfile
  # Stage 1: Builder
  # - Python 3.11 slim
  # - Instalar dependencias del sistema (build-essential, etc)
  # - Crear venv
  # - Instalar requirements.txt
  
  # Stage 2: Runtime
  # - Copiar venv del builder
  # - Usuario no-root
  # - Healthcheck
  # - CMD con uvicorn
  ```

- [ ] 1.4.2 Crear `docker-compose.yml` con servicios
  ```yaml
  # Servicio 'app' (FastAPI)
  # Servicio 'db' (PostgreSQL, opcional)
  # Volumes para desarrollo
  # Networks
  # Variables de entorno
  # Puertos mapeados
  ```

- [ ] 1.4.3 Crear `.dockerignore`
  ```
  __pycache__
  .git
  .gitignore
  .env
  *.pyc
  venv/
  .pytest_cache/
  .coverage
  ```

- [ ] 1.4.4 Crear scripts de ayuda en `scripts/`
  ```bash
  docker-build.sh    # Build imagen
  docker-run.sh      # Run contenedor
  docker-clean.sh    # Limpia volúmenes
  docker-logs.sh     # Ver logs
  ```

**Criterios de aceptación**:
- ✅ `docker build -t patrimonio:latest .` sin errores
- ✅ `docker-compose up` levanta app en puerto 8000
- ✅ `docker-compose down` detiene servicios limpiamente
- ✅ Volumen compartido permite hot-reload en dev

---

### TAREA 1.5: Configuración de CI/CD con GitHub Actions
**Objetivo**: Automatizar tests y checks en cada push.

**Subtareas**:
- [ ] 1.5.1 Crear `.github/workflows/tests.yml`
  ```yaml
  on: [push, pull_request]
  
  jobs:
    test:
      runs-on: ubuntu-latest
      strategy:
        python-version: [3.11, 3.12]
      steps:
        - Checkout
        - Setup Python
        - Install dependencies
        - Run tests con coverage
        - Upload coverage a Codecov
  ```

- [ ] 1.5.2 Crear `.github/workflows/lint.yml`
  ```yaml
  on: [push, pull_request]
  
  jobs:
    lint:
      runs-on: ubuntu-latest
      steps:
        - Checkout
        - Setup Python
        - Install dependencies
        - Run black --check
        - Run flake8
        - Run isort --check
  ```

- [ ] 1.5.3 Crear `.github/workflows/security.yml`
  ```yaml
  # Bandit para seguridad en código Python
  # Dependabot para vulnerabilidades en deps
  ```

**Criterios de aceptación**:
- ✅ Workflows aparecen en GitHub Actions
- ✅ Pasan en commit inicial
- ✅ Se ejecutan automáticamente en PRs

---

### TAREA 1.6: Documentación inicial y README
**Objetivo**: Crear documentación base del proyecto.

**Subtareas**:
- [ ] 1.6.1 Completar `README.md`
  ```markdown
  # Patrimonio Tracker
  
  - Descripción breve
  - Features principales
  - Tech stack
  - Instalación rápida (Docker)
  - Desarrollo local
  - Estructura de carpetas
  - API endpoints básicos
  - Contribuir
  - Licencia
  ```

- [ ] 1.6.2 Crear `docs/ARCHITECTURE.md`
  ```markdown
  - Diagramas de arquitectura
  - Flujo de datos
  - Decisiones de diseño
  - Stack justificado
  ```

- [ ] 1.6.3 Crear `docs/DATABASE.md`
  ```markdown
  - Schema ERD (ASCII o imagen)
  - Relaciones
  - Índices
  - Migración de esquema
  ```

- [ ] 1.6.4 Crear `CONTRIBUTING.md`
  ```markdown
  - Git workflow (gitflow)
  - Convención de commits
  - Proceso de PR
  - Coding style (Black, isort)
  - Testing requirements
  ```

**Criterios de aceptación**:
- ✅ README muestra cómo levantar app en 5 min
- ✅ Documentación coherente y navegable
- ✅ Diagramas claros

---

## FASE 2: BACKEND CORE (4 días)

### TAREA 2.1: Diseño y creación de modelos de base de datos
**Objetivo**: Definir estructura de datos persistente.

**Subtareas**:
- [ ] 2.1.1 Crear modelo `Account` (Cuentas corrientes)
  ```python
  # Campos:
  # - id (PK)
  # - name (str, unique)
  # - account_type (enum: Corriente, Ahorro, Inversión)
  # - bank (str)
  # - iban (str, nullable)
  # - currency (str, default EUR)
  # - current_balance (Decimal)
  # - created_at
  # - updated_at
  # - is_active (bool, default True)
  
  # Relaciones:
  # - operations (1:M) - historial de ingresos/egresos
  ```

- [ ] 2.1.2 Crear modelo `Asset` (Activos: acciones, ETFs, fondos)
  ```python
  # Campos:
  # - id (PK)
  # - ticker (str, unique dentro del asset_type)
  # - asset_type (enum: Stock, ETF, Fund, Crypto, Other)
  # - name (str)
  # - description (str, nullable)
  # - currency (str, default EUR)
  # - current_price (Decimal, nullable) - último precio conocido
  # - price_updated_at (datetime, nullable)
  # - is_active (bool)
  # - manual_price (bool) - indica si precio es manual
  # - created_at
  # - updated_at
  
  # Relaciones:
  # - operations (1:M) - compras/ventas
  # - prices (1:M) - histórico de precios
  ```

- [ ] 2.1.3 Crear modelo `Operation` (Compras/ventas)
  ```python
  # Campos:
  # - id (PK)
  # - asset_id (FK)
  # - account_id (FK)
  # - operation_type (enum: Buy, Sell)
  # - quantity (Decimal)
  # - unit_price (Decimal)
  # - total_amount (Decimal)
  # - commission (Decimal, default 0)
  # - operation_date (datetime)
  # - notes (str, nullable)
  # - created_at
  # - updated_at
  
  # Relaciones:
  # - asset (N:1)
  # - account (N:1)
  ```

- [ ] 2.1.4 Crear modelo `Price` (Histórico de precios)
  ```python
  # Campos:
  # - id (PK)
  # - asset_id (FK)
  # - price (Decimal)
  # - price_date (datetime)
  # - source (enum: yfinance, manual, api)
  # - created_at
  
  # Relaciones:
  # - asset (N:1)
  
  # Índice compuesto: (asset_id, price_date)
  ```

- [ ] 2.1.5 Crear modelo `PriceCache` (Caché de precios)
  ```python
  # Campos:
  # - id (PK)
  # - asset_id (FK)
  # - price (Decimal)
  # - cached_at (datetime)
  # - expires_at (datetime)
  # - source (str)
  ```

- [ ] 2.1.6 Implementar BaseModel común
  ```python
  # Clase base para todos los modelos con:
  # - id (Integer PK)
  # - created_at (DateTime, auto)
  # - updated_at (DateTime, auto)
  # - Métodos: to_dict(), __repr__()
  ```

- [ ] 2.1.7 Crear índices y constraints
  ```python
  # Índices:
  # - Account.name (UNIQUE)
  # - Asset.ticker + asset_type (UNIQUE)
  # - Operation.asset_id, account_id
  # - Operation.operation_date
  # - Price.asset_id, price_date (UNIQUE, composite)
  # - PriceCache.asset_id (UNIQUE)
  
  # Constraints:
  # - Cantidad en operaciones > 0
  # - Precio > 0
  # - Total_amount = quantity * unit_price (check)
  # - operation_date <= now()
  ```

**Criterios de aceptación**:
- ✅ Modelos definidos con SQLAlchemy ORM
- ✅ Relaciones bidireccionales funcionales
- ✅ Índices y constraints aplicados
- ✅ `python -c "from app.models import *"` sin errores
- ✅ Diagrama ERD generado

---

### TAREA 2.2: Creación de schemas Pydantic para validación
**Objetivo**: Definir validación de entrada/salida de datos.

**Subtareas**:
- [ ] 2.2.1 Crear schemas para `Account`
  ```python
  # AccountBase: campos comunes
  # AccountCreate: para POST (sin id, timestamps)
  # AccountUpdate: para PUT/PATCH (campos opcionales)
  # AccountRead: para GET (completo con id, timestamps)
  # AccountInDB: para interno (derived fields)
  
  # Validaciones:
  # - name: no vacío, 1-255 caracteres
  # - currency: ISO 4217 válido
  # - current_balance: >= 0
  # - account_type: enum válido
  ```

- [ ] 2.2.2 Crear schemas para `Asset`
  ```python
  # AssetBase, AssetCreate, AssetUpdate, AssetRead
  
  # Validaciones:
  # - ticker: no vacío, 1-20 caracteres, alphanumeric
  # - name: 1-255 caracteres
  # - asset_type: enum válido
  # - currency: ISO 4217 válido
  # - current_price: > 0 si presente
  # - manual_price: bool
  ```

- [ ] 2.2.3 Crear schemas para `Operation`
  ```python
  # OperationBase, OperationCreate, OperationUpdate, OperationRead
  
  # Validaciones:
  # - quantity: > 0, Decimal con 8 decimales
  # - unit_price: > 0
  # - commission: >= 0
  # - operation_date: <= hoy
  # - operation_type: enum válido (Buy/Sell)
  # - Validación custom: total_amount = quantity * unit_price
  ```

- [ ] 2.2.4 Crear schemas para `Price`
  ```python
  # PriceBase, PriceCreate, PriceRead
  
  # Validaciones:
  # - price: > 0
  # - price_date: <= hoy
  # - source: enum válido
  ```

- [ ] 2.2.5 Crear schemas derivados para respuestas complejas
  ```python
  # AccountReadWithOperations: Account + lista de operaciones
  # AssetReadWithOperations: Asset + lista de operaciones
  # PortfolioSummary: patrimonio total, composición
  # OperationReadFull: incluye datos de asset y account
  ```

- [ ] 2.2.6 Crear validadores personalizados
  ```python
  # @validator
  # - Validar ticker solo caracteres válidos
  # - Validar IBAN formato
  # - Validar que cantidad y precio sean positivos
  # - Validar fechas no futuras
  ```

**Criterios de aceptación**:
- ✅ Todos los schemas importables
- ✅ Validaciones funcionan con datos válidos e inválidos
- ✅ Errores de validación son informativos
- ✅ Ejemplos en docstrings de cada schema

---

### TAREA 2.3: Implementar servicio de base de datos y DAOs
**Objetivo**: Crear capa de acceso a datos reutilizable.

**Subtareas**:
- [ ] 2.3.1 Crear clase `Repository` base genérica
  ```python
  # Métodos:
  # - get(id) -> T
  # - get_all(skip, limit) -> List[T]
  # - create(obj) -> T
  # - update(id, obj) -> T
  # - delete(id) -> bool
  # - filter_by(**kwargs) -> List[T]
  
  # Tipado genérico con TypeVar
  # Manejo de transacciones
  ```

- [ ] 2.3.2 Crear `AccountRepository`
  ```python
  # Hereda de Repository[Account]
  # Métodos adicionales:
  # - get_by_name(name) -> Account | None
  # - get_active() -> List[Account]
  # - get_by_type(account_type) -> List[Account]
  # - update_balance(id, amount) -> Account
  ```

- [ ] 2.3.3 Crear `AssetRepository`
  ```python
  # Hereda de Repository[Asset]
  # Métodos adicionales:
  # - get_by_ticker(ticker, asset_type) -> Asset | None
  # - get_by_type(asset_type) -> List[Asset]
  # - get_active() -> List[Asset]
  # - update_current_price(id, price, timestamp) -> Asset
  ```

- [ ] 2.3.4 Crear `OperationRepository`
  ```python
  # Hereda de Repository[Operation]
  # Métodos adicionales:
  # - get_by_asset(asset_id) -> List[Operation]
  # - get_by_account(account_id) -> List[Operation]
  # - get_by_date_range(start, end) -> List[Operation]
  # - get_since(date) -> List[Operation]
  ```

- [ ] 2.3.5 Crear `PriceRepository`
  ```python
  # Hereda de Repository[Price]
  # Métodos adicionales:
  # - get_latest(asset_id) -> Price | None
  # - get_by_date(asset_id, date) -> Price | None
  # - get_history(asset_id, start, end) -> List[Price]
  # - bulk_create(prices) -> List[Price]
  ```

- [ ] 2.3.6 Crear `DatabaseService` para gestión de conexión
  ```python
  # Métodos:
  # - init_db() - crear tablas
  # - drop_db() - limpiar BD
  # - get_session() - context manager
  # - health_check() - verificar conexión
  # - backup() - backup de BD
  ```

**Criterios de aceptación**:
- ✅ Repositories funcionan sin errores SQL
- ✅ Transacciones se hacen/deshacen correctamente
- ✅ Métodos retornan tipos correctos
- ✅ Lazy loading y eager loading funcionan
- ✅ Unit tests de cada Repository pasan

---

### TAREA 2.4: Crear servicios de negocio
**Objetivo**: Implementar lógica de negocio agnóstica de infraestructura.

**Subtareas**:
- [ ] 2.4.1 Crear `CalculationService` para cálculos de patrimonio
  ```python
  # Métodos:
  # - calculate_asset_value(asset_id, quantity, current_price) -> Decimal
  #   Calcula valor total = quantity * current_price
  
  # - calculate_portfolio_value(account_id) -> Decimal
  #   Suma valor actual de todos los activos en cuenta
  
  # - calculate_total_wealth() -> Decimal
  #   Suma de todas las cuentas y activos
  
  # - calculate_cost_basis(asset_id) -> Decimal
  #   Precio promedio ponderado de compra
  
  # - calculate_realized_return(asset_id) -> Dict[str, Decimal]
  #   Ganancias/pérdidas realizadas en ventas
  #   Retorna: {total, percentage, trades_count}
  
  # - calculate_unrealized_return(asset_id, current_price) -> Dict[str, Decimal]
  #   Ganancias/pérdidas potenciales
  #   Retorna: {total, percentage, quantity_held}
  
  # - calculate_total_return(asset_id) -> Dict[str, Decimal]
  #   Retorna realizadas + no realizadas
  
  # - calculate_portfolio_composition() -> List[Dict]
  #   [{asset: ..., value: ..., percentage: ...}, ...]
  
  # - calculate_weighted_average_price(asset_id) -> Decimal
  ```

- [ ] 2.4.2 Crear `OperationService` para gestión de operaciones
  ```python
  # Métodos:
  # - create_buy_operation(asset_id, account_id, quantity, price, ...) -> Operation
  #   Valida cantidad, precio, actualiza saldo
  
  # - create_sell_operation(asset_id, account_id, quantity, price, ...) -> Operation
  #   Valida que exista cantidad disponible
  
  # - update_operation(id, data) -> Operation
  #   Solo si no está finalizada, permite cambiar fecha/precio
  
  # - cancel_operation(id) -> bool
  #   Revierte transacción
  
  # - get_holdings(asset_id) -> Dict
  #   {quantity, average_price, total_invested, current_value, gain}
  
  # - validate_operation(operation) -> Tuple[bool, str]
  #   Validaciones de negocio
  ```

- [ ] 2.4.3 Crear `AccountService` para gestión de cuentas
  ```python
  # Métodos:
  # - create_account(data) -> Account
  # - update_account(id, data) -> Account
  # - delete_account(id) -> bool (validar que esté vacía)
  # - transfer_funds(from_id, to_id, amount) -> bool
  #   Crea dos operaciones internas
  # - close_account(id) -> bool (soft delete)
  # - get_account_summary(id) -> Dict
  #   Saldo, valor de activos, total
  ```

- [ ] 2.4.4 Crear `AssetService` para gestión de activos
  ```python
  # Métodos:
  # - create_asset(data) -> Asset
  # - update_asset(id, data) -> Asset
  # - get_asset_details(id) -> Dict
  #   Incluye precio, rentabilidad, cantidad tenida
  # - get_all_assets_snapshot() -> List[Dict]
  #   Todos los activos con datos actuales
  # - search_assets(query) -> List[Asset]
  # - deprecate_asset(id) -> Asset
  ```

**Criterios de aceptación**:
- ✅ Métodos retornan valores correctos
- ✅ Validaciones son correctas
- ✅ Cálculos financieros son precisos
- ✅ Manejo de excepciones explícito
- ✅ Unit tests cubren casos normales y edge cases
- ✅ Documentación con ejemplos en cada método

---

### TAREA 2.5: Implementar rutas API principales
**Objetivo**: Crear endpoints REST para todas las operaciones CRUD.

**Subtareas**:
- [ ] 2.5.1 Crear rutas de `Accounts`
  ```python
  # GET /api/v1/accounts
  #   Query params: skip=0, limit=10, active=true
  #   Retorna: List[AccountRead]
  
  # GET /api/v1/accounts/{id}
  #   Retorna: AccountReadWithOperations
  
  # POST /api/v1/accounts
  #   Body: AccountCreate
  #   Retorna: AccountRead, status 201
  
  # PUT /api/v1/accounts/{id}
  #   Body: AccountUpdate
  #   Retorna: AccountRead
  
  # DELETE /api/v1/accounts/{id}
  #   Retorna: status 204, 400 si tiene operaciones
  
  # GET /api/v1/accounts/{id}/balance
  #   Retorna: {balance: Decimal, as_of: datetime}
  
  # GET /api/v1/accounts/{id}/summary
  #   Retorna: {balance, assets_value, total, currencies: {...}}
  ```

- [ ] 2.5.2 Crear rutas de `Assets`
  ```python
  # GET /api/v1/assets
  #   Query params: skip=0, limit=50, type=all, active=true
  #   Retorna: List[AssetRead]
  
  # GET /api/v1/assets/{id}
  #   Retorna: AssetReadWithOperations
  
  # POST /api/v1/assets
  #   Body: AssetCreate
  #   Retorna: AssetRead, status 201
  
  # PUT /api/v1/assets/{id}
  #   Body: AssetUpdate
  #   Retorna: AssetRead
  
  # DELETE /api/v1/assets/{id}
  #   Retorna: status 204, 400 si tiene operaciones
  
  # GET /api/v1/assets/{id}/holdings
  #   Retorna: {quantity, average_price, total_invested, current_value, gain}
  
  # GET /api/v1/assets/ticker/{ticker}
  #   Retorna: AssetRead (búsqueda por ticker)
  ```

- [ ] 2.5.3 Crear rutas de `Operations`
  ```python
  # GET /api/v1/operations
  #   Query params: skip=0, limit=100, asset_id, account_id, type, start_date, end_date
  #   Retorna: List[OperationReadFull]
  
  # GET /api/v1/operations/{id}
  #   Retorna: OperationReadFull
  
  # POST /api/v1/operations
  #   Body: OperationCreate (incluye type: Buy/Sell)
  #   Retorna: OperationRead, status 201
  #   Valida cantidad, precio, disponibilidad
  
  # PUT /api/v1/operations/{id}
  #   Body: OperationUpdate
  #   Retorna: OperationRead
  #   Solo permite editar si es reciente (< 7 días)
  
  # DELETE /api/v1/operations/{id}
  #   Retorna: status 204
  #   Revierte la operación
  
  # GET /api/v1/operations/asset/{asset_id}
  #   Retorna: List[OperationReadFull] del activo
  
  # GET /api/v1/operations/account/{account_id}
  #   Retorna: List[OperationReadFull] de la cuenta
  ```

- [ ] 2.5.4 Crear rutas de `Prices` (manual + automática)
  ```python
  # GET /api/v1/prices/asset/{asset_id}
  #   Query params: skip=0, limit=100
  #   Retorna: List[PriceRead] histórico
  
  # GET /api/v1/prices/asset/{asset_id}/latest
  #   Retorna: PriceRead más reciente
  
  # POST /api/v1/prices
  #   Body: PriceCreate (manual)
  #   Retorna: PriceRead, status 201
  
  # GET /api/v1/prices/asset/{asset_id}/current
  #   Intenta obtener de cache/yfinance
  #   Si falla, retorna última conocida o error
  #   Retorna: {price, source, timestamp}
  
  # POST /api/v1/prices/refresh/{asset_id}
  #   Fuerza actualización de precio desde yfinance
  #   Retorna: {old_price, new_price, timestamp}
  
  # POST /api/v1/prices/refresh-all
  #   Actualiza todos los activos activos
  #   Retorna: {updated_count, failed_count, details: [...]}
  ```

- [ ] 2.5.5 Añadir validación y manejo de errores
  ```python
  # HTTPException para errores comunes:
  # - 400 Bad Request (validación)
  # - 404 Not Found (recurso no existe)
  # - 409 Conflict (operación inválida)
  # - 422 Unprocessable Entity (error de negocio)
  # - 500 Internal Server Error
  
  # Custom exception handlers:
  # - ValidationError -> 422
  # - NotFoundError -> 404
  # - BusinessLogicError -> 409
  ```

- [ ] 2.5.6 Añadir documentación OpenAPI
  ```python
  # Descripción en cada ruta (docstring)
  # Ejemplos de request/response
  # Códigos de estado posibles
  # Parámetros de query explicados
  ```

**Criterios de aceptación**:
- ✅ Todas las rutas respondenv con status correcto
- ✅ Validaciones funcionan (request inválido -> 422)
- ✅ Documentación visible en /docs
- ✅ Ejemplos curl funcionales
- ✅ Errores tienen mensaje informativos

---

### TAREA 2.6: Crear servicio de caché y optimización
**Objetivo**: Implementar caché de precios para optimizar rendimiento.

**Subtareas**:
- [ ] 2.6.1 Crear `CacheService` usando Redis en memoria (o archivo)
  ```python
  # Métodos:
  # - get(key) -> T | None
  # - set(key, value, ttl) -> bool
  # - delete(key) -> bool
  # - clear() -> bool
  # - exists(key) -> bool
  # - ttl(key) -> int (segundos restantes)
  
  # Usar: Redis local o cachetools.TTLCache para simplificar
  ```

- [ ] 2.6.2 Crear `PriceCacheService` especializado
  ```python
  # Métodos:
  # - get_cached_price(asset_id) -> Tuple[Decimal, datetime] | None
  # - set_cached_price(asset_id, price, ttl=3600)
  # - invalidate_cache(asset_id)
  # - get_cache_stats() -> {hits, misses, size}
  # - cleanup_expired()
  
  # Almacenar: asset_id -> (price, timestamp, expires_at)
  ```

- [ ] 2.6.3 Integrar caché en precio service
  ```python
  # Al obtener precio:
  # 1. Consultar caché
  # 2. Si válido, retornar
  # 3. Si expirado o no existe, llamar a yfinance
  # 4. Guardar en caché y BD
  # 5. Retornar
  ```

- [ ] 2.6.4 Crear configuración de TTL por tipo de activo
  ```python
  # Stocks: 15 minutos
  # ETFs: 30 minutos
  # Cryptos: 5 minutos
  # Otros: 1 hora
  ```

**Criterios de aceptación**:
- ✅ Caché funciona sin errores
- ✅ TTL se respeta
- ✅ Fallback a BD si falla caché
- ✅ Stats de caché están disponibles
- ✅ Performance mejorada (medible)

---

### TAREA 2.7: Crear manejo de transacciones y rollback
**Objetivo**: Garantizar integridad de datos en operaciones complejas.

**Subtareas**:
- [ ] 2.7.1 Crear decorador `@transactional`
  ```python
  # Si excepción: rollback automático
  # Si éxito: commit automático
  # Logging de transacciones
  ```

- [ ] 2.7.2 Implementar compensating transactions para reversal
  ```python
  # Si cancel_operation(buy_operation):
  #   - Crear sell_operation con datos inversos
  #   - Actualizar saldo de cuenta
  #   - Marcar original como cancelada
  ```

- [ ] 2.7.3 Crear auditoría básica
  ```python
  # Log de cambios:
  # - Qué cambió
  # - Cuándo
  # - Qué valores (antes/después)
  # - Usuario (para fase 2)
  # Tabla: AuditLog
  ```

**Criterios de aceptación**:
- ✅ Operaciones fallidas no dejan datos inconsistentes
- ✅ Rollback funciona correctamente
- ✅ Auditoría registra cambios

---

## FASE 3: INTEGRACIÓN DE DATOS (2 días)

### TAREA 3.1: Integración con yfinance
**Objetivo**: Obtener precios de acciones, ETFs y criptos automáticamente.

**Subtareas**:
- [ ] 3.1.1 Crear `PriceProviderService` base abstracto
  ```python
  # Interface:
  # - get_price(ticker) -> Decimal
  # - get_prices(tickers) -> Dict[str, Decimal]
  # - validate_ticker(ticker) -> bool
  # - get_info(ticker) -> Dict
  ```

- [ ] 3.1.2 Implementar `YFinancePriceProvider`
  ```python
  # Métodos:
  # - fetch_price(ticker) -> Decimal
  #   Maneja errores, timeouts, tickers inválidos
  # - fetch_multiple(tickers) -> Dict[str, Decimal]
  #   Batch request más eficiente
  # - fetch_info(ticker) -> Dict
  #   {name, currency, sector, industry, marketCap}
  # - validate_ticker(ticker) -> bool
  #   Intenta obtener info, retorna verdadero si existe
  ```

- [ ] 3.1.3 Crear `PriceService` como orquestador
  ```python
  # Métodos:
  # - get_current_price(asset_id) -> Decimal
  #   Con fallback: caché -> provider -> última BD
  # - refresh_asset_price(asset_id) -> Tuple[Decimal, str]
  #   Obtiene precio fresco, guarda en caché y BD
  # - refresh_all_prices() -> Dict[str, Tuple[bool, Decimal | str]]
  #   Todos los activos activos en background
  # - get_price_history(asset_id, start, end) -> List[Price]
  ```

- [ ] 3.1.4 Crear manejo de errores y fallbacks
  ```python
  # Si yfinance falla:
  # - Retornar última conocida
  # - Log de error
  # - Marcar como "stale"
  # - Reintentar después
  
  # Si ticker no existe:
  # - Retornar None
  # - Sugerir búsqueda
  # - Permitir precio manual
  ```

- [ ] 3.1.5 Crear utilidad de búsqueda de tickers
  ```python
  # Método: search_ticker(query: str) -> List[Dict]
  # Retorna opciones similares usando yfinance
  # Útil para UI (autocomplete)
  ```

**Criterios de aceptación**:
- ✅ Obtiene precio de acciones reales
- ✅ Obtiene precio de ETFs
- ✅ Maneja tickers inválidos gracefully
- ✅ Caché funciona correctamente
- ✅ Fallback a última conocida si error

---

### TAREA 3.2: Crear background tasks para actualización periódica
**Objetivo**: Actualizar precios automáticamente sin bloquear API.

**Subtareas**:
- [ ] 3.2.1 Configurar APScheduler
  ```python
  # Instalación: pip install apscheduler
  # Configuración en app startup
  ```

- [ ] 3.2.2 Crear job de actualización de precios
  ```python
  # Función: update_all_prices_job()
  # Ejecuta: diariamente a las 18:00 (después cierre)
  # Para cada activo activo:
  #   - fetch precio
  #   - guardar en BD
  #   - actualizar caché
  # Log de resultados
  ```

- [ ] 3.2.3 Crear job de limpieza de caché expirado
  ```python
  # Función: cleanup_expired_cache_job()
  # Ejecuta: cada 1 hora
  # Elimina entradas expiradas de caché
  ```

- [ ] 3.2.4 Crear endpoint para disparar actualizaciones manuales
  ```python
  # POST /api/v1/admin/refresh-prices (async)
  # Retorna: task_id para polling
  
  # GET /api/v1/admin/refresh-prices/{task_id}
  # Retorna: estado, progreso, resultados
  ```

- [ ] 3.2.5 Crear logging y alertas
  ```python
  # Log cada job:
  # - Inicio/fin
  # - Cantidad procesada
  # - Errores
  # - Tiempo transcurrido
  ```

**Criterios de aceptación**:
- ✅ Jobs se ejecutan automáticamente
- ✅ Precios se actualizan correctamente
- ✅ Logs registran actividad
- ✅ Errores no detienen otros assets

---

### TAREA 3.3: Crear importador de datos (CSV)
**Objetivo**: Permitir cargar operaciones históricase desde archivo.

**Subtareas**:
- [ ] 3.3.1 Diseñar formato CSV
  ```csv
  date,operation_type,account,asset_ticker,quantity,unit_price,commission,notes
  2024-01-15,Buy,Cuenta 1,AAPL,10,150.50,9.99,"Compra inicial"
  2024-02-20,Buy,Cuenta 1,VTI,5,200.00,0,"ETF"
  2024-03-10,Sell,Cuenta 1,AAPL,5,160.00,9.99,"Venta parcial"
  ```

- [ ] 3.3.2 Crear parser de CSV
  ```python
  # Método: parse_csv(file) -> List[Dict]
  # Validar encabezados
  # Validar tipos de datos
  # Retornar lista de operaciones parseadas
  ```

- [ ] 3.3.3 Crear importador con validación
  ```python
  # Método: import_operations(data: List[Dict]) -> Dict
  # Para cada operación:
  #   - Validar fecha, ticker, cantidades
  #   - Obtener/crear asset
  #   - Obtener/crear account
  #   - Crear operación
  # Retorna: {success: N, errors: []}
  # Transacción: all or nothing
  ```

- [ ] 3.3.4 Crear endpoint de importación
  ```python
  # POST /api/v1/operations/import
  # multipart/form-data: file
  # Retorna: {imported: N, errors: [...]}
  ```

- [ ] 3.3.5 Crear validaciones específicas
  ```python
  # - Fechas no futuras
  # - Cantidades > 0
  # - Precios > 0
  # - Cuentas/assets existen o se crean
  # - Orden cronológico
  ```

**Criterios de aceptación**:
- ✅ CSV se parsea correctamente
- ✅ Validaciones detectan errores
- ✅ Errores son informativos
- ✅ Transacción se revierte si hay fallos
- ✅ Endpoint funciona

---

## FASE 4: FRONTEND BÁSICO (3 días)

### TAREA 4.1: Crear estructura HTML base y layout
**Objetivo**: Template base con navegación y estructura responsive.

**Subtareas**:
- [ ] 4.1.1 Crear `templates/base.html`
  ```html
  <!DOCTYPE html>
  <html lang="es">
  <head>
    - Meta tags (viewport, charset, description)
    - CSS principal (style.css)
    - Font (Google Fonts)
    - Bootstrap o similar
  </head>
  <body>
    {% include 'components/navbar.html' %}
    {% include 'components/sidebar.html' %}
    <main class="main-content">
      {% block content %}{% endblock %}
    </main>
    - Scripts al final
  </body>
  </html>
  ```

- [ ] 4.1.2 Crear `templates/components/navbar.html`
  ```html
  - Logo/marca
  - Enlaces principales: Dashboard, Cuentas, Activos, Operaciones, Reportes
  - Usuario/menú dropdown (fase 2)
  - Búsqueda (fase 2)
  ```

- [ ] 4.1.3 Crear `templates/components/sidebar.html` (opcional)
  ```html
  - Menú colapsible en móvil
  - Enlaces de navegación
  - Resumen rápido de patrimonio
  ```

- [ ] 4.1.4 Crear `static/css/style.css` base
  ```css
  - Variables CSS (colores, espacios, fuentes)
  - Reset y base styles
  - Responsive grid
  - Utilidades (margin, padding, etc)
  - Dark mode (opcional)
  ```

- [ ] 4.1.5 Crear `static/css/dashboard.css`
  ```css
  - Estilos específicos para dashboard
  - Cards de resumen
  - Gráficos
  - Tablas
  ```

**Criterios de aceptación**:
- ✅ Base.html renderiza sin errores
- ✅ CSS carga correctamente
- ✅ Responsive en móvil y desktop
- ✅ Navegación funcional

---

### TAREA 4.2: Crear páginas principales
**Objetivo**: Implementar vistas de todas las secciones principales.

**Subtareas**:
- [ ] 4.2.1 Crear `templates/index.html` (landing)
  ```html
  - Welcome message
  - CTA para crear cuenta
  - Features overview
  - Link a dashboard si tiene datos
  ```

- [ ] 4.2.2 Crear `templates/dashboard.html` (resumen principal)
  ```html
  - Cards de KPI:
    * Patrimonio total
    * Rentabilidad total
    * Cambio del día
    * Composición por tipo
  - Gráfico pie: composición de activos
  - Tabla: últimas operaciones
  - Top gainers/losers
  ```

- [ ] 4.2.3 Crear `templates/accounts.html`
  ```html
  - Tabla de cuentas con columnas:
    * Nombre, banco, tipo, saldo, moneda, acciones
  - Botón "Nueva Cuenta"
  - Búsqueda y filtrado
  - Link a detalle de cuenta
  ```

- [ ] 4.2.4 Crear `templates/assets.html`
  ```html
  - Tabla de activos con columnas:
    * Ticker, nombre, tipo, precio, cambio%, acciones
  - Filtro por tipo
  - Búsqueda por nombre/ticker
  - Botón "Nuevo Activo"
  - Botón "Actualizar Precios"
  ```

- [ ] 4.2.5 Crear `templates/operations.html`
  ```html
  - Tabla de operaciones con columnas:
    * Fecha, tipo, activo, cantidad, precio, total, comisión
  - Filtro por fecha, tipo, activo, cuenta
  - Búsqueda
  - Botón "Nueva Operación"
  - Botón "Importar CSV"
  - Acción: editar/eliminar
  ```

- [ ] 4.2.6 Crear `templates/reports.html`
  ```html
  - Tabs: Resumen, Rentabilidad, Composición, Histórico
  - Gráficos principales
  - Exportar a CSV/PDF (fase 2)
  ```

**Criterios de aceptación**:
- ✅ Todas las páginas cargan sin errores
- ✅ Navegación entre páginas funciona
- ✅ Responsive en móvil

---

### TAREA 4.3: Crear componentes de formularios
**Objetivo**: Formularios reutilizables para CRUD operations.

**Subtareas**:
- [ ] 4.3.1 Crear `templates/components/form_account.html`
  ```html
  - Campo: name
  - Campo: account_type (select)
  - Campo: bank (text)
  - Campo: iban (text, opcional)
  - Campo: currency (select EUR/USD/GBP)
  - Campo: current_balance (number)
  - Botones: Submit, Cancel
  - Modo: create/edit
  - Validación frontend
  ```

- [ ] 4.3.2 Crear `templates/components/form_asset.html`
  ```html
  - Campo: ticker (text, con búsqueda)
  - Campo: name (text)
  - Campo: asset_type (select)
  - Campo: currency (select)
  - Campo: manual_price (checkbox)
  - Campo: current_price (number, si manual)
  - Botones: Submit, Cancel
  ```

- [ ] 4.3.3 Crear `templates/components/form_operation.html`
  ```html
  - Campo: operation_date (date picker)
  - Campo: asset_id (select con search)
  - Campo: account_id (select)
  - Campo: operation_type (Buy/Sell radio)
  - Campo: quantity (decimal)
  - Campo: unit_price (decimal)
  - Campo: commission (decimal, default 0)
  - Campo: notes (textarea, opcional)
  - Calculated: total_amount (readonly)
  - Botones: Submit, Cancel
  ```

- [ ] 4.3.4 Crear `templates/components/modals.html`
  ```html
  - Modal de confirmación de eliminación
  - Modal de error/éxito
  - Modal de carga (loading)
  ```

**Criterios de aceptación**:
- ✅ Formularios renderean correctamente
- ✅ Validación frontend funciona
- ✅ Submit envia datos al API correcto

---

### TAREA 4.4: Crear cliente API en JavaScript
**Objetivo**: Funciones para comunicar frontend con backend.

**Subtareas**:
- [ ] 4.4.1 Crear `static/js/api.js`
  ```javascript
  // Base URL y configuración
  const API_BASE = '/api/v1';
  const DEFAULT_HEADERS = {
    'Content-Type': 'application/json'
  };
  
  // Helper genérico
  async function apiCall(method, endpoint, data = null) {
    // Manejo de errores
    // Retry logic
    // Timeout
  }
  
  // Métodos específicos:
  // accounts.getAll(), getOne(id), create(data), update(id, data), delete(id)
  // assets.getAll(), getOne(id), create(data), update(id, data), delete(id)
  // operations.getAll(), getOne(id), create(data), update(id, data), delete(id)
  // prices.getCurrent(assetId), refreshAll()
  // reports.getSummary(), getComposition(), getReturns()
  ```

- [ ] 4.4.2 Crear `static/js/app.js`
  ```javascript
  // Funciones de UI:
  // showLoading(), hideLoading()
  // showNotification(message, type)
  // showError(error)
  // showSuccess(message)
  
  // Gestión de tablas:
  // loadTable(endpoint, columns, filters)
  // renderTable(data, columns)
  // setupTablePagination()
  
  // Gestión de formularios:
  // loadForm(formElement, endpoint, id)
  // submitForm(formElement, endpoint)
  // resetForm(formElement)
  
  // Event listeners:
  // DOMContentLoaded
  // Botones de acción
  // Cambios en filtros
  ```

- [ ] 4.4.3 Crear `static/js/charts.js`
  ```javascript
  // Usar Chart.js para gráficos
  // pieChart(data, elementId) - composición
  // lineChart(data, elementId) - histórico de patrimonio
  // barChart(data, elementId) - rentabilidad por activo
  // updateCharts(data) - actualizar gráficos
  ```

**Criterios de aceptación**:
- ✅ API calls funcionan
- ✅ Errores se muestran en UI
- ✅ Loading indicators funcionan
- ✅ Gráficos se renderizan

---

### TAREA 4.5: Crear flujo de crear/editar recursos
**Objetivo**: Implementar UX completa para CRUD operations.

**Subtareas**:
- [ ] 4.5.1 Para Accounts
  - [ ] Botón "Nueva Cuenta" -> Modal con form
  - [ ] Click en fila -> Página de detalle/edición
  - [ ] Botón editar -> Modal con form prellenado
  - [ ] Botón eliminar -> Confirmación -> Ejecutar

- [ ] 4.5.2 Para Assets
  - [ ] Botón "Nuevo Activo" -> Modal con form
  - [ ] Auto-complete en ticker field
  - [ ] Click en fila -> Detalle del activo
  - [ ] Mostrar precio actual, rentabilidad
  - [ ] Botón "Actualizar Precio" -> Refresh manual

- [ ] 4.5.3 Para Operations
  - [ ] Botón "Nueva Operación" -> Modal/página
  - [ ] Seleccionar activo -> Cargar datos
  - [ ] Seleccionar cuenta -> Validar saldo
  - [ ] Calcular automáticamente total
  - [ ] Botón "Importar CSV" -> Upload
  - [ ] Click operación -> Detalle/edición
  - [ ] Botón eliminar -> Confirmación

**Criterios de aceptación**:
- ✅ Crear recurso funciona end-to-end
- ✅ Editar recurso funciona
- ✅ Eliminar solicita confirmación
- ✅ Errores se muestran claramente
- ✅ Página se actualiza post-operación

---

## FASE 5: REPORTES Y ANALYTICS (2 días)

### TAREA 5.1: Crear endpoints de reportes
**Objetivo**: APIs para datos agregados y análisis.

**Subtareas**:
- [ ] 5.1.1 Crear `routes/reports.py`
  ```python
  # GET /api/v1/reports/summary
  # Retorna:
  # {
  #   total_wealth: Decimal,
  #   total_invested: Decimal,
  #   total_gain: Decimal,
  #   total_gain_percentage: Decimal,
  #   portfolio_value: Decimal,
  #   cash: Decimal,
  #   by_currency: {EUR: {value, invested, gain}, ...},
  #   last_updated: datetime
  # }
  ```

- [ ] 5.1.2 Crear endpoint composición
  ```python
  # GET /api/v1/reports/composition
  # Retorna:
  # {
  #   by_type: [
  #     {type: "Stock", value: ..., percentage: ...},
  #     {type: "ETF", value: ..., percentage: ...},
  #     ...
  #   ],
  #   by_account: [
  #     {account: "name", value: ..., percentage: ...},
  #     ...
  #   ]
  # }
  ```

- [ ] 5.1.3 Crear endpoint rentabilidad
  ```python
  # GET /api/v1/reports/returns
  # Query: period=all|year|quarter|month
  # Retorna:
  # [
  #   {
  #     asset: {id, ticker, name},
  #     quantity: Decimal,
  #     cost_basis: Decimal,
  #     current_value: Decimal,
  #     unrealized_gain: Decimal,
  #     realized_gain: Decimal,
  #     total_gain: Decimal,
  #     return_percentage: Decimal
  #   },
  #   ...
  # ]
  ```

- [ ] 5.1.4 Crear endpoint histórico
  ```python
  # GET /api/v1/reports/history
  # Query: start_date, end_date, granularity=daily|weekly|monthly
  # Retorna:
  # [
  #   {
  #     date: datetime,
  #     total_value: Decimal,
  #     change: Decimal,
  #     change_percentage: Decimal
  #   },
  #   ...
  # ]
  ```

- [ ] 5.1.5 Crear endpoint de proyecciones (opcional)
  ```python
  # GET /api/v1/reports/projections
  # Query: months=12, growth_rate=0.07
  # Retorna: tabla de proyección
  ```

**Criterios de aceptación**:
- ✅ Todos los endpoints retornan datos válidos
- ✅ Cálculos son correctos
- ✅ Datos se cachean si es costoso
- ✅ Performance aceptable

---

### TAREA 5.2: Crear vistas de dashboard y reportes
**Objetivo**: Interfaces visuales para análisis.

**Subtareas**:
- [ ] 5.2.1 Mejorar dashboard principal
  ```html
  - Card 1: Patrimonio total (grande)
  - Card 2: Rentabilidad total
  - Card 3: Cambio del día
  - Card 4: Composición por tipo
  
  - Sección de gráficos:
    * Pie chart: composición por tipo
    * Line chart: evolución patrimonio (último año)
    * Bar chart: top 5 activos por valor
  
  - Tabla: últimas 10 operaciones
  - Card: próximos hitos (si es posible)
  ```

- [ ] 5.2.2 Crear página "Mis Activos" (análisis detallado)
  ```html
  - Tabla expandible con:
    * Ticker, Nombre, Tipo
    * Cantidad, Precio actual, Valor total
    * Costo promedio, Ganancia realizda, Ganancia no realizada
    * Rentabilidad %
  - Sumas totales por columna
  - Exportar a CSV
  ```

- [ ] 5.2.3 Crear página "Análisis de Rentabilidad"
  ```html
  - Tabla de top gainers/losers
  - Filtro por período (3m, 6m, 1y, all)
  - Gráfico: distribución de ganancias/pérdidas
  - Estadísticas: media, mediana, máx, mín, std dev
  ```

- [ ] 5.2.4 Crear página "Histórico de Patrimonio"
  ```html
  - Gráfico lineal: evolución total patrimonio
  - Selector de rango de fechas
  - Selector de granularidad (daily, weekly, monthly)
  - Tabla con valores puntuales
  - Estadísticas: máximo, mínimo, media, volatilidad
  ```

- [ ] 5.2.5 Crear página "Composición"
  ```html
  - Pie chart: por tipo de activo
  - Pie chart: por cuenta
  - Pie chart: por moneda
  - Tablas con números
  - Comparar con benchmark (opcional)
  ```

**Criterios de aceptación**:
- ✅ Todas las páginas cargan sin errores
- ✅ Gráficos se renderizan correctamente
- ✅ Datos son consistentes con API
- ✅ Responsive design

---

## FASE 6: TESTING Y QA (2 días)

### TAREA 6.1: Tests unitarios de modelos y servicios
**Objetivo**: Cobertura completa de lógica de negocio.

**Subtareas**:
- [ ] 6.1.1 Crear `tests/test_models.py`
  ```python
  # Tests para cada modelo:
  # - Creación con datos válidos
  # - Validación de constraints
  # - Relaciones entre modelos
  # - Métodos del modelo
  
  # Por modelo: ~10-15 tests
  ```

- [ ] 6.1.2 Crear `tests/test_repositories.py`
  ```python
  # Tests para cada Repository:
  # - get(), get_all(), create(), update(), delete()
  # - filter_by(), métodos customizados
  # - Transacciones y rollback
  # - Manejo de excepciones
  
  # Por repository: ~15-20 tests
  ```

- [ ] 6.1.3 Crear `tests/test_services.py`
  ```python
  # Tests para cada Service:
  # - CalculationService: cálculos correctos, edge cases
  # - OperationService: compra/venta, validaciones
  # - AccountService: creación, transferencias
  # - AssetService: gestión de activos
  # - PriceService: obtención de precios, caché
  
  # Por servicio: ~20-30 tests
  ```

- [ ] 6.1.4 Crear fixtures en `tests/conftest.py`
  ```python
  # Fixtures compartidas:
  # - test_db: sesión de BD para tests
  # - sample_accounts: cuentas de prueba
  # - sample_assets: activos de prueba
  # - sample_operations: operaciones de prueba
  ```

- [ ] 6.1.5 Ejecutar tests y medir cobertura
  ```bash
  pytest tests/ -v --cov=app --cov-report=html
  # Target: >= 80% cobertura
  ```

**Criterios de aceptación**:
- ✅ >= 80% cobertura de código
- ✅ Todos los tests pasan
- ✅ Ejecución < 30 segundos
- ✅ Tests son determinísticos

---

### TAREA 6.2: Tests de integración (API)
**Objetivo**: Verificar endpoints funcionan end-to-end.

**Subtareas**:
- [ ] 6.2.1 Crear `tests/test_routes_accounts.py`
  ```python
  # GET /accounts - listar
  # POST /accounts - crear
  # GET /accounts/{id} - detalle
  # PUT /accounts/{id} - editar
  # DELETE /accounts/{id} - eliminar
  # GET /accounts/{id}/summary - resumen
  
  # 2-3 tests por endpoint
  ```

- [ ] 6.2.2 Crear `tests/test_routes_assets.py`
  ```python
  # GET /assets - listar
  # POST /assets - crear
  # GET /assets/{id} - detalle
  # PUT /assets/{id} - editar
  # DELETE /assets/{id} - eliminar
  # GET /assets/{id}/holdings - posición actual
  ```

- [ ] 6.2.3 Crear `tests/test_routes_operations.py`
  ```python
  # GET /operations - listar con filtros
  # POST /operations - crear (compra/venta)
  # GET /operations/{id} - detalle
  # PUT /operations/{id} - editar
  # DELETE /operations/{id} - eliminar (con rollback)
  # Importar CSV
  ```

- [ ] 6.2.4 Crear `tests/test_routes_prices.py`
  ```python
  # GET /prices/asset/{id} - histórico
  # GET /prices/asset/{id}/latest - última
  # GET /prices/asset/{id}/current - actual
  # POST /prices - crear manual
  # POST /prices/refresh/{id} - actualizar
  # POST /prices/refresh-all - actualizar todas
  ```

- [ ] 6.2.5 Crear `tests/test_routes_reports.py`
  ```python
  # GET /reports/summary - resumen
  # GET /reports/composition - composición
  # GET /reports/returns - rentabilidad
  # GET /reports/history - histórico
  ```

**Criterios de aceptación**:
- ✅ Todos los tests pasan
- ✅ Status codes correctos
- ✅ Schemas de respuesta válidos
- ✅ Validaciones funcionan

---

### TAREA 6.3: Tests de frontend
**Objetivo**: Verificar interfaz funciona correctamente.

**Subtareas**:
- [ ] 6.3.1 Tests funcionales básicos
  ```javascript
  // Usando Cypress o Selenium
  // Test cada página carga sin errores
  // Test navegación entre páginas
  // Test crear cuenta
  // Test crear activo
  // Test crear operación
  ```

- [ ] 6.3.2 Tests de formularios
  ```javascript
  // Validación frontend funciona
  // Submit envia datos correctos
  // Error messages aparecen
  // Success messages aparecen
  ```

- [ ] 6.3.3 Tests de tablas y filtros
  ```javascript
  // Tabla se carga con datos
  // Filtros funcionan
  // Búsqueda funciona
  // Paginación funciona
  ```

**Criterios de aceptación**:
- ✅ Principales flujos funcionan
- ✅ Errores se muestran
- ✅ UI es responsive

---

### TAREA 6.4: Testing manual y QA
**Objetivo**: Verificación final antes de producción.

**Subtareas**:
- [ ] 6.4.1 Crear checklist de QA
  ```markdown
  ## Funcionalidad
  - [ ] Crear cuenta corriente
  - [ ] Crear activo (acciones)
  - [ ] Crear activo (ETF)
  - [ ] Comprar activo
  - [ ] Vender activo (cantidad total)
  - [ ] Vender activo (cantidad parcial)
  - [ ] Operación con comisión
  - [ ] Ver Dashboard
  - [ ] Ver reportes
  - [ ] Filtrar operaciones
  - [ ] Importar CSV
  
  ## Performance
  - [ ] Dashboard carga < 2s
  - [ ] Tablas de 1000 filas responden < 1s
  - [ ] Actualizar precios < 30s
  
  ## Seguridad
  - [ ] No hay SQLi posible
  - [ ] XSS está prevenido
  - [ ] CSRF está protegido
  
  ## Responsividad
  - [ ] Looks ok en 320px (móvil)
  - [ ] Looks ok en 768px (tablet)
  - [ ] Looks ok en 1920px (desktop)
  ```

- [ ] 6.4.2 Ejecutar checklist manualmente
- [ ] 6.4.3 Crear bug reports si es necesario
- [ ] 6.4.4 Verificar edge cases
  ```
  - Operación con precio 0
  - Vender más de lo que tienes
  - Crear cuenta con nombre duplicado
  - Editar operación del pasado
  - Eliminar activo con operaciones activas
  ```

**Criterios de aceptación**:
- ✅ Checklist completo sin críticos abiertos
- ✅ Performance aceptable
- ✅ Seguridad verificada

---

## FASE 7: DEVOPS Y DEPLOY (2 días)

### TAREA 7.1: Preparar aplicación para producción
**Objetivo**: Optimizaciones y configuración production-ready.

**Subtareas**:
- [ ] 7.1.1 Crear archivo `.env.prod`
  ```
  DATABASE_URL=postgresql://user:password@db:5432/patrimonio
  API_HOST=0.0.0.0
  API_PORT=8000
  API_DEBUG=False
  API_LOG_LEVEL=WARNING
  
  WORKERS=4
  WORKER_CLASS=uvicorn.workers.UvicornWorker
  
  PRICE_CACHE_TTL=3600
  YFINANCE_TIMEOUT=10
  
  CORS_ORIGINS=https://yourdomain.com
  ```

- [ ] 7.1.2 Optimizar Docker para producción
  ```dockerfile
  # Agregar a Dockerfile:
  - Non-root user
  - Health check
  - Security headers
  - Logging centralizado
  ```

- [ ] 7.1.3 Crear `docker-compose.prod.yml`
  ```yaml
  # Servicios:
  - app (FastAPI con gunicorn)
  - db (PostgreSQL con persistencia)
  - redis (caché, opcional)
  
  # Configuración:
  - Volumes persistentes para DB
  - Networks aisladas
  - Restart policies
  - Health checks
  ```

- [ ] 7.1.4 Optimizar BD para producción
  ```sql
  -- Crear índices faltantes
  -- Configurar vacuum automático
  -- Backups automáticos
  -- Replicación (opcional)
  ```

- [ ] 7.1.5 Configurar logging centralizado
  ```python
  # Usar structlog o similar
  # Logs a archivo y stdout
  # Rotación de logs
  # Formato JSON para parsing
  ```

**Criterios de aceptación**:
- ✅ App arranca sin errores en prod
- ✅ Base de datos conecta correctamente
- ✅ Logging funciona
- ✅ Health check responde

---

### TAREA 7.2: Crear scripts de deployment
**Objetivo**: Automatizar despliegue en servidor.

**Subtareas**:
- [ ] 7.2.1 Crear `scripts/deploy.sh`
  ```bash
  #!/bin/bash
  # 1. Git pull
  # 2. Backup BD
  # 3. docker-compose down
  # 4. docker-compose build
  # 5. docker-compose up -d
  # 6. Esperar health checks
  # 7. Ejecutar migraciones
  # 8. Precargar precios
  # 9. Log de éxito/error
  ```

- [ ] 7.2.2 Crear `scripts/rollback.sh`
  ```bash
  #!/bin/bash
  # Revertir último deploy
  # Restaurar backup de BD
  # Reiniciar contenedores
  ```

- [ ] 7.2.3 Crear `scripts/backup.sh`
  ```bash
  #!/bin/bash
  # Backup de BD
  # Compresión
  # Upload a storage remoto
  # Limpiar backups antiguos
  ```

- [ ] 7.2.4 Crear `scripts/init-prod.sh`
  ```bash
  #!/bin/bash
  # Primer deploy en servidor nuevo
  # Crear directorios
  # Crear variables de entorno
  # Inicializar BD
  # Cargar datos iniciales
  ```

- [ ] 7.2.5 Crear `Makefile` para comandos comunes
  ```makefile
  .PHONY: help build run stop clean test lint deploy rollback
  
  help:
  	@echo "Available commands"
  
  build:
  	docker-compose build
  
  run:
  	docker-compose up
  
  test:
  	docker-compose exec app pytest
  
  # ... etc
  ```

**Criterios de aceptación**:
- ✅ `make deploy` funciona end-to-end
- ✅ Rollback restaura estado anterior
- ✅ Backup se crea correctamente

---

### TAREA 7.3: Configurar CI/CD avanzado
**Objetivo**: Automatización completa de tests y deploy.

**Subtareas**:
- [ ] 7.3.1 Mejorar `workflows/tests.yml`
  ```yaml
  on: [push, pull_request]
  
  jobs:
    test:
      runs-on: ubuntu-latest
      
      services:
        postgres:
          image: postgres:15
          env:
            POSTGRES_DB: test_patrimonio
          options: >-
            --health-cmd pg_isready
      
      steps:
        - Checkout
        - Setup Python
        - Cache dependencies
        - Install
        - Run linting
        - Run tests con coverage
        - Upload coverage
  ```

- [ ] 7.3.2 Crear `workflows/deploy.yml`
  ```yaml
  on:
    push:
      branches: [main]
  
  jobs:
    deploy:
      runs-on: ubuntu-latest
      needs: test  # Solo si tests pasan
      
      steps:
        - Checkout
        - Setup Docker Buildx
        - Login a registry
        - Build y push imagen
        - Deploy a servidor
        - Health check
        - Rollback si falla
  ```

- [ ] 7.3.3 Crear `workflows/security.yml`
  ```yaml
  on: [push, pull_request]
  
  jobs:
    security:
      runs-on: ubuntu-latest
      
      steps:
        - Bandit (seguridad Python)
        - Trivy (vulnerabilidades en dependencias)
        - OWASP dependency check
  ```

**Criterios de aceptación**:
- ✅ Tests se ejecutan en cada push
- ✅ Deploy es automático en main
- ✅ Rollback funciona si health check falla

---

### TAREA 7.4: Documentación de deployment
**Objetivo**: Guías para desplegar y mantener en producción.

**Subtareas**:
- [ ] 7.4.1 Crear `docs/DEPLOYMENT.md`
  ```markdown
  # Guía de Deployment
  
  ## Requisitos del servidor
  - Ubuntu 20.04+
  - Docker 20.10+
  - Docker Compose 2.0+
  - 2GB RAM mínimo
  - 20GB disco
  
  ## Instalación inicial
  1. Clonar repo
  2. Configurar .env.prod
  3. ./scripts/init-prod.sh
  
  ## Mantenimiento
  - Backups automáticos
  - Monitoreo de logs
  - Updates de seguridad
  
  ## Troubleshooting
  - App no arranca
  - BD llena
  - Performance degradado
  ```

- [ ] 7.4.2 Crear `docs/MONITORING.md`
  ```markdown
  # Monitoreo y Observabilidad
  
  ## Métricas a monitorear
  - CPU/Memoria del contenedor
  - Tiempo de respuesta de APIs
  - Errores 4xx/5xx
  - Tamaño de BD
  
  ## Health checks
  - Endpoint /health
  - Conectividad de BD
  - Cache availability
  
  ## Alertas
  - Error rate > 5%
  - Response time > 2s
  - DB disk > 80%
  ```

- [ ] 7.4.3 Crear `docs/SCALING.md`
  ```markdown
  # Guía de Escalado
  
  ## Horizontal scaling
  - Load balancer
  - Múltiples instancias de app
  - Session sharing
  
  ## Vertical scaling
  - Aumentar RAM/CPU
  - Optimizar queries
  
  ## Caché distribuido
  - Redis cluster
  - Price caching mejorado
  ```

**Criterios de aceptación**:
- ✅ Documentación es clara y completa
- ✅ Nuevos desarrolladores pueden hacer deploy
- ✅ Troubleshooting cubre casos comunes

---

### TAREA 7.5: Crear dashboard de monitoreo
**Objetivo**: Visualización de estado de la aplicación.

**Subtareas**:
- [ ] 7.5.1 Crear endpoint de métricas
  ```python
  # GET /api/v1/admin/metrics
  # Retorna:
  # {
  #   uptime: seconds,
  #   memory_usage: MB,
  #   cpu_usage: %,
  #   db_connections: N,
  #   cache_size: MB,
  #   last_price_update: datetime,
  #   operations_count: N,
  #   errors_24h: N,
  #   api_calls_24h: N
  # }
  ```

- [ ] 7.5.2 Crear página de admin
  ```html
  # /admin (protegida, solo admin)
  # Widgets:
  # - Status de servicios (verde/rojo)
  # - Última actualización de precios
  # - Estadísticas de uso
  # - Logs recientes
  # - Botón de refresh de precios
  # - Botón de backup manual
  ```

- [ ] 7.5.3 Crear health check más completo
  ```python
  # GET /health/detailed
  # Retorna:
  # {
  #   status: "healthy" | "degraded" | "down",
  #   timestamp: datetime,
  #   checks: {
  #     api: ok | error,
  #     db: ok | error,
  #     cache: ok | error,
  #     yfinance: ok | error
  #   }
  # }
  ```

**Criterios de aceptación**:
- ✅ Métricas son precisas
- ✅ Dashboard carga rápido
- ✅ Health check detecta problemas

---

## 📊 Estimaciones y Dependencias

### Timeline por Fase
| Fase | Duración | Puntos |
|------|----------|--------|
| 1. Setup | 2d | 8 |
| 2. Backend | 4d | 20 |
| 3. Datos | 2d | 10 |
| 4. Frontend | 3d | 15 |
| 5. Reportes | 2d | 12 |
| 6. Testing | 2d | 12 |
| 7. DevOps | 2d | 13 |
| **Total** | **17d** | **90** |

### Dependencias Críticas
```
1. Setup
  ├─> 2. Backend (requiere estructura)
  │    ├─> 3. Datos (requiere servicios)
  │    ├─> 4. Frontend (requiere API)
  │    └─> 5. Reportes (requiere servicios)
  └─> 7. DevOps (requiere app funcional)

6. Testing (puede empezar en paralelo a 2-4)
```

### Puntos de Integración Clave
- Después de 2.3: Backend + Frontend conectados
- Después de 2.4: API totalmente funcional
- Después de 3.1: Precios en tiempo real
- Después de 4.5: UX completa para entrada de datos
- Después de 5.2: Analytics funcional
- Después de 6.4: QA cerrado, listo para prod

---

## ✅ Criterios de Aceptación Global

### MVP debe cumplir:
1. ✅ Gestionar múltiples cuentas corrientes
2. ✅ Registrar compra/venta de activos
3. ✅ Obtener precios automáticos
4. ✅ Calcular patrimonio total y rentabilidad
5. ✅ Generar reportes básicos
6. ✅ Interfaz web funcional
7. ✅ Desplegar en Docker
8. ✅ Tests unitarios e integración
9. ✅ Documentación completa
10. ✅ CI/CD automatizado

### Performance Mínimo:
- Dashboard carga < 2 segundos
- API endpoints responden < 500ms
- Soporte para 10,000+ operaciones

### Seguridad Mínima:
- BD con contraseña
- No hardcoded secrets
- Validación de inputs
- Logs de cambios

### Documentación Mínima:
- README con instrucciones
- Docstrings en funciones
- Swagger docs automáticas
- Guía de deployment

---

## 📝 Notas Finales

**Riesgos identificados:**
- yfinance puede no tener todos los tickers
  - Mitigation: fallback a entrada manual
- Performance con muchos activos
  - Mitigation: índices en BD, caché de precios
- Fechas y zonas horarias
  - Mitigation: usar UTC internamente, convertir en UI

**Mejoras futuras (Fase 2+):**
- Autenticación y multi-usuario
- Alertas y notificaciones
- API de terceros (yodlee, plaid)
- Machine learning para predicciones
- Mobile app nativa
- Integración con impuestos
- Sincronización con brokers

**Herramientas recomendadas:**
- Git client: GitHub Desktop o GitKraken
- API testing: Postman o Insomnia
- DB management: DBeaver
- Monitoring: Grafana + Prometheus (fase 2)
- Alertas: PagerDuty (fase 2)

---

**Documento versión:** 1.0
**Última actualización:** 2026-09-25
**Responsable:** Equipo de desarrollo
