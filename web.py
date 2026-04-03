#!/usr/bin/env python3
"""FastAPI web interface for Personal Buddy."""

import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from config import MEMORY_DIR, BUDDY_NAME, ANTHROPIC_API_KEY
from memory import Memory
from agent import BuddyAgent

app = FastAPI(title=f"{BUDDY_NAME} Web")

# Per-session agents
sessions: dict[str, BuddyAgent] = {}


def get_agent(session_id: str) -> BuddyAgent:
    if session_id not in sessions:
        memory = Memory(f"{MEMORY_DIR}/web_{session_id}")
        sessions[session_id] = BuddyAgent(memory)
    return sessions[session_id]


HTML = """<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>""" + BUDDY_NAME + """</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #0f0f0f;
    color: #e0e0e0;
    height: 100vh;
    display: flex;
    flex-direction: column;
}
.header {
    padding: 16px 20px;
    background: #1a1a2e;
    border-bottom: 1px solid #333;
    font-size: 1.2em;
    font-weight: 600;
}
.header span { color: #7c3aed; }
.chat {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}
.msg {
    max-width: 80%;
    padding: 12px 16px;
    border-radius: 16px;
    line-height: 1.5;
    white-space: pre-wrap;
    word-wrap: break-word;
}
.msg.user {
    align-self: flex-end;
    background: #7c3aed;
    color: white;
    border-bottom-right-radius: 4px;
}
.msg.bot {
    align-self: flex-start;
    background: #1e1e2e;
    border: 1px solid #333;
    border-bottom-left-radius: 4px;
}
.msg.typing {
    align-self: flex-start;
    background: #1e1e2e;
    border: 1px solid #333;
    color: #888;
    font-style: italic;
}
.input-area {
    padding: 16px 20px;
    background: #1a1a2e;
    border-top: 1px solid #333;
    display: flex;
    gap: 12px;
}
.input-area input {
    flex: 1;
    padding: 12px 16px;
    border: 1px solid #444;
    border-radius: 24px;
    background: #0f0f0f;
    color: #e0e0e0;
    font-size: 1em;
    outline: none;
}
.input-area input:focus { border-color: #7c3aed; }
.input-area button {
    padding: 12px 24px;
    border: none;
    border-radius: 24px;
    background: #7c3aed;
    color: white;
    font-size: 1em;
    cursor: pointer;
}
.input-area button:hover { background: #6d28d9; }
.input-area button:disabled { background: #444; cursor: not-allowed; }
</style>
</head>
<body>
<div class="header"><span>🤖</span> """ + BUDDY_NAME + """</div>
<div class="chat" id="chat"></div>
<div class="input-area">
    <input type="text" id="input" placeholder="พิมพ์ข้อความ..." autocomplete="off">
    <button id="send">ส่ง</button>
</div>
<script>
const chat = document.getElementById("chat");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send");
const sid = crypto.randomUUID();
const ws = new WebSocket(`ws://${location.host}/ws/${sid}`);

function addMsg(text, cls) {
    const d = document.createElement("div");
    d.className = "msg " + cls;
    d.textContent = text;
    chat.appendChild(d);
    chat.scrollTop = chat.scrollHeight;
    return d;
}

function send() {
    const text = input.value.trim();
    if (!text) return;
    addMsg(text, "user");
    ws.send(text);
    input.value = "";
    sendBtn.disabled = true;
    input.disabled = true;
    addMsg("กำลังคิด...", "typing");
}

ws.onmessage = (e) => {
    const typing = chat.querySelector(".typing");
    if (typing) typing.remove();
    addMsg(e.data, "bot");
    sendBtn.disabled = false;
    input.disabled = false;
    input.focus();
};

ws.onclose = () => addMsg("การเชื่อมต่อหลุด — refresh หน้าเพื่อเชื่อมต่อใหม่", "typing");

sendBtn.addEventListener("click", send);
input.addEventListener("keydown", (e) => { if (e.key === "Enter") send(); });
input.focus();
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    agent = get_agent(session_id)
    try:
        while True:
            data = await websocket.receive_text()
            response = agent.chat(data)
            await websocket.send_text(response)
    except WebSocketDisconnect:
        pass


if __name__ == "__main__":
    import uvicorn
    if not ANTHROPIC_API_KEY:
        print("❌ ตั้งค่า ANTHROPIC_API_KEY ก่อนนะ")
        exit(1)
    port = int(os.getenv("WEB_PORT", "8080"))
    print(f"🌐 {BUDDY_NAME} Web UI: http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
