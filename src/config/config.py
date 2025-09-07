from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):

    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4.1"
    BACKEND_URL: str | None = None

    MONGODB_URI: str
    MONGODB_DB: str
    MONGODB_DB_NAME: str

    LANGCHAIN_API_KEY: str
    LANGCHAIN_ENDPOINT: str
    LANGCHAIN_TRACING_V2: bool
    LANGCHAIN_TRACING: str

    class Config:
        # Compute env file path relative to the project root
        env_file = str(Path(__file__).resolve().parents[2] / ".env")
        env_file_encoding = "utf-8"



def load_settings():
    return Settings()

def load_key_from_env(key: str):
    """
    Load a single setting value using the Settings class.
    """
    settings = Settings()
    return getattr(settings, key, None)

