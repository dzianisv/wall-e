import os

class Config:
    mongo_uri = os.environ.get("MONGODB_URI")
    openai_api_base = os.environ.get("OPENAI_API_BASE")
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    openai_proxy = os.environ.get("OPENAI_PROXY")
    openai_model = os.environ.get("OPENAI_MODEL", "gpt-4o")
    telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    gmail_mcp_url = os.environ.get(
        "GMAIL_MCP_URL",
        "https://github.com/GongRzhe/Gmail-MCP-Server",
    )
    calendar_mcp_url = os.environ.get(
        "CALENDAR_MCP_URL",
        "https://github.com/taylorwilsdon/google_workspace_mcp",
    )
    integration_auth_base = os.environ.get(
        "INTEGRATION_AUTH_BASE",
        "https://example.com/auth",
    )
