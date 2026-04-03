#!/usr/bin/env python3
"""MCP Server — exposes Personal Buddy tools to Claude Code.

No ANTHROPIC_API_KEY needed — Claude Code is the brain.
"""

import json
import os
import sys

from mcp.server.fastmcp import FastMCP

# Ensure project modules are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

MEMORY_DIR = os.getenv("MEMORY_DIR", os.path.expanduser("~/.personal-buddy/memory"))

# Lightweight memory that doesn't import anthropic
from memory import Memory

mcp = FastMCP("personal-buddy", instructions="Personal AI buddy — memory, calendar, gmail, reminders")

# Shared memory instance
_memory = Memory(MEMORY_DIR)


# --- Memory Tools ---

@mcp.tool()
def save_memory(content: str, category: str = "general") -> str:
    """บันทึกข้อมูลลง memory (หมวดหมู่: personal, work, preference, fact)"""
    entry = _memory.add(content, category)
    return json.dumps({"status": "saved", "id": entry["id"]}, ensure_ascii=False)


@mcp.tool()
def search_memory(query: str) -> str:
    """ค้นหา memory ที่บันทึกไว้ (keyword search — Claude Code ทำ semantic reasoning เอง)"""
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


# --- Google Calendar Tools ---

@mcp.tool()
def list_calendar_events(days: int = 1) -> str:
    """ดูนัดหมายจาก Google Calendar (ดูล่วงหน้ากี่วัน)"""
    from google_tools import list_events
    return list_events(days)


@mcp.tool()
def create_calendar_event(title: str, start_time: str, end_time: str, description: str = "") -> str:
    """สร้างนัดหมายใหม่ใน Google Calendar (เวลาเป็น ISO format เช่น 2026-04-04T10:00:00)"""
    from google_tools import create_event
    return create_event(title, start_time, end_time, description)


# --- Gmail Tools ---

@mcp.tool()
def list_emails(max_results: int = 5, query: str = "is:unread") -> str:
    """ดูอีเมลจาก Gmail (query เช่น 'is:unread', 'from:boss@company.com')"""
    from google_tools import list_emails as _list
    return _list(max_results, query)


@mcp.tool()
def send_email(to: str, subject: str, body: str) -> str:
    """ส่งอีเมลผ่าน Gmail"""
    from google_tools import send_email as _send
    return _send(to, subject, body)


# --- Reminder Tools ---

@mcp.tool()
def set_reminder(message: str, remind_at: str) -> str:
    """ตั้งเตือนความจำ (remind_at เป็น ISO format เช่น 2026-04-04T09:00:00)"""
    from scheduler import add_reminder
    entry = add_reminder(0, message, remind_at)
    return json.dumps({"status": "set", "id": entry["id"], "remind_at": entry["remind_at"]}, ensure_ascii=False)


@mcp.tool()
def list_reminders() -> str:
    """แสดงรายการเตือนความจำที่ยังไม่ถึงเวลา"""
    from scheduler import list_reminders as _list
    return json.dumps(_list(0), ensure_ascii=False)


@mcp.tool()
def delete_reminder(reminder_id: int) -> str:
    """ลบเตือนความจำตาม ID"""
    from scheduler import delete_reminder as _del
    ok = _del(reminder_id)
    return json.dumps({"status": "deleted" if ok else "not_found"})


if __name__ == "__main__":
    mcp.run()
