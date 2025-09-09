from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    postgres_db: str = "ecom"
    postgres_user: str = "ecom"
    postgres_password: str = "ecom"
    postgres_host: str = "db"
    postgres_port: int = 5432
    database_url: str = "postgresql+psycopg://ecom:ecom@db:5432/ecom"

    redis_url: str = "redis://redis:6379/0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


settings = Settings()
