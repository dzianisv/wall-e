# test_llm.py
import os
import pytest
from unittest.mock import patch, MagicMock
from llm import LLM
import requests

try:
    requests.head("https://www.youtube.com", timeout=5)
except Exception:
    pytest.skip("Network access to YouTube unavailable", allow_module_level=True)

openai_key = os.environ.get("OPENAI_API_KEY")
if not openai_key:
    pytest.skip("OPENAI_API_KEY not set", allow_module_level=True)

@pytest.fixture
def llm_instance():
    return LLM()

def test_ask_weather(llm_instance):
    response = llm_instance.ask("What is the weather like?")
    print(response)
    assert len(response) > 0

def test_ask_fedfundrate(llm_instance):
    response = llm_instance.ask("What is the current federal funds rate?")
    print(response)
    assert len(response) > 0

def test_ask_youtube_context(llm_instance):
    youtube_url = "https://www.youtube.com/watch?v=uT0kHewjzkE"
    response = llm_instance.ask(f"What is the context of the YouTube video {youtube_url}?")
    print(response)
    assert len(response) > 0

def test_ask_youtube_podcast(llm_instance):
    response = llm_instance.ask(f"О чем рассказывается в этом подкасте https://www.youtube.com/watch?v=qI5T5VnvcYg")
    print(response)
    assert len(response) > 0
  