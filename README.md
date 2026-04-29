# NPS Chatbot — MCP Server

NPS chatbot'unu MCP (Model Context Protocol) tool olarak sunan server. Claude Desktop veya MCP destekleyen herhangi bir istemciye entegre edilebilir.

---

## Mac'te Çalıştırmak İçin

```bash
# 1. Repoyu klonla
git clone https://github.com/itu-itis22-kombak22/nps-chatbot-mcp.git
cd nps-chatbot-mcp

# 2. Sanal ortam oluştur ve aktive et
python3 -m venv venv
source venv/bin/activate

# 3. Bağımlılıkları kur
pip install -r requirements.txt

# 4. Sunucuyu başlat
python server.py
```

---

## Windows'ta Çalıştırmak İçin

```bash
# 1. Repoyu klonla
git clone https://github.com/itu-itis22-kombak22/nps-chatbot-mcp.git
cd nps-chatbot-mcp

# 2. Sanal ortam oluştur ve aktive et
python -m venv venv
venv\Scripts\activate

# 3. Bağımlılıkları kur
pip install -r requirements.txt

# 4. Sunucuyu başlat
python server.py
```

---

## Claude Desktop Entegrasyonu

`claude_desktop_config.json` dosyasına ekle:

```json
{
  "mcpServers": {
    "nps-chatbot": {
      "command": "python",
      "args": ["/absolute/path/to/nps-chatbot-mcp/server.py"]
    }
  }
}
```

---

## Araçlar (Tools)

| Tool | Açıklama |
|------|----------|
| `nps_chat` | Ana chatbot — doğal dil konuşması, state machine ile tam akış |
| `nps_summary` | Haftalık / aylık / günlük NPS özeti |
| `nps_topic` | Kategori, segment veya duygu bazlı analiz |
| `nps_example` | Filtreye uyan örnek müşteri yorumları (max 5) |
| `nps_reset_session` | Konuşma geçmişini sıfırla |
