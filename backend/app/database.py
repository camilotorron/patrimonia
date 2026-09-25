"""Configuración de la base de datos con SQLAlchemy 2.0.

Proporciona:
- :data:`engine` — el motor de SQLAlchemy.
- :data:`SessionLocal` — fábrica de sesiones.
- :func:`get_db` — dependencia de FastAPI.
- :func:`init_db` / :func:`drop_db` — utilidades para crear/eliminar tablas.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.models.base import Base  # re-export del Base de los modelos

# ------------------------------------------------------------------ #
# Engine
# ------------------------------------------------------------------ #
if settings.is_sqlite:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False,
    )

# Habilitar foreign keys en SQLite
if settings.is_sqlite:

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):  # noqa: ANN001
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# ------------------------------------------------------------------ #
# Session factory
# ------------------------------------------------------------------ #
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ------------------------------------------------------------------ #
# Dependencies & utilities
# ------------------------------------------------------------------ #
def get_db() -> Generator[Session, None, None]:
    """Dependencia de FastAPI: entrega una sesión y la cierra al final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager para usar sesiones fuera del ciclo de vida de FastAPI."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """Crea todas las tablas definidas en los modelos."""
    # Importar todos los modelos para que se registren en Base.metadata
    import app.models.account  # noqa: F401
    import app.models.account_balance  # noqa: F401
    import app.models.asset  # noqa: F401
    import app.models.audit_log  # noqa: F401
    import app.models.operation  # noqa: F401
    import app.models.price  # noqa: F401

    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """Elimina todas las tablas."""
    # Importar todos los modelos para que se registren en Base.metadata
    import app.models.account  # noqa: F401
    import app.models.account_balance  # noqa: F401
    import app.models.asset  # noqa: F401
    import app.models.audit_log  # noqa: F401
    import app.models.operation  # noqa: F401
    import app.models.price  # noqa: F401

    Base.metadata.drop_all(bind=engine)


def health_check() -> bool:
    """Verifica la conectividad con la base de datos."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
