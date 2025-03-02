from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from openai import AsyncOpenAI

class Settings(BaseSettings):
    BOT_TOKEN: str
    AI_TOKEN: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.env"),
        override=True
    )

    def get_bot_settings(self):
        return self.BOT_TOKEN
    
    def get_ai_settings(self):
        return AsyncOpenAI(api_key=self.AI_TOKEN)
    
settings = Settings()