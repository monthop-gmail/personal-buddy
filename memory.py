import json
import os
from datetime import datetime

class Memory:
    """Persistent memory store — the 'Soul' of the buddy."""

    def __init__(self, memory_dir: str):
        self.memory_dir = memory_dir
        self.memories_file = os.path.join(memory_dir, "memories.json")
        os.makedirs(memory_dir, exist_ok=True)
        self.memories: list[dict] = self._load()

    def _load(self) -> list[dict]:
        if os.path.exists(self.memories_file):
            with open(self.memories_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save(self):
        with open(self.memories_file, "w", encoding="utf-8") as f:
            json.dump(self.memories, f, ensure_ascii=False, indent=2)

    def add(self, content: str, category: str = "general") -> dict:
        entry = {
            "id": len(self.memories) + 1,
            "content": content,
            "category": category,
            "created_at": datetime.now().isoformat(),
        }
        self.memories.append(entry)
        self._save()
        return entry

    def search(self, query: str) -> list[dict]:
        query_lower = query.lower()
        return [m for m in self.memories if query_lower in m["content"].lower()]

    def get_all(self) -> list[dict]:
        return self.memories

    def get_recent(self, n: int = 10) -> list[dict]:
        return self.memories[-n:]

    def delete(self, memory_id: int) -> bool:
        for i, m in enumerate(self.memories):
            if m["id"] == memory_id:
                self.memories.pop(i)
                self._save()
                return True
        return False

    def format_for_context(self) -> str:
        if not self.memories:
            return "ยังไม่มี memory ที่บันทึกไว้"
        lines = []
        for m in self.memories:
            lines.append(f"- [{m['category']}] {m['content']} ({m['created_at'][:10]})")
        return "\n".join(lines)
