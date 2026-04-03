#!/usr/bin/env python3
"""Personal Buddy — CLI chat with persistent memory."""

from config import MEMORY_DIR, BUDDY_NAME, ANTHROPIC_API_KEY
from memory import Memory
from agent import BuddyAgent


def main():
    if not ANTHROPIC_API_KEY:
        print("❌ ตั้งค่า ANTHROPIC_API_KEY ก่อนนะ")
        print("   export ANTHROPIC_API_KEY=sk-ant-...")
        return

    memory = Memory(MEMORY_DIR)
    agent = BuddyAgent(memory)

    print(f"🤖 {BUDDY_NAME} พร้อมแล้ว! (พิมพ์ 'quit' เพื่อออก)")
    print(f"📝 Memory: {len(memory.get_all())} รายการ")
    print("-" * 40)

    while True:
        try:
            user_input = input("\nคุณ: ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n👋 {BUDDY_NAME} บ๊ายบาย!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "bye"):
            print(f"👋 {BUDDY_NAME} บ๊ายบาย!")
            break

        response = agent.chat(user_input)
        print(f"\n{BUDDY_NAME}: {response}")


if __name__ == "__main__":
    main()
