# Personal Buddy

Personal AI agent with persistent memory, powered by Claude API.

Buddy remembers what you tell it, manages your calendar, reads your email, and sends you reminders — all from a single chat interface.

## Features

- **Persistent memory** — remembers facts about you across sessions, with semantic search
- **Auto-summarize** — automatically summarizes conversations to build long-term context
- **Google Calendar** — view and create events ("วันนี้มีนัดอะไร", "สร้างนัดประชุมพรุ่งนี้ 10 โมง")
- **Gmail** — read and send emails ("มีเมลใหม่ไหม", "ส่งเมลหา boss@company.com")
- **Reminders** — set timed reminders via Telegram ("เตือนฉัน 5 โมงเย็น ว่าไปซื้อของ")
- **4 interfaces** — CLI, Telegram bot, Web UI, Claude Code (MCP)

## Quick Start

```bash
git clone https://github.com/monthop-gmail/personal-buddy.git
cd personal-buddy
cp .env.example .env
# Edit .env — add ANTHROPIC_API_KEY and TELEGRAM_BOT_TOKEN
```

### Claude Code (MCP integration)

```bash
# One-time setup
export ANTHROPIC_API_KEY=sk-ant-...
./setup_claude_code.sh

# Or manually:
claude mcp add personal-buddy python3 /path/to/mcp_server.py \
  -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  -e MEMORY_DIR="$HOME/.personal-buddy/memory"
```

Then in Claude Code, just ask naturally: "จำไว้ว่า...", "วันนี้มีนัดอะไร", "มีเมลใหม่ไหม"

### Telegram bot (recommended)

```bash
docker compose up telegram -d
```

### Web UI

```bash
docker compose up web -d
# Open http://your-server:8080
```

### CLI

```bash
docker compose run --rm buddy
```

## Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome + help |
| `/memories` | List all saved memories |
| `/forget <id>` | Delete a memory |
| `/reminders` | List pending reminders |
| `/reset` | Clear chat history (memories persist) |

## Google Calendar & Gmail Setup

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable **Calendar API** and **Gmail API**
3. Create **OAuth 2.0 credentials** (Desktop app)
4. Download as `credentials.json` into the project root
5. Run CLI mode once to complete OAuth flow: `docker compose run --rm buddy`

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | (required) | Anthropic API key |
| `TELEGRAM_BOT_TOKEN` | (required for Telegram) | Token from @BotFather |
| `MODEL` | `claude-sonnet-4-20250514` | Claude model |
| `BUDDY_NAME` | `Buddy` | Display name |
| `MAX_HISTORY` | `50` | Conversation turns in context |
| `AUTO_SUMMARIZE_EVERY` | `10` | Summarize every N messages |
| `WEB_PORT` | `8080` | Web UI port |
| `GOOGLE_CREDENTIALS_FILE` | `/data/credentials.json` | Google OAuth credentials |

## Architecture

Inspired by the "Bones & Soul" pattern:

- **Bones** — recomputed each session (conversation history, system prompt)
- **Soul** — persistent data (memories + conversation summaries stored as JSON)

The agent uses Claude's [tool use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) to autonomously decide when to save memories, search context, call Google APIs, or set reminders.

## Project Structure

```
personal-buddy/
├── main.py            # CLI chat loop
├── telegram_bot.py    # Telegram bot + reminder scheduler
├── web.py             # FastAPI + WebSocket chat UI
├── agent.py           # Claude API client + all tool handling
├── memory.py          # Persistent memory + semantic search + auto-summarize
├── google_tools.py    # Google Calendar + Gmail integration
├── scheduler.py       # Reminder storage + due-checking
├── mcp_server.py      # MCP server for Claude Code integration
├── setup_claude_code.sh  # One-line setup script
├── config.py          # Settings and system prompt
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## License

MIT
