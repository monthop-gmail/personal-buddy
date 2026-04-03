# Personal Buddy

Personal AI assistant for Claude Code — memory, Google Calendar, Gmail, and reminders.

Uses Claude Code as the brain with MCP tools for persistence, and official channel plugins for Telegram and web chat.

## Features

- **Persistent memory** — remembers facts about you across sessions
- **Google Calendar** — view and create events
- **Gmail** — read and send emails
- **Reminders** — set timed reminders
- **Telegram** — chat with Claude Code from your phone (official plugin)
- **Web chat** — localhost chat UI via fakechat (official plugin)
- **Permission relay** — approve/deny tool use from Telegram

## Quick Start

```bash
git clone https://github.com/monthop-gmail/personal-buddy.git
cd personal-buddy
./setup.sh
```

### 1. Install plugins (inside Claude Code)

```
/plugin install telegram@claude-plugins-official
/plugin install fakechat@claude-plugins-official
/reload-plugins
/telegram:configure <your-bot-token>
```

### 2. Start with channels

```bash
# Telegram
claude --channels plugin:telegram@claude-plugins-official

# Web chat (localhost:8787)
claude --channels plugin:fakechat@claude-plugins-official

# Both
claude --channels plugin:telegram@claude-plugins-official plugin:fakechat@claude-plugins-official
```

### 3. Pair Telegram

1. Send any message to your bot on Telegram
2. Bot replies with a pairing code
3. In Claude Code: `/telegram:access pair <code>`
4. Lock down: `/telegram:access policy allowlist`

## Google Calendar & Gmail Setup

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable **Calendar API** and **Gmail API**
3. Create **OAuth 2.0 credentials** (Desktop app)
4. Download as `credentials.json` to `~/.personal-buddy/`
5. First use will open a browser for OAuth flow

## Architecture

```
📱 Telegram ──→ Official Telegram Plugin ──→ Claude Code session
🌐 Browser  ──→ Official Fakechat Plugin ──→ Claude Code session
                                                    │
                                              MCP Tools Server
                                              (personal-buddy)
                                                    │
                                    ┌───────────────┼───────────────┐
                                    │               │               │
                                 Memory      Google APIs      Reminders
                              (JSON files)  (Calendar/Gmail)  (JSON files)
```

Claude Code is the brain — no separate API key needed for the MCP server. The official channel plugins handle Telegram/web chat with pairing, sender gating, and permission relay built in.

## Project Structure

```
personal-buddy/
├── CLAUDE.md          # Buddy personality + behavior rules
├── mcp_server.py      # MCP tools server (memory, calendar, gmail, reminders)
├── memory.py          # Persistent JSON memory store
├── google_tools.py    # Google Calendar + Gmail integration
├── scheduler.py       # Reminder storage
├── config.py          # Settings
├── setup.sh           # One-time setup script
└── requirements.txt   # Python dependencies (mcp, google-api)
```

## License

MIT
