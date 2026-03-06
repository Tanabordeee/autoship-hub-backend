from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_HOURS: int
    DATABASE_URL: str
    OCR_MODEL: str = "scb10x/typhoon-ocr1.5-3b:latest"
    POPPLER_PATH: str = r"E:\poppler\poppler-25.12.0\Library\bin"
    TYPHOON_API_KEY: str = os.getenv("TYPHOON_API_KEY")
    TYPHOON_OCR_URL: str = "https://api.opentyphoon.ai/v1/ocr"
    TYPHOON_CHAT_URL: str = "https://api.opentyphoon.ai/v1"
    TYPHOON_CHAT_MODEL: str = "typhoon-v2.5-30b-a3b-instruct"
    DEMO: int = os.getenv("DEMO", 1)

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
