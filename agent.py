import json
import anthropic
from memory import Memory
from config import ANTHROPIC_API_KEY, MODEL, SYSTEM_PROMPT, MAX_HISTORY, AUTO_SUMMARIZE_EVERY

TOOLS = [
    # --- Memory ---
    {
        "name": "save_memory",
        "description": "บันทึกข้อมูลลง memory เมื่อผู้ใช้บอกให้จำ หรือเมื่อมีข้อมูลสำคัญที่ควรจำ",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "สิ่งที่ต้องจำ"},
                "category": {
                    "type": "string",
                    "description": "หมวดหมู่: personal, work, preference, fact",
                    "default": "general",
                },
            },
            "required": ["content"],
        },
    },
    {
        "name": "search_memory",
        "description": "ค้นหา memory ที่บันทึกไว้ (semantic search — ค้นหาตามความหมายได้)",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "คำค้นหา หรือคำถามที่ต้องการค้น"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "list_memories",
        "description": "แสดง memory ล่าสุดทั้งหมด",
        "input_schema": {
            "type": "object",
            "properties": {
                "count": {"type": "integer", "description": "จำนวนที่ต้องการ", "default": 10},
            },
        },
    },
    {
        "name": "delete_memory",
        "description": "ลบ memory ตาม ID",
        "input_schema": {
            "type": "object",
            "properties": {
                "memory_id": {"type": "integer", "description": "ID ของ memory ที่ต้องการลบ"},
            },
            "required": ["memory_id"],
        },
    },
    # --- Google Calendar ---
    {
        "name": "list_calendar_events",
        "description": "ดูนัดหมายจาก Google Calendar (เช่น วันนี้มีนัดอะไร, สัปดาห์นี้มีอะไรบ้าง)",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "description": "ดูล่วงหน้ากี่วัน (default: 1)", "default": 1},
            },
        },
    },
    {
        "name": "create_calendar_event",
        "description": "สร้างนัดหมายใหม่ใน Google Calendar",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "ชื่อนัดหมาย"},
                "start_time": {"type": "string", "description": "เวลาเริ่ม ISO format เช่น 2026-04-04T10:00:00"},
                "end_time": {"type": "string", "description": "เวลาจบ ISO format เช่น 2026-04-04T11:00:00"},
                "description": {"type": "string", "description": "รายละเอียด", "default": ""},
            },
            "required": ["title", "start_time", "end_time"],
        },
    },
    # --- Gmail ---
    {
        "name": "list_emails",
        "description": "ดูอีเมลจาก Gmail (เช่น มีเมลใหม่ไหม, เมลจากใคร)",
        "input_schema": {
            "type": "object",
            "properties": {
                "max_results": {"type": "integer", "description": "จำนวนอีเมล", "default": 5},
                "query": {"type": "string", "description": "Gmail search query เช่น 'is:unread', 'from:boss@company.com'", "default": "is:unread"},
            },
        },
    },
    {
        "name": "send_email",
        "description": "ส่งอีเมลผ่าน Gmail",
        "input_schema": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "อีเมลผู้รับ"},
                "subject": {"type": "string", "description": "หัวข้อ"},
                "body": {"type": "string", "description": "เนื้อหา"},
            },
            "required": ["to", "subject", "body"],
        },
    },
    # --- Reminders ---
    {
        "name": "set_reminder",
        "description": "ตั้งเตือนความจำ ส่งข้อความเตือนเมื่อถึงเวลา",
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "ข้อความเตือน"},
                "remind_at": {"type": "string", "description": "เวลาเตือน ISO format เช่น 2026-04-04T09:00:00"},
            },
            "required": ["message", "remind_at"],
        },
    },
    {
        "name": "list_reminders",
        "description": "แสดงรายการเตือนความจำที่ยังไม่ถึงเวลา",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "delete_reminder",
        "description": "ลบเตือนความจำตาม ID",
        "input_schema": {
            "type": "object",
            "properties": {
                "reminder_id": {"type": "integer", "description": "ID ของ reminder"},
            },
            "required": ["reminder_id"],
        },
    },
]


