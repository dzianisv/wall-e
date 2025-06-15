Decisions:
1. Python vs Node.js: python, because it supports more community tools (https://python.langchain.com/v0.1/docs/integrations/tools/)
2. Use MongoDB Chat Memory: https://python.langchain.com/v0.1/docs/integrations/chat_memory/mongodb/
3. Mongodb at cloud: https://cloud.mongodb.com/ (free tier)


## quickstart

```bash
pipenv install
pipenv run python -m spacy download en_core_web_sm
```



## github required env variables

- OPENAI_API_KEY
- TELEGRAM_BOT_TOKEN
- NOMAD_ADDR
- NOMAD_CACERT
- NOMAD_CLIENT_CERT
- NOMAD_CLIENT_KEY
- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET
- GMAIL_TOKEN_JSON *(path to OAuth token for test Gmail account)*

## google workspace integration

1. Run `/google_auth` command in the chat to receive an authorization link.
2. Open the link, grant access and copy the verification code.
3. Send `/google_auth_code <code>` back to the bot to finish setup.
4. Optionally provide Google Keep access using `/keep_auth <email> <token>` where token is a master token from gkeepapi docs.
5. After that the assistant can use tools based on the `langchain-google-community` package to read recent emails, calendar events, drive files and Keep notes.

## smoke test

To run the Gmail/LLM smoke test on CI, set `GMAIL_TOKEN_JSON` to the token file
for the dev Gmail account along with `OPENAI_API_KEY`, `GOOGLE_CLIENT_ID` and
`GOOGLE_CLIENT_SECRET`.
