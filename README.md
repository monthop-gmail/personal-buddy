# Personal Buddy

Personal AI agent with persistent memory, powered by Claude API.

Buddy remembers what you tell it, manages your calendar, reads your email, and sends you reminders — all from a single chat interface.

## Features

- **Persistent memory** — remembers facts about you across sessions, with semantic search
- **Auto-summarize** — automatically summarizes conversations to build long-term context
- **Google Calendar** — view and create events ("วันนี้มีนัดอะไร", "สร้างนัดประชุมพรุ่งนี้ 10 โมง")
- **Gmail** — read and send emails ("มีเมลใหม่ไหม", "ส่งเมลหา boss@company.com")
- **Reminders** — set timed reminders via Telegram ("เตือนฉัน 5 โมงเย็น ว่าไปซื้อของ")
- **Telegram Channel for Claude Code** — two-way chat + permission relay from your phone
- **5 interfaces** — CLI, Telegram bot, Web UI, Claude Code (MCP tools), Claude Code (Telegram Channel)

## Quick Start

```bash
git clone https://github.com/monthop-gmail/personal-buddy.git
cd personal-buddy
cp .env.example .env
# Edit .env — add ANTHROPIC_API_KEY and TELEGRAM_BOT_TOKEN
```

### Claude Code (MCP integration)

No API key needed — Claude Code is the brain.

```bash
# One-time setup
./setup_claude_code.sh

# Or manually:
claude mcp add personal-buddy python3 /path/to/mcp_server.py \
  -e MEMORY_DIR="$HOME/.personal-buddy/memory"
```

Restart Claude Code, then ask naturally: "จำไว้ว่า...", "วันนี้มีนัดอะไร", "มีเมลใหม่ไหม"

### Claude Code + Telegram Channel (two-way chat)

Chat with Claude Code from your phone, with permission relay — approve/deny tool use remotely.

```bash
# Setup
export TELEGRAM_BOT_TOKEN=your-token
cd channel && ./setup.sh

# Start Claude Code with the channel
claude --dangerously-load-development-channels server:personal-buddy-telegram
```

First message to the bot auto-pairs your Telegram ID. After that:
- Send any message → Claude Code receives and responds via Telegram
- When Claude needs permission → you get a prompt on Telegram, reply `yes <id>` or `no <id>`

### Telegram bot (recommended for standalone)

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
| `ALLOWED_TELEGRAM_IDS` | (auto-pair) | Comma-separated Telegram user IDs for channel |

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
├── channel/
│   ├── buddy-channel.ts  # Telegram Channel for Claude Code (two-way + permission relay)
│   ├── setup.sh          # Channel setup script
│   └── package.json
├── config.py          # Settings and system prompt
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## License

MIT
