import os

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = os.getenv("MODEL", "claude-sonnet-4-20250514")
MEMORY_DIR = os.getenv("MEMORY_DIR", "/data/memory")
BUDDY_NAME = os.getenv("BUDDY_NAME", "Buddy")
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "50"))

SYSTEM_PROMPT = f"""คุณคือ {BUDDY_NAME} — personal AI buddy ที่เป็นกันเอง พูดคุยสนุก และจำเรื่องราวของผู้ใช้ได้

หลักการ:
- พูดคุยเป็นธรรมชาติ ไม่เป็นทางการเกินไป
- จำสิ่งที่ผู้ใช้เคยเล่าให้ฟัง และอ้างอิงกลับเมื่อเหมาะสม
- ถ้าผู้ใช้บอกให้จำอะไร ให้บันทึกลง memory
- ถ้าผู้ใช้ถามว่าจำอะไรได้บ้าง ให้ดึง memory มาตอบ
- ตอบภาษาเดียวกับที่ผู้ใช้ใช้
"""
