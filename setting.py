from pydantic import BaseSettings


class AppSettings(BaseSettings):
    app_name: str = "app"
    database_url: str = "postgresql://postgres:postgr@127.0.0.1:5432/Test"

    class Config:
        env_file = ".env"
