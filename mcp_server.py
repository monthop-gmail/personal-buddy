#!/usr/bin/env python3
"""Personal Buddy MCP Server — tools for Claude Code.

No API key needed. Claude Code is the brain.
This server provides memory, calendar, gmail, and reminder tools.
"""

import json
import os
import sys

from mcp.server.fastmcp import FastMCP

# Ensure project modules are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory import Memory
from config import MEMORY_DIR

mcp = FastMCP(
    "personal-buddy",
    instructions="Personal buddy tools: memory, Google Calendar, Gmail, reminders.",
)

_memory = Memory(MEMORY_DIR)


# --- Memory ---

@mcp.tool()
def save_memory(content: str, category: str = "general") -> str:
    """บันทึกข้อมูลลง memory (category: personal, preference, work, people, fact)"""
    entry = _memory.add(content, category)
    return json.dumps({"status": "saved", "id": entry["id"]}, ensure_ascii=False)


@mcp.tool()
def search_memory(query: str) -> str:
    """ค้นหา memory ที่บันทึกไว้"""
    results = _memory.search(query)
    if not results:
        return json.dumps({"results": [], "message": "ไม่พบ memory ที่เกี่ยวข้อง"}, ensure_ascii=False)
    return json.dumps(results, ensure_ascii=False)


@mcp.tool()
def list_memories(count: int = 10) -> str:
    """แสดง memory ล่าสุด"""
    results = _memory.get_recent(count)
    if not results:
        return json.dumps({"results": [], "message": "ยังไม่มี memory"}, ensure_ascii=False)
    return json.dumps(results, ensure_ascii=False)


@mcp.tool()
def delete_memory(memory_id: int) -> str:
    """ลบ memory ตาม ID"""
    ok = _memory.delete(memory_id)
    return json.dumps({"status": "deleted" if ok else "not_found"})


# --- Google Calendar ---

@mcp.tool()
def list_calendar_events(days: int = 1) -> str:
    """ดูนัดหมายจาก Google Calendar"""
    from google_tools import list_events
    return list_events(days)


@mcp.tool()
def create_calendar_event(title: str, start_time: str, end_time: str, description: str = "") -> str:
    """สร้างนัดหมายใน Google Calendar (เวลา ISO format เช่น 2026-04-04T10:00:00)"""
    from google_tools import create_event
    return create_event(title, start_time, end_time, description)


# --- Gmail ---

@mcp.tool()
def list_emails(max_results: int = 5, query: str = "is:unread") -> str:
    """ดูอีเมลจาก Gmail"""
    from google_tools import list_emails as _list
    return _list(max_results, query)


@mcp.tool()
def send_email(to: str, subject: str, body: str) -> str:
    """ส่งอีเมลผ่าน Gmail"""
    from google_tools import send_email as _send
    return _send(to, subject, body)


# --- Reminders ---

@mcp.tool()
def set_reminder(message: str, remind_at: str) -> str:
    """ตั้งเตือนความจำ (remind_at ISO format เช่น 2026-04-04T09:00:00)"""
    from scheduler import add_reminder
    entry = add_reminder(message, remind_at)
    return json.dumps({"status": "set", "id": entry["id"], "remind_at": entry["remind_at"]}, ensure_ascii=False)


@mcp.tool()
def check_reminders() -> str:
    """เช็ค reminder ที่ถึงเวลาแล้ว"""
    from scheduler import get_due_reminders
    due = get_due_reminders()
    if not due:
        return json.dumps({"due": [], "message": "ไม่มี reminder ที่ถึงเวลา"}, ensure_ascii=False)
    return json.dumps({"due": due}, ensure_ascii=False)


@mcp.tool()
def list_reminders() -> str:
    """แสดง reminder ที่ยังไม่ถึงเวลา"""
    from scheduler import list_pending
    return json.dumps(list_pending(), ensure_ascii=False)


@mcp.tool()
def delete_reminder(reminder_id: int) -> str:
    """ลบ reminder ตาม ID"""
    from scheduler import delete_reminder as _del
    ok = _del(reminder_id)
    return json.dumps({"status": "deleted" if ok else "not_found"})


if __name__ == "__main__":
    mcp.run()
