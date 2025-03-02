from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    BOT_TOKEN: str
    AI_TOKEN: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.env")
    )

    def get_bot_settings(self):
        return self.BOT_TOKEN
    
    def get_ai_settings(self):
        return self.AI_TOKEN
    
settings = Settings()