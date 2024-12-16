import os

class Config:
    mongo_uri = os.environ.get("MONGO_URI")
    openai_api_base = os.environ.get("OPENAI_API_BASE")
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    openai_proxy = os.environ.get("OPENAI_PROXY")
    openai_model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
