# Personal Buddy

Personal AI chat agent with persistent memory, powered by Claude API.

Buddy remembers what you tell it across sessions — your preferences, facts about you, and anything you ask it to remember.

## Features

- **Conversational chat** — natural, friendly responses in your language
- **Persistent memory** — stores and recalls information across sessions using Claude's tool use
- **Memory management** — search, list, and delete memories on demand
- **Dockerized** — runs in a container with data stored in a Docker volume

## Quick Start

```bash
# Clone
git clone https://github.com/monthop-gmail/personal-buddy.git
cd personal-buddy

# Configure
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Run
docker compose run --rm buddy
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | (required) | Your Anthropic API key |
| `MODEL` | `claude-sonnet-4-20250514` | Claude model to use |
| `BUDDY_NAME` | `Buddy` | Your buddy's display name |
| `MAX_HISTORY` | `50` | Max conversation turns to keep in context |

## Architecture

Inspired by the "Bones & Soul" pattern:

- **Bones** — recomputed each session (conversation history, system prompt)
- **Soul** — persistent data that survives restarts (memories stored as JSON in a Docker volume)

The agent uses Claude's [tool use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) to decide when to save, search, or delete memories autonomously.

## Project Structure

```
personal-buddy/
├── main.py           # CLI chat loop
├── agent.py          # Claude API client + tool handling
├── memory.py         # Persistent JSON memory store
├── config.py         # Settings and system prompt
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## License

MIT
