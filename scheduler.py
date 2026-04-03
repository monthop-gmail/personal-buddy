"""Reminder scheduler — stores reminders as JSON."""

import json
import os
from datetime import datetime

from config import MEMORY_DIR

REMINDERS_FILE = os.path.join(MEMORY_DIR, "reminders.json")


def _load() -> list[dict]:
    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save(reminders: list[dict]):
    os.makedirs(os.path.dirname(REMINDERS_FILE), exist_ok=True)
    with open(REMINDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(reminders, f, ensure_ascii=False, indent=2)


def _next_id(reminders: list[dict]) -> int:
    if not reminders:
        return 1
    return max(r["id"] for r in reminders) + 1


def add_reminder(message: str, remind_at: str) -> dict:
    """Add a reminder. remind_at should be ISO format datetime."""
    reminders = _load()
    entry = {
        "id": _next_id(reminders),
        "message": message,
        "remind_at": remind_at,
        "created_at": datetime.now().isoformat(),
        "done": False,
    }
    reminders.append(entry)
    _save(reminders)
    return entry


def get_due_reminders() -> list[dict]:
    """Get all reminders that are due and not yet done."""
    reminders = _load()
    now = datetime.now()
    due = []
    changed = False
    for r in reminders:
        if not r["done"] and datetime.fromisoformat(r["remind_at"]) <= now:
            r["done"] = True
            changed = True
            due.append(r)
    if changed:
        _save(reminders)
    return due


def list_pending() -> list[dict]:
    """List all pending reminders."""
    reminders = _load()
    return [r for r in reminders if not r["done"]]


def delete_reminder(reminder_id: int) -> bool:
    reminders = _load()
    for i, r in enumerate(reminders):
        if r["id"] == reminder_id:
            reminders.pop(i)
            _save(reminders)
            return True
    return False
