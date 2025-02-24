import os

class Config:
    mongo_uri = os.environ.get("MONGODB_URI")
    openai_api_base = os.environ.get("OPENAI_API_BASE")
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    openai_proxy = os.environ.get("OPENAI_PROXY")
    # https://platform.openai.com/docs/models#gpt-4o-mini
    openai_model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    telegram_bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
