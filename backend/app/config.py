from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    groq_api_key: str
    openai_api_key: str
    uazapi_base_url: str
    uazapi_token: str
    uazapi_instance: str
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
