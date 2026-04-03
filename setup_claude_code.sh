#!/bin/bash
# Setup Personal Buddy as MCP server for Claude Code
# No API key needed — Claude Code is the brain

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MEMORY_DIR="${HOME}/.personal-buddy/memory"

echo "🔧 Setting up Personal Buddy MCP server for Claude Code..."

# Create memory directory
mkdir -p "$MEMORY_DIR"

# Add to Claude Code settings
claude mcp add personal-buddy \
  python3 "${SCRIPT_DIR}/mcp_server.py" \
  -e MEMORY_DIR="$MEMORY_DIR"

echo ""
echo "✅ Done! Restart Claude Code, then try:"
echo ""
echo '   "จำไว้ว่าฉันชอบกาแฟเย็น"'
echo '   "ค้นหา memory เรื่องกาแฟ"'
echo '   "วันนี้มีนัดอะไร"'
echo '   "เตือนฉัน 5 โมงเย็น ว่าประชุม"'
