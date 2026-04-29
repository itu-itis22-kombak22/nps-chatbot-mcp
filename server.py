"""
NPS Chatbot — MCP Server

Bankadaki Claude/MCP istemcilerine aşağıdaki araçları sunar:

  nps_chat          → Ana chatbot (state machine ile tam konuşma akışı)
  nps_summary       → Haftalık/aylık/günlük özet
  nps_topic         → Kategori / segment / duygu analizi
  nps_example       → Örnek yorum listesi
  nps_reset_session → Chatbot session'ını sıfırla

Çalıştır (stdio transport):
    python server.py

Claude Desktop / MCP istemci config:
    {
      "mcpServers": {
        "nps-chatbot": {
          "command": "python",
          "args": ["/path/to/nps-chatbot-mcp/server.py"]
        }
      }
    }
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
)

from chatbot.engine import NPSChatbot
from chatbot.modes import summary as summary_mode
from chatbot.modes import topic as topic_mode
from chatbot.modes import example as example_mode

# ──────────────────────────────────────────────────────────────────────────────
# Server ve chatbot instance
# ──────────────────────────────────────────────────────────────────────────────

app = Server("nps-chatbot")

# Her MCP session için tek bot instance
_bot = NPSChatbot(use_llm=True)


def _text(content: str) -> CallToolResult:
    return CallToolResult(content=[TextContent(type="text", text=content)])


# ──────────────────────────────────────────────────────────────────────────────
# Tool tanımları
# ──────────────────────────────────────────────────────────────────────────────

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="nps_chat",
            description=(
                "NPS chatbot ile doğal dil konuşması. "
                "Kullanıcının mesajını alır, intent'i belirler ve uygun yanıtı üretir. "
                "State machine ile DIRECT → DETAIL → RESPONSE akışını yönetir."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Kullanıcının chatbot'a yazdığı mesaj",
                    }
                },
                "required": ["message"],
            },
        ),
        Tool(
            name="nps_summary",
            description=(
                "Belirtilen dönem için NPS özeti döndürür. "
                "Offline hazırlık tablosunda hazır özet varsa onu kullanır, "
                "yoksa istatistiksel özet üretir."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "period": {
                        "type": "string",
                        "enum": ["haftalık", "aylık", "günlük"],
                        "description": "Özet dönemi",
                    }
                },
                "required": ["period"],
            },
        ),
        Tool(
            name="nps_topic",
            description=(
                "Belirli bir kategori, segment veya duygu bazında NPS analizi yapar. "
                "Tüm parametreler opsiyoneldir, hiç verilmezse genel analiz döndürür."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": (
                            "Ana kategori adı. Örnek: 'Mobil Bankacılık', 'ATM', 'Kartlar', "
                            "'Banka', 'Şube', 'Çağrı Merkezi', 'Borsa Market', 'Fon Market', "
                            "'Getirfinans', 'FX Market', 'Görüntülü Bankacılık', "
                            "'Kiraz (Vadeli Hesap)', 'Hızlı Para (KMH)', 'Kripto Market', "
                            "'Kurumsal Bankacılık', 'Kampanyalar', 'Diğer'"
                        ),
                    },
                    "segment": {
                        "type": "string",
                        "enum": ["Detractor", "Passive", "Promoter"],
                        "description": "NPS segmenti (Detractor: 0-6, Passive: 7-8, Promoter: 9-10)",
                    },
                    "emotion": {
                        "type": "string",
                        "enum": ["Mutsuz", "Kızgın", "Endişeli", "Mutlu", "Umutlu", "Minnettar", "Veri Yetersiz"],
                        "description": "Müşteri duygu durumu",
                    },
                    "period": {
                        "type": "string",
                        "enum": ["haftalık", "aylık", "günlük"],
                        "description": "Analiz dönemi (varsayılan: aylık)",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="nps_example",
            description=(
                "Filtre kriterlerine uyan gerçek müşteri yorumu örnekleri döndürür. "
                "Maksimum 5 örnek gösterir."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "segment": {
                        "type": "string",
                        "enum": ["Detractor", "Passive", "Promoter"],
                        "description": "NPS segmenti",
                    },
                    "category": {
                        "type": "string",
                        "description": "Ana kategori adı",
                    },
                    "emotion": {
                        "type": "string",
                        "enum": ["Mutsuz", "Kızgın", "Endişeli", "Mutlu", "Umutlu", "Minnettar", "Veri Yetersiz"],
                        "description": "Müşteri duygu durumu",
                    },
                    "comment_type": {
                        "type": "string",
                        "enum": ["Şikayet", "Memnuniyet", "Talep/Öneri", "Veri Yetersiz"],
                        "description": "Yorum tipi",
                    },
                    "period": {
                        "type": "string",
                        "enum": ["haftalık", "aylık", "günlük"],
                        "description": "Dönem (varsayılan: haftalık)",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="nps_reset_session",
            description="Chatbot konuşma geçmişini ve state'ini sıfırlar. Yeni bir konuşma başlatmak için kullanın.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
    ]


# ──────────────────────────────────────────────────────────────────────────────
# Tool handler
# ──────────────────────────────────────────────────────────────────────────────

@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:

    if name == "nps_chat":
        message = arguments.get("message", "").strip()
        if not message:
            return _text("Mesaj boş olamaz.")
        response = _bot.chat(message)
        return _text(response)

    elif name == "nps_summary":
        period = arguments.get("period", "haftalık")
        result = summary_mode.respond({"period": period})
        return _text(result)

    elif name == "nps_topic":
        params = {
            "category": arguments.get("category"),
            "segment":  arguments.get("segment"),
            "emotion":  arguments.get("emotion"),
            "period":   arguments.get("period", "aylık"),
        }
        result = topic_mode.respond(params)
        return _text(result)

    elif name == "nps_example":
        params = {
            "segment":      arguments.get("segment"),
            "category":     arguments.get("category"),
            "emotion":      arguments.get("emotion"),
            "comment_type": arguments.get("comment_type"),
            "period":       arguments.get("period", "haftalık"),
        }
        result = example_mode.respond(params)
        return _text(result)

    elif name == "nps_reset_session":
        _bot.reset()
        return _text("Chatbot session sıfırlandı. Yeni bir konuşma başlatabilirsiniz.")

    else:
        return _text(f"Bilinmeyen tool: {name}")


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
