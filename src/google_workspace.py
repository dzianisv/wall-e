import os
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from langchain_google_community.gmail.utils import build_resource_service as build_gmail_service
from langchain_google_community.gmail.toolkit import GmailToolkit
from langchain_google_community.calendar.utils import build_resource_service as build_calendar_service
from pymongo import MongoClient
from config import Config

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/drive.readonly',
]

class GoogleWorkspace:
    def __init__(self):
        self.client_config = {
            'installed': {
                'client_id': Config.google_client_id,
                'client_secret': Config.google_client_secret,
                'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                'token_uri': 'https://oauth2.googleapis.com/token',
                'redirect_uris': ['urn:ietf:wg:oauth:2.0:oob']
            }
        }
        client = MongoClient(Config.mongo_uri)
        self.collection = client['walle']['google_tokens']

    def start_authorization(self, user_id: str) -> str:
        flow = Flow.from_client_config(self.client_config, scopes=SCOPES)
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        auth_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true', prompt='consent')
        self.collection.update_one({'_id': user_id}, {'$set': {'state': state}}, upsert=True)
        return auth_url

    def finish_authorization(self, user_id: str, code: str) -> None:
        doc = self.collection.find_one({'_id': user_id})
        state = doc.get('state') if doc else None
        flow = Flow.from_client_config(self.client_config, scopes=SCOPES, state=state)
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        flow.fetch_token(code=code)
        creds = flow.credentials
        data = {
            '_id': user_id,
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes,
        }
        self.collection.update_one({'_id': user_id}, {'$set': data}, upsert=True)

    def _get_credentials(self, user_id: str):
        doc = self.collection.find_one({'_id': user_id})
        if not doc or 'token' not in doc:
            return None
        creds = Credentials(
            token=doc['token'],
            refresh_token=doc.get('refresh_token'),
            token_uri=doc['token_uri'],
            client_id=doc['client_id'],
            client_secret=doc['client_secret'],
            scopes=doc['scopes'],
        )
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            self.collection.update_one({'_id': user_id}, {'$set': {
                'token': creds.token,
                'refresh_token': creds.refresh_token
            }})
        return creds

    def get_recent_emails(self, user_id: str, num: int = 5) -> str:
        creds = self._get_credentials(user_id)
        if not creds:
            return 'Please authorize using /google_auth.'
        service = build_gmail_service(credentials=creds)
        results = service.users().messages().list(userId='me', maxResults=num).execute()
        messages = results.get('messages', [])
        subjects = []
        for msg in messages:
            m = service.users().messages().get(userId='me', id=msg['id'], format='metadata', metadataHeaders=['Subject']).execute()
            for h in m.get('payload', {}).get('headers', []):
                if h['name'] == 'Subject':
                    subjects.append(h['value'])
                    break
        if not subjects:
            return 'No messages found.'
        return '\n'.join(subjects)

    def get_today_events(self, user_id: str) -> str:
        creds = self._get_credentials(user_id)
        if not creds:
            return 'Please authorize using /google_auth.'
        service = build_calendar_service(credentials=creds)
        now = datetime.utcnow().isoformat() + 'Z'
        end = (datetime.utcnow() + timedelta(days=1)).isoformat() + 'Z'
        events = service.events().list(calendarId='primary', timeMin=now, timeMax=end, singleEvents=True, orderBy='startTime').execute().get('items', [])
        res = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', '')
            res.append(f"{start}: {summary}")
        if not res:
            return 'No events.'
        return '\n'.join(res)

    def list_drive_files(self, user_id: str, num: int = 5) -> str:
        creds = self._get_credentials(user_id)
        if not creds:
            return 'Please authorize using /google_auth.'
        service = build('drive', 'v3', credentials=creds)
        results = service.files().list(pageSize=num, fields='files(id,name)').execute()
        files = results.get('files', [])
        if not files:
            return 'No files found.'
        return '\n'.join([f"{f['name']} ({f['id']})" for f in files])

    def get_gmail_toolkit(self, user_id: str):
        creds = self._get_credentials(user_id)
        if not creds:
            return None
        service = build_gmail_service(credentials=creds)
        return GmailToolkit(api_resource=service)

    def set_keep_credentials(self, user_id: str, email: str, token: str) -> None:
        self.collection.update_one({'_id': user_id}, {
            '$set': {'keep_email': email, 'keep_token': token}
        }, upsert=True)

    def list_keep_notes(self, user_id: str, num: int = 5) -> str:
        doc = self.collection.find_one({'_id': user_id})
        if not doc or 'keep_email' not in doc or 'keep_token' not in doc:
            return 'Please authorize Keep using /keep_auth <email> <token>.'
        import gkeepapi
        keep = gkeepapi.Keep()
        if not keep.authenticate(doc['keep_email'], doc['keep_token']):
            return 'Authentication failed.'
        keep.sync()
        notes = list(keep.all())[:num]
        if not notes:
            return 'No notes found.'
        return '\n'.join([n.title or '(no title)' for n in notes])

google_workspace = GoogleWorkspace()
