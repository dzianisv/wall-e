#!/usr/bin/env python3

from unittest.mock import patch
from youtube_captions_tool import _transcript, YouTubeCaptionTool

def test_transcript():
    text = _transcript("Oa_RSwwpPaA")
    print(text)
    assert len(text) > 0


def test_tool():
    text = YouTubeCaptionTool().run("https://www.youtube.com/watch?v=uT0kHewjzkE")
    print(text)
    assert text is not None
