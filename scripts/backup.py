"""Script para hacer backup de la base de datos."""

from __future__ import annotations

import shutil
import sys
from datetime import datetime
from pathlib import Path

from app.config import settings


def backup_database() -> Path | None:
    """Crea una copia de seguridad de la base de datos SQLite."""
    if not settings.is_sqlite:
        print("⚠️  El backup automático solo soporta SQLite en este script.")
        return None

    db_path = Path(settings.DATABASE_URL.replace("sqlite:///", ""))
    if not db_path.exists():
        print(f"⚠️  No se encontró la BD en {db_path}")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = db_path.parent / "backups"
    backup_dir.mkdir(exist_ok=True)
    backup_path = backup_dir / f"patrimonio_{timestamp}.db"

    shutil.copy2(db_path, backup_path)
    print(f"✅ Backup creado: {backup_path}")
    return backup_path


if __name__ == "__main__":
    backup_database()
