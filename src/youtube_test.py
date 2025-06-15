#!/usr/bin/env python3

import os
import pytest
from youtube_captions_tool import _transcript, YouTubeCaptionTool
import requests

try:
    requests.head("https://www.youtube.com", timeout=5)
except Exception:
    pytest.skip("Network access to YouTube unavailable", allow_module_level=True)

openai_key = os.environ.get("OPENAI_API_KEY")
if not openai_key:
    pytest.skip("OPENAI_API_KEY not set", allow_module_level=True)

def test_transcript():
    text = _transcript("Oa_RSwwpPaA")
    print(text)
    assert len(text) > 0


def test_tool():
    text = YouTubeCaptionTool().run("https://www.youtube.com/watch?v=uT0kHewjzkE")
    print(text)
    assert text is not None
