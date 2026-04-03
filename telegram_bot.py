#!/usr/bin/env python3
"""Telegram bot interface for Personal Buddy."""

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from config import MEMORY_DIR, BUDDY_NAME
from memory import Memory
from agent import BuddyAgent
from scheduler import get_due_reminders

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Per-chat agents (each chat gets its own memory + history)
agents: dict[int, BuddyAgent] = {}


def get_agent(chat_id: int) -> BuddyAgent:
    if chat_id not in agents:
        memory = Memory(f"{MEMORY_DIR}/{chat_id}")
        agents[chat_id] = BuddyAgent(memory, chat_id=chat_id)
    return agents[chat_id]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"สวัสดี! ฉันคือ {BUDDY_NAME} 🤖\n"
        f"คุยกับฉันได้เลย ฉันจะจำเรื่องราวของคุณไว้ข้ามเซสชัน\n\n"
        f"📝 /memories — ดู memory ที่จำไว้\n"
        f"🗑️ /forget <id> — ลบ memory ตาม ID\n"
        f"🔄 /reset — ล้างประวัติแชท\n"
        f"⏰ /reminders — ดู reminder ที่ตั้งไว้\n\n"
        f"💡 ลองพูดว่า:\n"
        f'  "เตือนฉันพรุ่งนี้ 9 โมง ว่าประชุมทีม"\n'
        f'  "วันนี้มีนัดอะไรบ้าง"\n'
        f'  "มีเมลใหม่ไหม"'
    )


async def memories_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    agent = get_agent(update.effective_chat.id)
    all_mem = agent.memory.get_all()
    if not all_mem:
        await update.message.reply_text("ยังไม่มี memory ที่บันทึกไว้")
        return
    lines = []
    for m in all_mem:
        lines.append(f"#{m['id']} [{m['category']}] {m['content']}")
    await update.message.reply_text("\n".join(lines))


async def forget_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("ใช้: /forget <id>")
        return
    try:
        mid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("ID ต้องเป็นตัวเลข")
        return
    agent = get_agent(update.effective_chat.id)
    if agent.memory.delete(mid):
        await update.message.reply_text(f"ลบ memory #{mid} แล้ว")
    else:
        await update.message.reply_text(f"ไม่พบ memory #{mid}")


async def reminders_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from scheduler import list_reminders
    chat_id = update.effective_chat.id
    pending = list_reminders(chat_id)
    if not pending:
        await update.message.reply_text("ไม่มี reminder ที่ตั้งไว้")
        return
    lines = []
    for r in pending:
        lines.append(f"#{r['id']} ⏰ {r['remind_at'][:16]} — {r['message']}")
    await update.message.reply_text("\n".join(lines))


async def reset_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in agents:
        agents[chat_id].history.clear()
    await update.message.reply_text("ล้างประวัติแชทแล้ว (memory ยังอยู่)")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    agent = get_agent(update.effective_chat.id)
    await update.effective_chat.send_action("typing")
    response = agent.chat(update.message.text)
    await update.message.reply_text(response)


async def check_reminders(context: ContextTypes.DEFAULT_TYPE):
    """Periodic job to check and send due reminders."""
    due = get_due_reminders()
    for r in due:
        try:
            await context.bot.send_message(
                chat_id=r["chat_id"],
                text=f"⏰ เตือนความจำ!\n\n{r['message']}",
            )
        except Exception as e:
            logger.error(f"Failed to send reminder #{r['id']}: {e}")


def run_bot(token: str):
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("memories", memories_cmd))
    app.add_handler(CommandHandler("forget", forget_cmd))
    app.add_handler(CommandHandler("reminders", reminders_cmd))
    app.add_handler(CommandHandler("reset", reset_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Check reminders every 30 seconds
    app.job_queue.run_repeating(check_reminders, interval=30, first=5)

    logger.info(f"{BUDDY_NAME} Telegram bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    import os
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ ตั้งค่า TELEGRAM_BOT_TOKEN ก่อนนะ")
        exit(1)
    run_bot(token)
