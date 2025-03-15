from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from openai import AsyncOpenAI
from amplitude import Amplitude, BaseEvent

from typing import Optional

class Settings(BaseSettings):
    BOT_TOKEN: str
    AI_TOKEN: str
    ASSISTANT_ID: Optional[str] = None
    AMPLITUDE_TOKEN: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.env"),
        override=True, extra="ignore"
    )

    def get_bot_settings(self):
        return self.BOT_TOKEN
    
    def get_ai_settings(self):
        return AsyncOpenAI(api_key=self.AI_TOKEN)
    
    def get_assistant(self):
        return self.ASSISTANT_ID
    
    def get_amplitude_token(self):
        return Amplitude(self.AMPLITUDE_TOKEN)
    
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

class RedisSettings(BaseSettings):
    REDIS_USER: Optional[str]
    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_PASSWORD: Optional[str]

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.env"),
        extra="ignore"
    )

    def get_thread_db(self):
        if not self.REDIS_PASSWORD and not self.REDIS_USER:
            return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
        return f"redis://{self.REDIS_USER}:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"
    
redis_settings = RedisSettings()