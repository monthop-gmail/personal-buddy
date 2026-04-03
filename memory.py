import json
import os
from datetime import datetime

import anthropic
from config import ANTHROPIC_API_KEY, MODEL


class Memory:
    """Persistent memory store — the 'Soul' of the buddy."""

    def __init__(self, memory_dir: str):
        self.memory_dir = memory_dir
        self.memories_file = os.path.join(memory_dir, "memories.json")
        self.summaries_file = os.path.join(memory_dir, "summaries.json")
        os.makedirs(memory_dir, exist_ok=True)
        self.memories: list[dict] = self._load(self.memories_file)
        self.summaries: list[dict] = self._load(self.summaries_file)
        self._client = None

    @property
    def client(self) -> anthropic.Anthropic:
        if self._client is None:
            self._client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        return self._client

    def _load(self, path: str) -> list[dict]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save_memories(self):
        with open(self.memories_file, "w", encoding="utf-8") as f:
            json.dump(self.memories, f, ensure_ascii=False, indent=2)

    def _save_summaries(self):
        with open(self.summaries_file, "w", encoding="utf-8") as f:
            json.dump(self.summaries, f, ensure_ascii=False, indent=2)

    def _next_id(self) -> int:
        if not self.memories:
            return 1
        return max(m["id"] for m in self.memories) + 1

    def add(self, content: str, category: str = "general") -> dict:
        entry = {
            "id": self._next_id(),
            "content": content,
            "category": category,
            "created_at": datetime.now().isoformat(),
        }
        self.memories.append(entry)
        self._save_memories()
        return entry

    def search(self, query: str) -> list[dict]:
        """Keyword search."""
        query_lower = query.lower()
        return [m for m in self.memories if query_lower in m["content"].lower()]

    def semantic_search(self, query: str, top_k: int = 5) -> list[dict]:
        """Use Claude to find semantically relevant memories."""
        if not self.memories:
            return []

        # For small memory sets, keyword is enough
        if len(self.memories) <= 10:
            keyword_results = self.search(query)
            if keyword_results:
                return keyword_results
            # Fall through to semantic if keyword found nothing

        memories_text = "\n".join(
            f"[ID:{m['id']}] [{m['category']}] {m['content']}"
            for m in self.memories
        )

        response = self.client.messages.create(
            model=MODEL,
            max_tokens=256,
            system="คุณเป็นระบบค้นหา memory ตอบเฉพาะ ID ที่เกี่ยวข้อง คั่นด้วยจุลภาค ถ้าไม่มีที่เกี่ยวข้องตอบ NONE",
            messages=[{
                "role": "user",
                "content": f"Query: {query}\n\nMemories:\n{memories_text}\n\nตอบเฉพาะ ID ที่เกี่ยวข้อง (เช่น 1,3,5):"
            }],
        )

        result_text = response.content[0].text.strip()
        if result_text == "NONE":
            return []

        try:
            ids = [int(x.strip()) for x in result_text.split(",") if x.strip().isdigit()]
        except ValueError:
            return []

        return [m for m in self.memories if m["id"] in ids][:top_k]

    def get_all(self) -> list[dict]:
        return self.memories

    def get_recent(self, n: int = 10) -> list[dict]:
        return self.memories[-n:]

    def delete(self, memory_id: int) -> bool:
        for i, m in enumerate(self.memories):
            if m["id"] == memory_id:
                self.memories.pop(i)
                self._save_memories()
                return True
        return False

    def add_summary(self, summary: str) -> dict:
        entry = {
            "id": len(self.summaries) + 1,
            "summary": summary,
            "created_at": datetime.now().isoformat(),
        }
        self.summaries.append(entry)
        self._save_summaries()
        return entry

    def format_for_context(self) -> str:
        parts = []

        if self.memories:
            lines = []
            for m in self.memories:
                lines.append(f"- #{m['id']} [{m['category']}] {m['content']} ({m['created_at'][:10]})")
            parts.append("### Memories\n" + "\n".join(lines))

        if self.summaries:
            recent = self.summaries[-5:]
            lines = [f"- {s['summary']} ({s['created_at'][:10]})" for s in recent]
            parts.append("### สรุปบทสนทนาที่ผ่านมา\n" + "\n".join(lines))

        return "\n\n".join(parts) if parts else "ยังไม่มี memory ที่บันทึกไว้"
