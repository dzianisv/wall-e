#!/usr/bin/env python3

from unittest.mock import patch
from youtube_captions_tool import _transcript

def test_transcript():
    text = _transcript("Oa_RSwwpPaA")
    print(text)
    assert len(text) > 0
