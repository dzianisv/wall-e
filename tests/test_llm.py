# test_llm.py
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

try:
    from llm import LLM
except ModuleNotFoundError:  # pragma: no cover
    pytest.skip("langchain not installed", allow_module_level=True)

if not os.environ.get("OPENAI_API_KEY"):
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
  