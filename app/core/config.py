from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_HOURS: int
    DATABASE_URL: str
    OCR_MODEL: str = "scb10x/typhoon-ocr1.5-3b:latest"
    POPPLER_PATH: str = r"E:\poppler\poppler-25.12.0\Library\bin"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
