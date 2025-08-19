Decisions:
1. Python vs Node.js: python, because it supports more community tools (https://python.langchain.com/v0.1/docs/integrations/tools/)
2. Use MongoDB Chat Memory: https://python.langchain.com/v0.1/docs/integrations/chat_memory/mongodb/
3. Mongodb at cloud: https://cloud.mongodb.com/ (free tier)


## quickstart

```bash
pipenv install
pipenv run python -m spacy download en_core_web_sm
```

## MCP integrations

The bot supports connecting external Model Context Protocol (MCP) servers.

### Commands

* `/mcp` – list connected MCP servers
* `/mcp <url>` – connect a new MCP server
* `/mcp delete <index>` – remove a server by index
* `/integration gmail` – connect the Gmail MCP server
* `/integration calendar` – connect the Google Calendar MCP server

By default the Gmail server uses [GongRzhe/Gmail-MCP-Server](https://github.com/GongRzhe/Gmail-MCP-Server)
and the Calendar server uses [taylorwilsdon/google_workspace_mcp](https://github.com/taylorwilsdon/google_workspace_mcp).



## github required env variables

- OPENAI_API_KEY
- TELEGRAM_BOT_TOKEN
- NOMAD_ADDR
- NOMAD_CACERT
- NOMAD_CLIENT_CERT
- NOMAD_CLIENT_KEY
