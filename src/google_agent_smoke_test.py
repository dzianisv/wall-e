import os
import json
import pytest
import mongomock
import requests
from importlib import reload

# Skip the test if required environment variables are missing
openai_key = os.environ.get("OPENAI_API_KEY")
gmail_token = os.environ.get("GMAIL_TOKEN_JSON")
client_id = os.environ.get("GOOGLE_CLIENT_ID")
client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")

skip_reason = None
if not openai_key:
    skip_reason = "OPENAI_API_KEY not set"
elif not gmail_token:
    skip_reason = "GMAIL_TOKEN_JSON not set"
elif not client_id or not client_secret:
    skip_reason = "Google client secrets not set"

try:
    requests.head("https://gmail.googleapis.com", timeout=5)
except Exception:
    skip_reason = "Network access to Gmail unavailable"

pytestmark = pytest.mark.skipif(skip_reason is not None, reason=skip_reason)

@pytest.fixture(scope="module")
def llm_instance(monkeypatch):
    monkeypatch.setattr("pymongo.MongoClient", mongomock.MongoClient)
    import google_workspace
    reload(google_workspace)
    import google_workspace_tool
    reload(google_workspace_tool)
    import llm
    reload(llm)

    # load token and store in mocked db
    with open(gmail_token) as f:
        token_data = json.load(f)
    token_data["_id"] = "smoke-user"
    google_workspace.google_workspace.collection.insert_one(token_data)

    return llm.LLM()

def test_llm_fetch_emails(llm_instance):
    response = llm_instance.ask("list my most recent emails 1", session_id="smoke-user")
    assert isinstance(response, str) and response
