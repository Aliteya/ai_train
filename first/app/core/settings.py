from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from openai import AsyncOpenAI

from typing import Optional
import redis

class Settings(BaseSettings):
    BOT_TOKEN: str
    AI_TOKEN: str
    ASSISTANT_ID: Optional[str] =None

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.env"),
        override=True, extra="ignore"
    )

    def get_bot_settings(self):
        return self.BOT_TOKEN
    
    def get_ai_settings(self):
        return AsyncOpenAI(api_key=self.AI_TOKEN)
    
    def get_db(self):
        return redis.Redis(host="redis", port=6379, decode_responses=True)
    
    def get_assistant(self):
        return self.ASSISTANT_ID
    
settings = Settings()