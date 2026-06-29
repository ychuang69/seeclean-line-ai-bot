import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    app_name: str = os.getenv("APP_NAME", "seeclean-line-ai-bot")
    environment: str = os.getenv("ENVIRONMENT", "local")
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'app.db'}")

    line_channel_secret: str = os.getenv("LINE_CHANNEL_SECRET", "")
    line_channel_access_token: str = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
    line_reply_api_url: str = os.getenv("LINE_REPLY_API_URL", "https://api.line.me/v2/bot/message/reply")

    ai_enabled: bool = os.getenv("AI_ENABLED", "false").lower() in {"1", "true", "yes", "on"}
    ai_api_key: str = os.getenv("AI_API_KEY", "")
    ai_api_url: str = os.getenv("AI_API_URL", "https://api.openai.com/v1/chat/completions")
    ai_model: str = os.getenv("AI_MODEL", "gpt-4o-mini")


settings = Settings()
