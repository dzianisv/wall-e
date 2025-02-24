# wall-e

![](./doc/demo1.webp)

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