class BuddyAgent:
    def __init__(self, memory: Memory, chat_id: int = 0):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.memory = memory
        self.chat_id = chat_id
        self.history: list[dict] = []
        self._message_count = 0

    def _build_system(self) -> str:
        memory_context = self.memory.format_for_context()
        return f"{SYSTEM_PROMPT}\n\n## Memory ที่จำไว้:\n{memory_context}"

    def _handle_tool(self, name: str, input_data: dict) -> str:
        # Memory tools
        if name == "save_memory":
            entry = self.memory.add(input_data["content"], input_data.get("category", "general"))
            return json.dumps({"status": "saved", "id": entry["id"]}, ensure_ascii=False)
        elif name == "search_memory":
            results = self.memory.semantic_search(input_data["query"])
            return json.dumps(results, ensure_ascii=False)
        elif name == "list_memories":
            results = self.memory.get_recent(input_data.get("count", 10))
            return json.dumps(results, ensure_ascii=False)
        elif name == "delete_memory":
            ok = self.memory.delete(input_data["memory_id"])
            return json.dumps({"status": "deleted" if ok else "not_found"})

        # Google Calendar tools
        elif name == "list_calendar_events":
            from google_tools import list_events
            return list_events(input_data.get("days", 1))
        elif name == "create_calendar_event":
            from google_tools import create_event
            return create_event(
                input_data["title"],
                input_data["start_time"],
                input_data["end_time"],
                input_data.get("description", ""),
            )

        # Gmail tools
        elif name == "list_emails":
            from google_tools import list_emails
            return list_emails(input_data.get("max_results", 5), input_data.get("query", "is:unread"))
        elif name == "send_email":
            from google_tools import send_email
            return send_email(input_data["to"], input_data["subject"], input_data["body"])

        # Reminder tools
        elif name == "set_reminder":
            from scheduler import add_reminder
            entry = add_reminder(self.chat_id, input_data["message"], input_data["remind_at"])
            return json.dumps({"status": "set", "id": entry["id"], "remind_at": entry["remind_at"]}, ensure_ascii=False)
        elif name == "list_reminders":
            from scheduler import list_reminders
            return json.dumps(list_reminders(self.chat_id), ensure_ascii=False)
        elif name == "delete_reminder":
            from scheduler import delete_reminder
            ok = delete_reminder(input_data["reminder_id"])
            return json.dumps({"status": "deleted" if ok else "not_found"})

        return json.dumps({"error": "unknown tool"})

    def _auto_summarize(self):
        """Summarize conversation and store as memory."""
        if len(self.history) < 6:
            return

        # Take last N exchanges to summarize
        recent = self.history[-6:]
        convo_text = ""
        for msg in recent:
            role = "User" if msg["role"] == "user" else "Buddy"
            content = msg["content"] if isinstance(msg["content"], str) else str(msg["content"])
            convo_text += f"{role}: {content}\n"

        response = self.client.messages.create(
            model=MODEL,
            max_tokens=200,
            system="สรุปบทสนทนานี้ใน 1-2 ประโยค เน้นข้อมูลสำคัญเกี่ยวกับผู้ใช้ ใช้ภาษาเดียวกับบทสนทนา",
            messages=[{"role": "user", "content": convo_text}],
        )
        summary = response.content[0].text.strip()
        self.memory.add_summary(summary)

    def chat(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})
        self._message_count += 1

        # Trim history
        if len(self.history) > MAX_HISTORY:
            self.history = self.history[-MAX_HISTORY:]

        messages = list(self.history)

        while True:
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=1024,
                system=self._build_system(),
                tools=TOOLS,
                messages=messages,
            )

            if response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = self._handle_tool(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })
                messages.append({"role": "user", "content": tool_results})
                continue

            text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    text += block.text
            break

        self.history.append({"role": "assistant", "content": text})

        # Auto-summarize every N messages
        if self._message_count % AUTO_SUMMARIZE_EVERY == 0:
            try:
                self._auto_summarize()
            except Exception:
                pass  # Don't break chat if summarization fails

        return text
