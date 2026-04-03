#!/bin/bash
# Setup Personal Buddy Telegram Channel for Claude Code

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🔧 Setting up Personal Buddy Telegram Channel..."

# Check token
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
  echo "❌ TELEGRAM_BOT_TOKEN is required"
  echo "   export TELEGRAM_BOT_TOKEN=your-token-here"
  exit 1
fi

# Install deps if needed
if [ ! -d "$SCRIPT_DIR/node_modules" ]; then
  echo "📦 Installing dependencies..."
  cd "$SCRIPT_DIR" && bun install
fi

# Memory dir
MEMORY_DIR="${HOME}/.personal-buddy/memory"
mkdir -p "$MEMORY_DIR"

# Add channel
claude mcp add personal-buddy-telegram \
  bun "${SCRIPT_DIR}/buddy-channel.ts" \
  -e TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" \
  -e ALLOWED_TELEGRAM_IDS="${ALLOWED_TELEGRAM_IDS:-}"

# Also add MCP tools if not already added
claude mcp add personal-buddy \
  python3 "${PROJECT_DIR}/mcp_server.py" \
  -e MEMORY_DIR="$MEMORY_DIR" 2>/dev/null || true

echo ""
echo "✅ Done! Start Claude Code with:"
echo ""
echo "   claude --dangerously-load-development-channels server:personal-buddy-telegram"
echo ""
echo "📱 Then send a message to your Telegram bot."
echo "   First message will pair your Telegram ID automatically."
echo ""
echo "🔐 Permission relay is enabled — approve/deny tool use from Telegram."
