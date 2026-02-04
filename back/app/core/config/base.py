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
    ENV: str = "prod"
    FRONTEND_URLS: list[str]
    OPENAI_API_KEY: str
    LLM: str = "gpt-4o"
    CPI_SOURCE_URL: str = (
        "https://www.rateinflation.com/consumer-price-index/germany-historical-cpi/"
    )


settings = Settings()
