from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    DATABASE_URL: str
    CHROMA_DB_PATH: str
    MODEL_NAME: str

    class Config:
        env_file = ".env"

settings = Settings()