# 🚀 SmartOps Core v4.0 - ONE PAGE REFERENCE (Demo Ready)

**Status:** ✅ PRODUCTION READY | **Date:** Dec 1, 2025 | **Phase:** 3 (Integration)

---

## ⚡ QUICK START (60 Seconds)

```bash
# Setup (First time only):
python setup.py

# Run server (Every time):
python start.py

# In another terminal, test:
curl http://localhost:8001/docs
```

---

## 🌉 DEMO SETUP (30 Minutes Before)

```bash
# Terminal 1 - FastAPI
python start.py
# OUTPUT: INFO: Application startup complete

# Terminal 2 - SSH Tunnel (KEEP OPEN)
ssh -R 8001:localhost:8001 smartops@164.92.110.179
# OUTPUT: smartops@vps:~$

# Terminal 3 - Test
curl http://localhost:8001/
ssh smartops@164.92.110.179 "curl http://localhost:8001/"
# BOTH should return JSON
```

---

## 🎬 DEMO FLOW (Martín Demo)

```
1. Martín sends WhatsApp: "¿Qué tienen de costillas?"
   ↓
2. Waha receives → n8n webhook
   ↓
3. n8n transforms JSON → Posts to http://localhost:8001/demo/message
   ↓
4. SSH Tunnel routes to local FastAPI
   ↓
5. FastAPI RAG pipeline:
   - Búsqueda en pgvector
   - Retrieves menú data
   - Genera respuesta con IA
   ↓
6. Response JSON → n8n → Waha → WhatsApp
   ↓
7. Martín recibe: "Tenemos costilla Premium a $28.990"

⏱️ Total latency: 2-5 seconds
```

---

## 📋 PRE-DEMO CHECKLIST

```
□ FastAPI running (terminal 1): python start.py
□ SSH Tunnel active (terminal 2): ssh -R 8001:localhost:8001 ...
□ Local API responds: curl http://localhost:8001/ → 200
□ Tunnel works: ssh smartops@164.92.110.179 "curl..." → 200
□ n8n workflow active: http://164.92.110.179:5678
□ PostgreSQL running: docker ps | grep postgres
□ Test WhatsApp sent: Recibiste respuesta?
□ Logs visible: Terminal 1 shows requests
□ Backup ready: python interactive_demo.py funciona
```

---

## 🔧 n8n WORKFLOW (Blueprint)

```
Webhook → Transform → HTTP Request → Response

Node 1 - Webhook:
  Path: /webhook/demo-message
  Method: POST

Node 2 - Transform:
  Output: {
    "session_id": "{{$node.Webhook.json.from}}",
    "message": "{{$node.Webhook.json.body}}"
  }

Node 3 - HTTP Request:
  URL: http://localhost:8001/demo/message
  Method: POST
  Body: {{$node.Transform.json}}

Node 4 - Response:
  Status: 200
  Body: {{$node["HTTP Request"].json}}
```

---

## 🎯 KEY ENDPOINTS

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check |
| `/docs` | GET | Swagger UI |
| `/demo/upload` | POST | Load PDF/Image (THE LOADER) |
| `/demo/message` | POST | Query RAG (THE SHOW) |
| `/demo/reset` | POST | Clean session (THE NEURALIZER) |

---

## 📊 MONITORING (During Demo)

```
Terminal 1 (FastAPI logs):
  ✓ INFO: POST /demo/message HTTP/1.1" 200 OK
  ✓ Response time < 5 sec
  ✓ No 500 errors

n8n Logs:
  ✓ Workflow triggered
  ✓ No execution errors
  ✓ Response received

WhatsApp:
  ✓ Message received
  ✓ Response within 5 sec
```

---

## 🚨 TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| FastAPI not responding | `python start.py` |
| Tunnel not working | Check: `ssh smartops@164.92.110.179 "echo OK"` |
| n8n error | Check workflow at http://164.92.110.179:5678 |
| Slow response | Check: Terminal 1 logs, PostgreSQL, network |
| No WhatsApp message | Verify: Waha running, webhook URL correct |

---

## 📁 IMPORTANT FILES

```
setup.py                    # First-time setup
start.py                    # Launch FastAPI
integrate.py                # Integration protocol
INTEGRATION_PHASE3.md       # Full integration guide
DEMO_SCRIPT_MARTIN.md       # Demo talking points
DEMO_DAY_CHECKLIST.md       # Minute-by-minute ops
interactive_demo.py         # Backup demo tool
```

---

## 🎓 ARCHITECTURE

```
Frontend (Waha)
  ↓
n8n (Orchestrator)
  ↓
SSH Tunnel (Reverse)
  ↓
FastAPI (Your PC)
  ├─ POST /demo/message
  ├─ RAG Pipeline
  │  ├─ pgvector Search
  │  ├─ LLM Response Gen
  │  └─ JSON Return
  ├─ PostgreSQL
  └─ OpenAI API
```

---

## 📞 SUPPORT

- **Setup issues:** See WINDOWS_QUICK_START.md
- **Integration:** See INTEGRATION_PHASE3.md
- **Demo prep:** See DEMO_DAY_CHECKLIST.md
- **Everything:** See DOCS_INDEX.md

---

## ✅ SUCCESS CRITERIA

```
Demo Success = 
  3 WhatsApp messages 
  × 3 correct responses 
  × < 5 sec latency each
  × 0 system crashes
```

---

## 🚀 NEXT PHASES

**Phase 4:** Multi-language support + Chat history  
**Phase 5:** ML model fine-tuning + Performance optimization  
**Phase 6:** Scalable deployment + Team dashboard  

---

**You're ready! Let's go! 🎯**
