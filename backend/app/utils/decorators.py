"""Decoradores de utilidad."""

from __future__ import annotations

import functools
import logging
from typing import Any, Callable, TypeVar

from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def transactional(func: F) -> F:
    """Decorador que envuelve una función en una transacción de BD.

    - Si la función recibe ``db`` como primer argumento, usa esa sesión.
    - Si la ejecución es exitosa → commit.
    - Si ocurre una excepción → rollback y re-raise.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        db = kwargs.get("db") or (args[0] if args else None)
        try:
            result = func(*args, **kwargs)
            if db is not None and hasattr(db, "commit"):
                db.commit()
            return result
        except SQLAlchemyError as exc:
            if db is not None and hasattr(db, "rollback"):
                db.rollback()
            logger.exception("Transaction failed in %s: %s", func.__name__, exc)
            raise
        except Exception:
            if db is not None and hasattr(db, "rollback"):
                db.rollback()
            raise

    return wrapper  # type: ignore[return-value]
