import threading
from langchain.tools import BaseTool
from langchain_google_community.gmail.search import GmailSearch
from google_workspace import google_workspace

session_context = threading.local()

class GoogleEmailsTool(BaseTool):
    name: str = "google_recent_emails"
    description: str = "Fetch recent email subjects from user's Gmail account. Input should be the number of emails to fetch."

    def _run(self, count: str) -> str:
        try:
            num = int(count)
        except ValueError:
            num = 5
        user_id = getattr(session_context, 'session_id', 'unknown')
        toolkit = google_workspace.get_gmail_toolkit(user_id)
        if not toolkit:
            return 'Please authorize using /google_auth.'
        search_tool = GmailSearch(api_resource=toolkit.api_resource)
        results = search_tool.run('in:inbox', max_results=num)
        if not results:
            return 'No messages found.'
        subjects = [r['subject'] for r in results][:num]
        return '\n'.join(subjects)

    async def _arun(self, count: str) -> str:
        return self._run(count)

class GoogleCalendarTool(BaseTool):
    name: str = "google_today_events"
    description: str = "Get today's events from user's primary Google Calendar."

    def _run(self, _: str = "") -> str:
        user_id = getattr(session_context, 'session_id', 'unknown')
        return google_workspace.get_today_events(user_id)

    async def _arun(self, query: str = "") -> str:
        return self._run(query)

class GoogleDriveTool(BaseTool):
    name: str = "google_list_drive_files"
    description: str = "List files from user's Google Drive. Input is the number of files to list."

    def _run(self, count: str) -> str:
        try:
            num = int(count)
        except ValueError:
            num = 5
        user_id = getattr(session_context, 'session_id', 'unknown')
        return google_workspace.list_drive_files(user_id, num)

    async def _arun(self, count: str) -> str:
        return self._run(count)


class GoogleKeepTool(BaseTool):
    name: str = "google_keep_notes"
    description: str = (
        "List notes from user's Google Keep. Input is the number of notes to list."
    )

    def _run(self, count: str) -> str:
        try:
            num = int(count)
        except ValueError:
            num = 5
        user_id = getattr(session_context, 'session_id', 'unknown')
        return google_workspace.list_keep_notes(user_id, num)

    async def _arun(self, count: str) -> str:
        return self._run(count)
