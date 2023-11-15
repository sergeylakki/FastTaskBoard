import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv, find_dotenv
load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL_FOR_TEST: str
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int

    #model_config = SettingsConfigDict(
    #    env_file="~/.env",
    #    env_file_encoding='utf-8'
    #)

    class Config:
        env_file = find_dotenv(".env")
        env_file_encoding = "utf-8"

settings = Settings()