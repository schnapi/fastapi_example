from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str
    postgres_password: str

    # App
    debug: bool = False
    secret_key: str = "defaultsecret"

    class Config:
        env_file = ".env"
        # fields = {
        #     "hot_reload": {"env": "HOT_RELOAD"},
        #     "debug": {"env": "DEBUG"},
        # }


settings = Settings()
