from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Task Manager API"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./task_manager.db"

    # JWT
    SECRET_KEY: str = "changeme-use-a-long-random-secret-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
