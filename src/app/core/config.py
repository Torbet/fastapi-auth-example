from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    jwt_secret: str = "secret"


class DatabaseSettings(BaseSettings):
    database_user: str = "admin"
    database_password: str = "admin"
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "db"

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"


class Settings(AuthSettings, DatabaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()  # type: ignore
