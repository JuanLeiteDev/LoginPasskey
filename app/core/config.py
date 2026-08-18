from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    RP_ID: str
    RP_NAME: str
    RP_ORIGIN: str
    DATABASE_URL: str
    SECRET_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env"
    )

settings = Settings()
