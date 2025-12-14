from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="deploy/.env", env_file_encoding="utf-8")

    DB_HOST: str
    DB_PORT: str
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_PASSWORD: str

    KAFKA_HOSTS: list[str]

    SAGA_EVENTS_TOPIC: str
    ORDER_EVENTS_TOPIC: str
    NOTIFICATION_EVENTS_TOPIC: str
    ANALYTIC_EVENTS_TOPIC: str
    PAYMENT_EVENTS_TOPIC: str


settings = Settings()

DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.POSTGRES_DB}?async_fallback=True"
)

VERSION = 1
