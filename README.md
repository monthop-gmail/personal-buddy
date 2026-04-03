# Personal Buddy

Personal AI assistant that runs inside [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

Built on Claude Code's official extension system — [CLAUDE.md](https://code.claude.com/docs/en/memory) for personality, [MCP](https://code.claude.com/docs/en/mcp) for tools, and [Channels](https://code.claude.com/docs/en/channels) for Telegram/web chat. Your buddy remembers who you are, manages your calendar, reads your email, and sends you reminders.

## How it works

Claude Code is the brain. This project adds:

- **[CLAUDE.md](https://code.claude.com/docs/en/memory)** — personality and behavior rules, loaded every session
- **[MCP tools server](https://code.claude.com/docs/en/mcp)** — persistent memory, Google Calendar, Gmail, reminders (12 tools)
- **[Official channel plugins](https://code.claude.com/docs/en/channels)** — Telegram and web chat, built and maintained by Anthropic

No separate API key needed for the tools server. Claude Code handles all the reasoning.

## Features

- **Persistent memory** — remembers facts, preferences, and people across sessions
- **Google Calendar** — view upcoming events, create new ones
- **Gmail** — read inbox, send emails (confirms before sending)
- **Reminders** — set timed reminders, check what's due
- **Telegram chat** — talk to your buddy from your phone via [official plugin](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/telegram)
- **Web chat** — localhost chat UI via [fakechat plugin](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/fakechat)
- **Permission relay** — approve/deny Claude's tool use from Telegram

## Quick Start

### 1. Setup MCP tools

```bash
git clone https://github.com/monthop-gmail/personal-buddy.git
cd personal-buddy
./setup.sh
```

### 2. Install channel plugins (inside Claude Code)

```
/plugin install telegram@claude-plugins-official
/plugin install fakechat@claude-plugins-official
/reload-plugins
/telegram:configure <your-bot-token>
```

> Get a bot token from [@BotFather](https://t.me/BotFather) on Telegram.

### 3. Start with channels

```bash
# Telegram only
claude --channels plugin:telegram@claude-plugins-official

# Web chat only (localhost:8787)
claude --channels plugin:fakechat@claude-plugins-official

# Both
claude --channels plugin:telegram@claude-plugins-official plugin:fakechat@claude-plugins-official
```

### 4. Pair Telegram

1. Send any message to your bot on Telegram
2. Bot replies with a pairing code
3. In Claude Code: `/telegram:access pair <code>`
4. Lock down: `/telegram:access policy allowlist`

Done! Chat with your buddy from Telegram or the web UI.

## MCP Tools

| Tool | Description |
|------|-------------|
| `save_memory` | Save facts, preferences, people |
| `search_memory` | Search saved memories |
| `list_memories` | Show recent memories |
| `delete_memory` | Remove a memory by ID |
| `list_calendar_events` | View upcoming Google Calendar events |
| `create_calendar_event` | Create a new calendar event |
| `list_emails` | Read emails from Gmail |
| `send_email` | Send an email via Gmail |
| `set_reminder` | Set a timed reminder |
| `check_reminders` | Check for due reminders |
| `list_reminders` | Show pending reminders |
| `delete_reminder` | Remove a reminder by ID |

## Google Calendar & Gmail Setup

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable **Calendar API** and **Gmail API**
3. Create **OAuth 2.0 credentials** (Desktop app)
4. Download as `credentials.json` to `~/.personal-buddy/`
5. First use triggers a browser OAuth flow

## Architecture

```
📱 Telegram ──→ Official Telegram Plugin ──┐
🌐 Browser  ──→ Official Fakechat Plugin ──┤
💻 Terminal ────────────────────────────────┘
                                            │
                                     Claude Code (brain)
                                            │
                                     CLAUDE.md (personality)
                                            │
                                     MCP Tools Server
                                    (personal-buddy)
                                            │
                            ┌───────────────┼───────────────┐
                            │               │               │
                         Memory      Google APIs      Reminders
                       (JSON files) (Calendar/Gmail)  (JSON files)
```

Follows the same pattern as Claude Code's built-in `/buddy` companion:

- **Recomputed each session** — CLAUDE.md personality rules, conversation context
- **Persisted across sessions** — memories, reminders (JSON files in `~/.personal-buddy/`)

The `/buddy` companion persists static data (species, rarity, stats) and regenerates personality via Claude API each session. Personal Buddy applies this same pattern: static data persists in JSON, while Claude Code recomputes behavior from CLAUDE.md every session.

## Project Structure

```
personal-buddy/
├── CLAUDE.md          # Personality rules (recomputed each session)
├── mcp_server.py      # MCP tools server (12 tools, no API key needed)
├── memory.py          # Persistent memory store (persisted across sessions)
├── google_tools.py    # Google Calendar + Gmail integration
├── scheduler.py       # Reminder storage
├── config.py          # Settings (memory dir, credentials path)
├── setup.sh           # One-time setup script
└── requirements.txt   # Python dependencies (mcp, google-api)
```

## License

MIT
