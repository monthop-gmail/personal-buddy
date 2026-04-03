# Personal Buddy

AI assistant ส่วนตัวที่รันบน [Claude Code](https://docs.anthropic.com/en/docs/claude-code)

สร้างบนระบบ extension อย่างเป็นทางการของ Claude Code — [CLAUDE.md](https://code.claude.com/docs/en/memory) สำหรับบุคลิก, [MCP](https://code.claude.com/docs/en/mcp) สำหรับ tools, และ [Channels](https://code.claude.com/docs/en/channels) สำหรับ Telegram/web chat Buddy จะจำเรื่องของคุณ จัดการปฏิทิน อ่านอีเมล และเตือนความจำให้

## วิธีการทำงาน

Claude Code เป็นสมอง โปรเจกต์นี้เพิ่ม:

- **[CLAUDE.md](https://code.claude.com/docs/en/memory)** — กฎบุคลิกและพฤติกรรม โหลดใหม่ทุกเซสชัน
- **[MCP tools server](https://code.claude.com/docs/en/mcp)** — memory ถาวร, Google Calendar, Gmail, reminders (12 tools)
- **[Official channel plugins](https://code.claude.com/docs/en/channels)** — Telegram และ web chat สร้างและดูแลโดย Anthropic

ไม่ต้องใช้ API key แยก — Claude Code จัดการการคิดทั้งหมดเอง

## ฟีเจอร์

- **Memory ถาวร** — จำข้อมูล ความชอบ และคนรอบข้างข้ามเซสชัน
- **Google Calendar** — ดูนัดหมาย สร้างนัดใหม่
- **Gmail** — อ่านเมล ส่งเมล (ยืนยันก่อนส่งเสมอ)
- **Reminders** — ตั้งเตือนความจำ เช็คว่าอะไรถึงเวลา
- **Telegram** — คุยกับ buddy จากมือถือผ่าน [official plugin](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/telegram)
- **Web chat** — หน้าเว็บแชทบน localhost ผ่าน [fakechat plugin](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/fakechat)
- **Permission relay** — อนุมัติ/ปฏิเสธการใช้ tools จาก Telegram ได้

## เริ่มต้นใช้งาน

### 1. ติดตั้ง MCP tools

```bash
git clone https://github.com/monthop-gmail/personal-buddy.git
cd personal-buddy
./setup.sh
```

### 2. ติดตั้ง channel plugins (ใน Claude Code)

```
/plugin install telegram@claude-plugins-official
/plugin install fakechat@claude-plugins-official
/reload-plugins
/telegram:configure <bot-token-ของคุณ>
```

> สร้าง bot token จาก [@BotFather](https://t.me/BotFather) บน Telegram

### 3. เปิดใช้งานพร้อม channels

```bash
# Telegram อย่างเดียว
claude --channels plugin:telegram@claude-plugins-official

# Web chat อย่างเดียว (localhost:8787)
claude --channels plugin:fakechat@claude-plugins-official

# ทั้งคู่
claude --channels plugin:telegram@claude-plugins-official plugin:fakechat@claude-plugins-official
```

### 4. จับคู่ Telegram

1. ส่งข้อความอะไรก็ได้ไปที่ bot บน Telegram
2. Bot ตอบกลับด้วย pairing code
3. ใน Claude Code: `/telegram:access pair <code>`
4. ล็อกการเข้าถึง: `/telegram:access policy allowlist`

เรียบร้อย! คุยกับ buddy ได้จาก Telegram หรือหน้าเว็บ

## MCP Tools

| Tool | คำอธิบาย |
|------|---------|
| `save_memory` | บันทึกข้อมูล ความชอบ คนรอบข้าง |
| `search_memory` | ค้นหา memory ที่บันทึกไว้ |
| `list_memories` | แสดง memory ล่าสุด |
| `delete_memory` | ลบ memory ตาม ID |
| `list_calendar_events` | ดูนัดหมายจาก Google Calendar |
| `create_calendar_event` | สร้างนัดหมายใหม่ |
| `list_emails` | อ่านอีเมลจาก Gmail |
| `send_email` | ส่งอีเมลผ่าน Gmail |
| `set_reminder` | ตั้งเตือนความจำ |
| `check_reminders` | เช็ค reminder ที่ถึงเวลา |
| `list_reminders` | แสดง reminder ที่รอดำเนินการ |
| `delete_reminder` | ลบ reminder ตาม ID |

## ตั้งค่า Google Calendar & Gmail

1. สร้างโปรเจกต์ใน [Google Cloud Console](https://console.cloud.google.com/)
2. เปิดใช้ **Calendar API** และ **Gmail API**
3. สร้าง **OAuth 2.0 credentials** (Desktop app)
4. ดาวน์โหลดเป็น `credentials.json` ไปที่ `~/.personal-buddy/`
5. ใช้ครั้งแรกจะเปิด browser เพื่อทำ OAuth flow

## สถาปัตยกรรม

```
📱 Telegram ──→ Official Telegram Plugin ──┐
🌐 Browser  ──→ Official Fakechat Plugin ──┤
💻 Terminal ────────────────────────────────┘
                                            │
                                     Claude Code (สมอง)
                                            │
                                     CLAUDE.md (บุคลิก)
                                            │
                                     MCP Tools Server
                                    (personal-buddy)
                                            │
                            ┌───────────────┼───────────────┐
                            │               │               │
                         Memory      Google APIs      Reminders
                      (ไฟล์ JSON)  (Calendar/Gmail)  (ไฟล์ JSON)
```

ใช้ pattern เดียวกับ `/buddy` companion ใน Claude Code:

- **คำนวณใหม่ทุกเซสชัน** — กฎบุคลิกจาก CLAUDE.md, บริบทการสนทนา
- **เก็บถาวรข้ามเซสชัน** — memories, reminders (ไฟล์ JSON ใน `~/.personal-buddy/`)

`/buddy` companion เก็บข้อมูลคงที่ (species, rarity, stats) และสร้างบุคลิกใหม่ผ่าน Claude API ทุกเซสชัน Personal Buddy ใช้ pattern เดียวกัน: ข้อมูลคงที่เก็บใน JSON ส่วน Claude Code คำนวณพฤติกรรมจาก CLAUDE.md ใหม่ทุกเซสชัน

## เปรียบเทียบ Official กับ Third-Party

> **สำคัญ:** ช่วงแรกของการพัฒนา เราอ้างอิง blog จากบุคคลที่สาม (claudefa.st) ที่ตั้งชื่อ "Bones & Soul" และอ้างรายละเอียดเกี่ยวกับ `/buddy` หลังจากตรวจสอบกับ source code จริงและ official docs แล้ว เราแก้ไขทุกจุดให้ถูกต้อง ตารางนี้ช่วยแยกแยะว่าอะไรเป็น official อะไรไม่ใช่

| หัวข้อ | Blog บุคคลที่สาม (claudefa.st) | Official (source code / docs) | โปรเจกต์นี้ |
|-------|-------------------------------|-------------------------------|------------|
| **ชื่อสถาปัตยกรรม** | "Bones & Soul" | ไม่มีคำนี้ใน source code — blog ตั้งเอง | ใช้คำ official: "persisted" vs "recomputed" |
| **Hash function** | FNV-1a + Mulberry32 PRNG | LCG PRNG (`Math.imul(seed, 1664525)`) | ไม่เกี่ยว — ไม่ได้ใช้ใน personal buddy |
| **บุคลิก** | "Soul" สร้างจาก LLM | Claude API สร้างชื่อ/บุคลิกจาก seed ทุกเซสชัน | CLAUDE.md โหลดทุกเซสชัน (official [memory system](https://code.claude.com/docs/en/memory)) |
| **ข้อมูลถาวร** | "Bones" (species, stats) | `bones` object เก็บใน appState | ไฟล์ JSON ใน `~/.personal-buddy/` |
| **Species/Rarity/Stats** | 18 species, 5 rarity, 5 stats | ยืนยันแล้วว่ามีจริงใน source code | ไม่เกี่ยว — ไม่ได้ใช้ใน personal buddy |
| **Telegram** | ไม่ได้กล่าวถึง | [Official Telegram plugin](https://code.claude.com/docs/en/channels) | ใช้ official plugin |
| **Web UI** | ไม่ได้กล่าวถึง | [Official fakechat plugin](https://code.claude.com/docs/en/channels) | ใช้ official plugin |
| **MCP tools** | ไม่ได้กล่าวถึง | [Official MCP protocol](https://code.claude.com/docs/en/mcp) | MCP server 12 tools |
| **ระบบ extension** | ไม่ได้กล่าวถึง | [CLAUDE.md + MCP + Channels + Plugins](https://code.claude.com/docs/en/features-overview) | ใช้ทั้ง 4 ระบบ official |

**สรุป:** _pattern_ ของ `/buddy` (เก็บข้อมูลคงที่ + คำนวณพฤติกรรมใหม่ทุกเซสชัน) มีอยู่จริง ยืนยันจาก source code แล้ว แต่ชื่อ "Bones & Soul" ไม่ใช่ official — เป็นคำที่ blog บุคคลที่สามตั้งขึ้น โปรเจกต์นี้สร้างบน official Claude Code APIs และระบบ extension ทั้งหมด

## โครงสร้างโปรเจกต์

```
personal-buddy/
├── CLAUDE.md          # กฎบุคลิก (คำนวณใหม่ทุกเซสชัน)
├── mcp_server.py      # MCP tools server (12 tools, ไม่ต้องใช้ API key)
├── memory.py          # Memory store ถาวร (เก็บข้ามเซสชัน)
├── google_tools.py    # Google Calendar + Gmail
├── scheduler.py       # ระบบเตือนความจำ
├── config.py          # การตั้งค่า (memory dir, credentials path)
├── setup.sh           # script ติดตั้งครั้งเดียว
└── requirements.txt   # Python dependencies (mcp, google-api)
```

## License

MIT
