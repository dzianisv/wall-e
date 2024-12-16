from langchain.tools import BaseTool
from youtube_transcript_api import YouTubeTranscriptApi
import re
import json

def _transcript(video_id):
    return YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
    

class YouTubeCaptionTool(BaseTool):
    name: str = "youtube_captions"
    description: str = "Fetch the captions of a given YouTube video URL to use as context."

    def _run(self, url: str) -> str:
        # Extract video_id from URL
        # Typical formats: https://www.youtube.com/watch?v=VIDEO_ID or https://youtu.be/VIDEO_ID
        match = re.search(r"(?:v/|be/|v=|\/)([^&?]+)", url)
        if not match:
            return "No valid video_id found in URL."
        video_id = match.group(1)

        try:
            return json.dumps(_transcript(video_id))
        except Exception as e:
            return f"Failed to get captions of {video_id}: {e}"

    async def _arun(self, url: str) -> str:
        # Async version if needed
        return self._run(url)
