from functools import lru_cache
import os
from typing import Any, Optional, Union, List
from dotenv import find_dotenv
from pydantic import PostgresDsn, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

class AsyncPostgresDsn(PostgresDsn):
    allowed_schemes = {"postgres+asyncpg", "postgresql+asyncpg"}

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra='allow')

    # Debug
    DEBUG: bool

    # Backend
    BACKEND_TTILE: str
    BACKEND_DESCRIPTION: str
    BACKEND_PREFIX: str

    BACKEND_HOST: str
    BACKEND_PORT: int
    BACKEND_RELOAD: bool

    # BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    BACKEND_CORS_ORIGINS: List = ["*"]

    BACKEND_JWT_SECRET: str
    BACKEND_JWT_ALGORITHM: str
    BACKEND_JWT_ACCESS_TOKEN_EXPIRE_MINUTES: str = '21600'

    BACKEND_DISABLE_AUTH: bool
    BACKEND_DISABLE_FILE_SENDING: bool
    BACKEND_DISABLE_REGISTRATION: bool

    # AI
    CHAT_PDF_API_KEY: str
    GIGA_CREDS: str

    # Postgres
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int

    GEOJSON_DIR: str = os.path.join('app/geojson_files')

    SQLALCHEMY_DATABASE_URI: Union[Optional[AsyncPostgresDsn], Optional[str]] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_async_db_connection(cls, v: Optional[str], values: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        return AsyncPostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_SERVER"),
            port=values.data.get("POSTGRES_PORT"),
            path=f"{values.data.get('POSTGRES_DB') or ''}",
        )


@lru_cache
def get_config(env_file: str = ".env") -> Config:
    return Config(_env_file=find_dotenv(env_file))
