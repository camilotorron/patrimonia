"""Configuración centralizada de la aplicación.

Lee las variables de entorno usando pydantic-settings y proporciona
una instancia singleton :data:`settings` accesible desde cualquier módulo.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Entornos de ejecución soportados."""

    DEV = "dev"
    TEST = "test"
    PROD = "prod"


class Settings(BaseSettings):
    """Configuración de la aplicación cargada desde variables de entorno.

    Las variables se pueden sobreescribir con un archivo ``.env`` en la raíz
    del proyecto o con variables de entorno del sistema.
    """

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # —— App ——————————————————————————————————————————————
    APP_NAME: str = "Patrimonia"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: Environment = Environment.DEV

    # —— API ——————————————————————————————————————————————
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_DEBUG: bool = True

    # —— Database ————————————————————————————————————————
    DATABASE_URL: str = "sqlite:///./patrimonio.db"

    # —— yFinance ————————————————————————————————————————
    YFINANCE_TIMEOUT: int = 10
    PRICE_CACHE_TTL: int = 3600

    # —— Logging ————————————————————————————————————————
    LOG_LEVEL: str = "INFO"

    # —— CORS ——————————————————————————————————————————
    CORS_ORIGINS: List[str] = ["*"]

    # —— Cache TTL por tipo de activo (segundos) ————————
    CACHE_TTL_STOCK: int = 900  # 15 min
    CACHE_TTL_ETF: int = 1800  # 30 min
    CACHE_TTL_CRYPTO: int = 300  # 5 min
    CACHE_TTL_OTHER: int = 3600  # 1 h

    # —— Initial data ————————————————————————————————————
    INIT_DATA_DIR: str = "init_data"

    # —— Paths ——————————————————————————————————————————
    @property
    def base_dir(self) -> Path:
        """Directorio raíz del backend."""
        return Path(__file__).resolve().parent.parent

    @property
    def init_data_dir(self) -> Path:
        """Directorio con los datos iniciales (JSON)."""
        return self.base_dir.parent / self.INIT_DATA_DIR

    # —— Helpers ————————————————————————————————————————
    @property
    def is_dev(self) -> bool:
        return self.ENVIRONMENT == Environment.DEV

    @property
    def is_prod(self) -> bool:
        return self.ENVIRONMENT == Environment.PROD

    @property
    def is_test(self) -> bool:
        return self.ENVIRONMENT == Environment.TEST

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    def model_post_init(self, __context) -> None:  # noqa: ANN001
        """Resuelve rutas SQLite relativas a absolutas desde la raíz del proyecto."""
        project_root = Path(__file__).resolve().parent.parent.parent
        if self.DATABASE_URL.startswith("sqlite:///./"):
            db_name = self.DATABASE_URL.replace("sqlite:///./", "")
            self.DATABASE_URL = f"sqlite:///{project_root / db_name}"


settings = Settings()
