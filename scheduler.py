"""Reminder scheduler — stores reminders and checks them periodically."""

import json
import os
from datetime import datetime

REMINDERS_FILE = os.path.join(os.getenv("MEMORY_DIR", "/data/memory"), "reminders.json")


def _load() -> list[dict]:
    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save(reminders: list[dict]):
    os.makedirs(os.path.dirname(REMINDERS_FILE), exist_ok=True)
    with open(REMINDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(reminders, f, ensure_ascii=False, indent=2)


def add_reminder(chat_id: int, message: str, remind_at: str) -> dict:
    """Add a reminder. remind_at should be ISO format datetime."""
    reminders = _load()
    entry = {
        "id": len(reminders) + 1,
        "chat_id": chat_id,
        "message": message,
        "remind_at": remind_at,
        "created_at": datetime.now().isoformat(),
        "sent": False,
    }
    reminders.append(entry)
    _save(reminders)
    return entry


def get_due_reminders() -> list[dict]:
    """Get all reminders that are due and not yet sent."""
    reminders = _load()
    now = datetime.now()
    due = []
    changed = False
    for r in reminders:
        if not r["sent"] and datetime.fromisoformat(r["remind_at"]) <= now:
            r["sent"] = True
            changed = True
            due.append(r)
    if changed:
        _save(reminders)
    return due


def list_reminders(chat_id: int) -> list[dict]:
    """List pending reminders for a chat."""
    reminders = _load()
    return [r for r in reminders if r["chat_id"] == chat_id and not r["sent"]]


def delete_reminder(reminder_id: int) -> bool:
    reminders = _load()
    for i, r in enumerate(reminders):
        if r["id"] == reminder_id:
            reminders.pop(i)
            _save(reminders)
            return True
    return False
