from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MIN: int = 30

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

@lru_cache()
def get_settings() -> Settings:
    # Returns a cached singleton instance of the application settings
    return Settings()