from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://order:order@localhost:5433/order"
    catalog_service_url: str = "http://localhost:8001"
    http_timeout_seconds: float = 5.0


settings = Settings()


class NotFoundError(Exception):
    pass
