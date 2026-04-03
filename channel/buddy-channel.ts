#!/usr/bin/env bun
/**
 * Personal Buddy — Telegram Channel for Claude Code
 *
 * Bridges Telegram messages into a Claude Code session so you can
 * chat with your personal buddy from your phone. Supports:
 * - Two-way chat (reply tool)
 * - Permission relay (approve/deny tool use from Telegram)
 * - Sender gating (allowlist by Telegram user ID)
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";

// --- Config ---
const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
if (!BOT_TOKEN) {
  console.error("❌ TELEGRAM_BOT_TOKEN is required");
  process.exit(1);
}

const TELEGRAM_API = `https://api.telegram.org/bot${BOT_TOKEN}`;

// Allowed sender IDs — comma-separated in env, or empty to allow first user (pairing mode)
const allowedRaw = process.env.ALLOWED_TELEGRAM_IDS ?? "";
const allowed = new Set<number>(
  allowedRaw
    .split(",")
    .map((s) => parseInt(s.trim(), 10))
    .filter((n) => !isNaN(n))
);
let pairingMode = allowed.size === 0;

// --- Telegram API helpers ---
async function tgCall(method: string, body: Record<string, unknown>) {
  const res = await fetch(`${TELEGRAM_API}/${method}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return res.json() as Promise<{ ok: boolean; result: unknown }>;
}

async function sendMessage(chatId: number, text: string) {
  await tgCall("sendMessage", {
    chat_id: chatId,
    text,
    parse_mode: "Markdown",
  });
}

async function sendTyping(chatId: number) {
  await tgCall("sendChatAction", { chat_id: chatId, action: "typing" });
}

// --- MCP Server ---
const mcp = new Server(
  { name: "personal-buddy-telegram", version: "0.1.0" },
  {
    capabilities: {
      experimental: {
        "claude/channel": {},
        "claude/channel/permission": {}, // permission relay
      },
      tools: {}, // reply tool
    },
    instructions: `Messages arrive as <channel source="personal-buddy-telegram" chat_id="..." sender="...">.
These are from the user's Telegram. You are their personal buddy.
Reply using the reply tool, passing the chat_id from the tag.
Keep replies concise and friendly — this is a mobile chat.
Use the same language as the sender.
If the message asks you to remember something, use save_memory.
If it asks about calendar/email, use the appropriate MCP tools.`,
  }
);

// --- Reply tool ---
mcp.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "reply",
      description:
        "Send a reply back to the user on Telegram. Always use this to respond to channel messages.",
      inputSchema: {
        type: "object" as const,
        properties: {
          chat_id: {
            type: "string",
            description: "The Telegram chat ID from the channel tag",
          },
          text: {
            type: "string",
            description: "The message to send back",
          },
        },
        required: ["chat_id", "text"],
      },
    },
  ],
}));

mcp.setRequestHandler(CallToolRequestSchema, async (req) => {
  if (req.params.name === "reply") {
    const { chat_id, text } = req.params.arguments as {
      chat_id: string;
      text: string;
    };
    await sendMessage(parseInt(chat_id, 10), text);
    return { content: [{ type: "text" as const, text: "sent" }] };
  }
  throw new Error(`unknown tool: ${req.params.name}`);
});

// --- Permission relay ---
const PermissionRequestSchema = z.object({
  method: z.literal("notifications/claude/channel/permission_request"),
  params: z.object({
    request_id: z.string(),
    tool_name: z.string(),
    description: z.string(),
    input_preview: z.string(),
  }),
});

// Track which chat to send permission prompts to
let lastActiveChatId: number | null = null;

mcp.setNotificationHandler(PermissionRequestSchema, async ({ params }) => {
  if (!lastActiveChatId) return;

  const msg =
    `🔐 *Permission Request*\n\n` +
    `Tool: \`${params.tool_name}\`\n` +
    `Action: ${params.description}\n\n` +
    `Reply \`yes ${params.request_id}\` or \`no ${params.request_id}\``;

  await sendMessage(lastActiveChatId, msg);
});

// --- Connect to Claude Code ---
await mcp.connect(new StdioServerTransport());

// --- Telegram polling ---
const PERMISSION_REPLY_RE = /^\s*(y|yes|n|no)\s+([a-km-z]{5})\s*$/i;
let offset = 0;

async function poll() {
  while (true) {
    try {
      const res = (await tgCall("getUpdates", {
        offset,
        timeout: 30,
        allowed_updates: ["message"],
      })) as { ok: boolean; result: TgUpdate[] };

      if (!res.ok || !res.result) continue;

      for (const update of res.result) {
        offset = update.update_id + 1;
        const msg = update.message;
        if (!msg?.text) continue;

        const senderId = msg.from?.id;
        const chatId = msg.chat.id;
        const senderName =
          msg.from?.first_name ?? msg.from?.username ?? "unknown";

        // --- Pairing mode: first user gets added ---
        if (pairingMode && senderId) {
          allowed.add(senderId);
          pairingMode = false;
          await sendMessage(
            chatId,
            `✅ Paired! Your Telegram ID (${senderId}) is now allowed.\n` +
              `Set \`ALLOWED_TELEGRAM_IDS=${senderId}\` to skip pairing next time.`
          );
          continue;
        }

        // --- Sender gate ---
        if (!senderId || !allowed.has(senderId)) {
          await sendMessage(chatId, "⛔ You are not authorized.");
          continue;
        }

        lastActiveChatId = chatId;

        // --- Permission verdict ---
        const m = PERMISSION_REPLY_RE.exec(msg.text);
        if (m) {
          await mcp.notification({
            method: "notifications/claude/channel/permission" as any,
            params: {
              request_id: m[2].toLowerCase(),
              behavior: m[1].toLowerCase().startsWith("y") ? "allow" : "deny",
            },
          });
          await sendMessage(
            chatId,
            m[1].toLowerCase().startsWith("y") ? "✅ Allowed" : "❌ Denied"
          );
          continue;
        }

        // --- Normal message: forward to Claude Code ---
        await sendTyping(chatId);
        await mcp.notification({
          method: "notifications/claude/channel",
          params: {
            content: msg.text,
            meta: {
              chat_id: String(chatId),
              sender: senderName,
              sender_id: String(senderId),
            },
          },
        });
      }
    } catch (err) {
      // Network hiccup — wait and retry
      await new Promise((r) => setTimeout(r, 3000));
    }
  }
}

// Start polling
poll();

// --- Types ---
interface TgUpdate {
  update_id: number;
  message?: {
    text?: string;
    chat: { id: number };
    from?: { id: number; first_name?: string; username?: string };
  };
}
