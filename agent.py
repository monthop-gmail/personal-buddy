import json
import anthropic
from memory import Memory
from config import ANTHROPIC_API_KEY, MODEL, SYSTEM_PROMPT, MAX_HISTORY

TOOLS = [
    {
        "name": "save_memory",
        "description": "บันทึกข้อมูลลง memory เมื่อผู้ใช้บอกให้จำ หรือเมื่อมีข้อมูลสำคัญที่ควรจำ",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "สิ่งที่ต้องจำ"},
                "category": {
                    "type": "string",
                    "description": "หมวดหมู่ เช่น personal, work, preference, fact",
                    "default": "general",
                },
            },
            "required": ["content"],
        },
    },
    {
        "name": "search_memory",
        "description": "ค้นหา memory ที่บันทึกไว้",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "คำค้นหา"},
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
]


class BuddyAgent:
    def __init__(self, memory: Memory):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.memory = memory
        self.history: list[dict] = []

    def _build_system(self) -> str:
        memory_context = self.memory.format_for_context()
        return f"{SYSTEM_PROMPT}\n\n## Memory ที่จำไว้:\n{memory_context}"

    def _handle_tool(self, name: str, input_data: dict) -> str:
        if name == "save_memory":
            entry = self.memory.add(input_data["content"], input_data.get("category", "general"))
            return json.dumps({"status": "saved", "id": entry["id"]}, ensure_ascii=False)
        elif name == "search_memory":
            results = self.memory.search(input_data["query"])
            return json.dumps(results, ensure_ascii=False)
        elif name == "list_memories":
            results = self.memory.get_recent(input_data.get("count", 10))
            return json.dumps(results, ensure_ascii=False)
        elif name == "delete_memory":
            ok = self.memory.delete(input_data["memory_id"])
            return json.dumps({"status": "deleted" if ok else "not_found"})
        return json.dumps({"error": "unknown tool"})

    def chat(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})

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

            # Collect tool uses and text
            if response.stop_reason == "tool_use":
                # Add assistant response to messages
                messages.append({"role": "assistant", "content": response.content})

                # Process all tool calls
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

            # Extract text response
            text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    text += block.text
            break

        # Save final exchange to history
        self.history.append({"role": "assistant", "content": text})
        return text
