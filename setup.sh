#!/bin/bash
# Setup Personal Buddy for Claude Code
# Installs MCP tools + official Telegram & fakechat channel plugins

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MEMORY_DIR="${HOME}/.personal-buddy/memory"

echo "🔧 Setting up Personal Buddy for Claude Code..."
echo ""

# Create memory directory
mkdir -p "$MEMORY_DIR"

# Install Python deps for MCP tools (if not in a venv)
echo "📦 Installing Python dependencies..."
pip3 install --break-system-packages -q google-api-python-client google-auth-oauthlib 2>/dev/null || \
pip3 install -q google-api-python-client google-auth-oauthlib 2>/dev/null || true

# Add MCP tools server
echo "🔌 Adding MCP tools server..."
claude mcp add personal-buddy \
  python3 "${SCRIPT_DIR}/mcp_server.py" \
  -e MEMORY_DIR="$MEMORY_DIR"

# Install official plugins
echo "📱 Installing official channel plugins..."
echo "   Run these inside Claude Code:"
echo ""
echo "   /plugin install telegram@claude-plugins-official"
echo "   /plugin install fakechat@claude-plugins-official"
echo "   /reload-plugins"
echo ""

# Configure Telegram if token is set
if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
  echo "   Then configure Telegram:"
  echo "   /telegram:configure $TELEGRAM_BOT_TOKEN"
  echo ""
fi

echo "🚀 Start Claude Code with channels:"
echo ""
echo "   # Telegram only"
echo "   claude --channels plugin:telegram@claude-plugins-official"
echo ""
echo "   # Fakechat (web UI on localhost:8787)"
echo "   claude --channels plugin:fakechat@claude-plugins-official"
echo ""
echo "   # Both"
echo "   claude --channels plugin:telegram@claude-plugins-official plugin:fakechat@claude-plugins-official"
echo ""
echo "✅ Done!"
