from langchain.tools import BaseTool
from youtube_transcript_api import YouTubeTranscriptApi
import re

class YouTubeCaptionTool(BaseTool):
    name: str = "youtube_captions"
    description: str = "Fetch the captions of a given YouTube video URL to use as context."

    def _run(self, url: str) -> str:
        # Extract video_id from URL
        # Typical formats: https://www.youtube.com/watch?v=VIDEO_ID or similar
        match = re.search(r"v=([^&]+)", url)
        if not match:
            return "No valid video_id found in URL."
        video_id = match.group(1)

        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            full_text = " ".join([x['text'] for x in transcript])
            return full_text
        except Exception as e:
            return f"Failed to get captions: {e}"

    async def _arun(self, url: str) -> str:
        # Async version if needed
        return self._run(url)
