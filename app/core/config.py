from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "eTODA Bongao API"
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "etoda_db"
    SECRET_KEY: str = "super-secret-key-for-tcto-lgu"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    class Config:
        env_file = ".env"

settings = Settings()