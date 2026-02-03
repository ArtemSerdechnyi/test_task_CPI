from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[4]

class _BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        case_sensitive=True,
        extra="ignore",
    )

class Settings(_BaseConfig):
    SERVER_HOST: str
    SERVER_PORT: int
    RELOAD: bool = True
    FRONTEND_URLS: list[str]


settings = Settings()