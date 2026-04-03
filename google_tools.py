"""Google Calendar + Gmail integration."""

import os
import json
import pickle
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.modify",
]

from config import MEMORY_DIR, GOOGLE_CREDENTIALS_FILE

TOKEN_DIR = MEMORY_DIR
CREDENTIALS_FILE = GOOGLE_CREDENTIALS_FILE


def _get_creds():
    token_path = os.path.join(TOKEN_DIR, "google_token.pickle")
    creds = None

    if os.path.exists(token_path):
        with open(token_path, "rb") as f:
            creds = pickle.load(f)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, "wb") as f:
            pickle.dump(creds, f)

    if not creds or not creds.valid:
        if not os.path.exists(CREDENTIALS_FILE):
            return None
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(token_path, "wb") as f:
            pickle.dump(creds, f)

    return creds


def _calendar_service():
    creds = _get_creds()
    if not creds:
        return None
    return build("calendar", "v3", credentials=creds)


def _gmail_service():
    creds = _get_creds()
    if not creds:
        return None
    return build("gmail", "v1", credentials=creds)


# --- Calendar ---

def list_events(days: int = 1) -> str:
    service = _calendar_service()
    if not service:
        return json.dumps({"error": "Google credentials not configured"})

    now = datetime.utcnow()
    time_min = now.isoformat() + "Z"
    time_max = (now + timedelta(days=days)).isoformat() + "Z"

    result = service.events().list(
        calendarId="primary",
        timeMin=time_min,
        timeMax=time_max,
        maxResults=20,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = result.get("items", [])
    if not events:
        return json.dumps({"events": [], "message": f"ไม่มีนัดในอีก {days} วัน"}, ensure_ascii=False)

    items = []
    for e in events:
        start = e["start"].get("dateTime", e["start"].get("date"))
        items.append({
            "title": e.get("summary", "(ไม่มีชื่อ)"),
            "start": start,
            "location": e.get("location", ""),
            "description": e.get("description", "")[:200],
        })
    return json.dumps({"events": items}, ensure_ascii=False)


def create_event(title: str, start_time: str, end_time: str, description: str = "") -> str:
    service = _calendar_service()
    if not service:
        return json.dumps({"error": "Google credentials not configured"})

    event = {
        "summary": title,
        "start": {"dateTime": start_time, "timeZone": "Asia/Bangkok"},
        "end": {"dateTime": end_time, "timeZone": "Asia/Bangkok"},
    }
    if description:
        event["description"] = description

    created = service.events().insert(calendarId="primary", body=event).execute()
    return json.dumps({
        "status": "created",
        "id": created["id"],
        "link": created.get("htmlLink", ""),
    }, ensure_ascii=False)


# --- Gmail ---

def list_emails(max_results: int = 5, query: str = "is:unread") -> str:
    service = _gmail_service()
    if not service:
        return json.dumps({"error": "Google credentials not configured"})

    result = service.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()

    messages = result.get("messages", [])
    if not messages:
        return json.dumps({"emails": [], "message": "ไม่มีอีเมล"}, ensure_ascii=False)

    emails = []
    for msg_ref in messages:
        msg = service.users().messages().get(
            userId="me", id=msg_ref["id"], format="metadata",
            metadataHeaders=["Subject", "From", "Date"],
        ).execute()

        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
        emails.append({
            "id": msg["id"],
            "subject": headers.get("Subject", "(ไม่มีหัวข้อ)"),
            "from": headers.get("From", ""),
            "date": headers.get("Date", ""),
            "snippet": msg.get("snippet", ""),
        })

    return json.dumps({"emails": emails}, ensure_ascii=False)


def send_email(to: str, subject: str, body: str) -> str:
    import base64
    from email.mime.text import MIMEText

    service = _gmail_service()
    if not service:
        return json.dumps({"error": "Google credentials not configured"})

    message = MIMEText(body, "plain", "utf-8")
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    sent = service.users().messages().send(
        userId="me", body={"raw": raw}
    ).execute()

    return json.dumps({"status": "sent", "id": sent["id"]}, ensure_ascii=False)
