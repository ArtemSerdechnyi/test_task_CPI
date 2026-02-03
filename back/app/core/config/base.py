from pydantic_settings import BaseSettings, SettingsConfigDict

class _BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

class Settings(_BaseConfig):
    FRONTEND_URLS: list[str]