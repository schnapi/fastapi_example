from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str
    postgres_user: str
    postgres_password: str

    # App
    debug: bool = False
    secret_key: str = "defaultsecret"

    # CORS - Allow Vite dev server in development
    allowed_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost",
        "http://127.0.0.1",
    ]

    class Config:
        env_file = ".env"
        extra = "forbid"


settings = Settings()  # type: ignore
