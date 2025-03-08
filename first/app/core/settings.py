from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from openai import AsyncOpenAI

from typing import Optional
import redis

class Settings(BaseSettings):
    BOT_TOKEN: str
    AI_TOKEN: str
    REDIS_URL: Optional[str]
    ASSISTANT_ID: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.env"),
        override=True, extra="ignore"
    )

    def get_bot_settings(self):
        return self.BOT_TOKEN
    
    def get_ai_settings(self):
        return AsyncOpenAI(api_key=self.AI_TOKEN)
    
    def get_thread_db(self):
        if self.REDIS_URL != "":
            return redis.from_url(self.REDIS_URL, decode_responses=True)
        else: 
            return redis.Redis(host="redis", port=6379, decode_responses=True)
    
    def get_assistant(self):
        return self.ASSISTANT_ID
    
settings = Settings()

class TreasureSettings(BaseSettings):
    DB_NAME: str
    DB_USER: str
    DB_HOST: str
    DB_PORT: str
    DB_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.env"),
        extra="ignore"
    )

    def get_treasure_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
treasure_db_settings = TreasureSettings()