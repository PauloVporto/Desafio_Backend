from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_db: str = "desafio"
    postgres_user: str = "desafio"
    postgres_password: str = "desafio"
    postgres_host: str = "db"
    postgres_port: int = 5432

    mongo_url: str = "mongodb://mongo:27017"
    mongo_db: str = "desafio"

    jwt_secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    django_secret_key: str = "dev-django-secret-change-me"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()
