from langchain.tools import BaseTool
from youtube_transcript_api import YouTubeTranscriptApi
import json
import logging
import os
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

def _transcript(video_id):
    return YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
    

class YouTubeCaptionTool(BaseTool):
    name: str = "youtube_captions"
    description: str = "Fetch the captions of a given YouTube video URL to use as context."

    def _run(self, url: str) -> str:
        # Extract video_id from URL
        # Typical formats: https://www.youtube.com/watch?v=VIDEO_ID or https://youtu.be/VIDEO_ID
        parsed_url = urlparse(url)
        # For 'youtube.com' links, the video ID is stored in query parameters
        if "youtube.com" in parsed_url.netloc:
            video_id = parse_qs(parsed_url.query).get("v", [None])[0]
        # For 'youtu.be' links, the video ID is stored in the path
        else:
            video_id = parsed_url.path[1:]


        try:
            logger.info("HTTPS_PROXY=%s", os.environ.get("HTTPS_PROXY"))
            return json.dumps(_transcript(video_id))
        except Exception as e:
            logger.exception(e)
            return f"Failed to get captions of {video_id}: {e}"

    async def _arun(self, url: str) -> str:
        # Async version if needed
        return self._run(url)
