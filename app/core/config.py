from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import ClassVar

class Settings(BaseSettings):
    RP_ID: str
    RP_NAME: str
    RP_ORIGIN: str
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str

    model_config = SettingsConfigDict(
        env_file=".env"
    )

class TokenSettings(BaseSettings):
    ACCESS: ClassVar[str] = "access_token"
    REFRESH: ClassVar[str] = "refresh_token"

    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int

    model_config = SettingsConfigDict(
        env_file=".env"
)

token_settings = TokenSettings()
settings = Settings()
