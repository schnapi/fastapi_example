from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str
    postgres_user: str
    postgres_password: str

    # App
    debug: bool = False
    secret_key: str = "defaultsecret"

    class Config:
        env_file = ".env"
        extra = "forbid"


settings = Settings()
