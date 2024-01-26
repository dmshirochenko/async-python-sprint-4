import os

from pydantic import BaseSettings, Field


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env_file = ".env"
ENV_FILE_PATH = os.path.join(BASE_DIR, env_file)


class Settings(BaseSettings):
    app_debug_level: str = Field("INFO", env="APP_DEBUG_LEVEL")
    base_dir: str = Field(BASE_DIR)
    env_name: str = "Local"
    base_url: str = "http://localhost:8000"
    db_url: str = "sqlite:///./shortener.db"

    class Config:
        env_file = ENV_FILE_PATH


settings = Settings()
