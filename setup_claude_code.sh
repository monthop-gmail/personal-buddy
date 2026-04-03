#!/bin/bash
# Setup Personal Buddy as MCP server for Claude Code

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🔧 Setting up Personal Buddy MCP server for Claude Code..."

# Create memory directory
mkdir -p ~/.personal-buddy/memory

# Add to Claude Code settings
claude mcp add personal-buddy \
  python3 "${SCRIPT_DIR}/mcp_server.py" \
  -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
  -e MEMORY_DIR="${HOME}/.personal-buddy/memory"

echo ""
echo "✅ Done! Personal Buddy is now available in Claude Code."
echo ""
echo "📝 Tools available:"
echo "   • save_memory / search_memory / list_memories / delete_memory"
echo "   • list_calendar_events / create_calendar_event"
echo "   • list_emails / send_email"
echo "   • set_reminder / list_reminders / delete_reminder"
echo ""
echo "💡 Try: ask Claude Code 'จำไว้ว่าฉันชอบกาแฟเย็น' or 'วันนี้มีนัดอะไร'"
