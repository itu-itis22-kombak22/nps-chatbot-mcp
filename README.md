# NPS Chatbot — MCP Server

NPS chatbot'unu MCP (Model Context Protocol) tool olarak sunan server. Claude Desktop, MCP Inspector veya on-prem MCP UI'larına entegre edilebilir.

---

## Mac'te Kurulum

```bash
git clone https://github.com/itu-itis22-kombak22/nps-chatbot-mcp.git
cd nps-chatbot-mcp

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

## Windows'ta Kurulum

```bash
git clone https://github.com/itu-itis22-kombak22/nps-chatbot-mcp.git
cd nps-chatbot-mcp

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```

---

## .env Ayarları

`.env` dosyası repoda hazır gelir. İş bilgisayarında on-prem LLM ve Oracle kullanmak için güncelle:

```env
# On-prem LLM (GROQ_API_KEY satırını sil, bunları doldur)
OPENAI_API_KEY=your-onprem-api-key
OPENAI_BASE_URL=http://your-llm-host:port/v1
LLM_MODEL=gpt-oss120b

# Oracle DB (USE_DB=true yapınca parquet yerine Oracle'dan okur)
USE_DB=true
ORACLE_HOST=your-oracle-host
ORACLE_PORT=1521
ORACLE_SERVICE=your-service-name
ORACLE_USER=your-username
ORACLE_PASSWORD=your-password
ORACLE_NPS_TABLE=SCHEMA.TABLE_NAME
```

---

## MCP Inspector ile Test

MCP Inspector, tool'ları tarayıcıdan interaktif olarak test etmeyi sağlar. Node.js kurulu olması yeterli.

**Mac:**
```bash
npx @modelcontextprotocol/inspector python server.py
```

**Windows:**
```bash
npx @modelcontextprotocol/inspector python server.py
```

Komut çalıştıktan sonra tarayıcıda `http://localhost:5173` açılır.

### Inspector'da Test Adımları

1. Sol panelde **Tools** sekmesine tıkla
2. Test etmek istediğin tool'u seç
3. Parametreleri doldur ve **Run** butonuna bas

### Örnek Test Senaryoları

**1. Selamlama testi**
- Tool: `nps_chat`
- `message`: `Merhaba, ne yapabilirsin?`

**2. Haftalık özet**
- Tool: `nps_summary`
- `period`: `haftalık`

**3. Kategori analizi**
- Tool: `nps_topic`
- `category`: `Mobil Bankacılık`
- `period`: `aylık`

**4. Segment analizi**
- Tool: `nps_topic`
- `segment`: `Detractor`
- `period`: `haftalık`

**5. Örnek yorum**
- Tool: `nps_example`
- `segment`: `Detractor`
- `emotion`: `Kızgın`

**6. Chatbot state machine testi**
- Tool: `nps_chat` → `message`: `özet` (DETAIL'a düşer, dönem sorar)
- Tool: `nps_chat` → `message`: `haftalık` (cevap üretir)

**7. Session sıfırlama**
- Tool: `nps_reset_session`

---

## Claude Desktop Entegrasyonu

**Mac** — `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows** — `C:\Users\<kullanıcı>\AppData\Roaming\Claude\claude_desktop_config.json`

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

| Tool | Parametreler | Açıklama |
|------|-------------|----------|
| `nps_chat` | `message` | Ana chatbot — doğal dil, state machine akışı |
| `nps_summary` | `period` (haftalık/aylık/günlük) | NPS özeti |
| `nps_topic` | `category`, `segment`, `emotion`, `period` | Detay analiz |
| `nps_example` | `segment`, `category`, `emotion`, `comment_type`, `period` | Örnek yorumlar |
| `nps_reset_session` | — | Konuşma geçmişini sıfırla |
