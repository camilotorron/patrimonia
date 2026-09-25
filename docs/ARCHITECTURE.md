# Arquitectura

## 📐 Visión General

Patrimonia sigue una **arquitectura por capas** con clara separación de responsabilidades:

```
┌─────────────────────────────────────────────────┐
│                  Frontend (HTML/CSS/JS)           │
│               frontend/ (independiente)            │
├─────────────────────────────────────────────────┤
│                    API Layer                       │
│             backend/app/routes/                    │
│        (FastAPI endpoints, validación)             │
├─────────────────────────────────────────────────┤
│                  Service Layer                     │
│            backend/app/services/                   │
│       (Lógica de negocio, cálculos)               │
├─────────────────────────────────────────────────┤
│                Repository Layer                    │
│           backend/app/repositories/                │
│         (Acceso a datos, CRUD genérico)           │
├─────────────────────────────────────────────────┤
│                  Model Layer                       │
│              backend/app/models/                   │
│          (SQLAlchemy ORM, entidades)              │
├─────────────────────────────────────────────────┤
│              Database (SQLite / Postgres)          │
└─────────────────────────────────────────────────┘
```

## 🔀 Flujo de Datos

```
HTTP Request → Route → Service → Repository → Model → DB
                   ↓
              Pydantic Schema (validación)
                   ↓
              DTO (Dataclass) (transferencia)
```

1. **Route** recibe la petición HTTP y valida con schemas Pydantic
2. **Service** contiene la lógica de negocio, usa DTOs internamente
3. **Repository** abstrae el acceso a datos con un patrón genérico
4. **Model** define la estructura de datos en SQLAlchemy

## 🧩 Patrones de Diseño

- **Repository Pattern**: Abstracción del acceso a datos con `BaseRepository[T]` genérico
- **DTO Pattern**: Dataclasses inmutables para transferencia entre capas
- **Dependency Injection**: FastAPI `Depends()` para inyectar sesiones de BD
- **Strategy Pattern**: `PriceProvider` abstracto con implementación `YFinancePriceProvider`
- **Singleton**: Instancias de configuración y caché

## 🔄 Integración Externa

```
PriceService (orquestador)
    ├── PriceCacheService (caché TTL)
    │       └── cachetools.TTLCache
    ├── YFinancePriceProvider (datos externos)
    │       └── yfinance API
    └── PriceRepository (persistencia BD)
```

El flujo de obtención de precios sigue un patrón de **fallback en cascada**:
1. Caché en memoria → 2. yfinance API → 3. Último precio en BD → 4. Precio del asset

## 🐳 Deployment

- **Dev**: SQLite + Docker Compose con hot-reload
- **Prod**: PostgreSQL + Docker Compose con health checks
- **CI/CD**: GitHub Actions (lint → test → build → deploy)
