#!/usr/bin/env python3
import os
import sys
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

try:
    from youtube_captions_tool import _transcript, YouTubeCaptionTool
except ModuleNotFoundError:  # pragma: no cover
    pytest.skip("langchain not installed", allow_module_level=True)

if not os.environ.get("YOUTUBE_TESTS"):
    pytest.skip("YOUTUBE_TESTS not set", allow_module_level=True)

def test_transcript():
    text = _transcript("Oa_RSwwpPaA")
    print(text)
    assert len(text) > 0


def test_tool():
    text = YouTubeCaptionTool().run("https://www.youtube.com/watch?v=uT0kHewjzkE")
    print(text)
    assert text is not None
