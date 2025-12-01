# 🚀 SMARTOPS CORE v4.0 - TEAM HANDOFF PROTOCOL

**Fecha:** 1 de Diciembre 2025  
**Estado:** 🟢 PRODUCTION READY  
**Commit Genesis:** `c9487e8` (Clean production-ready)  
**Restore Commit:** `23e681a` (Full recovery with Python backend)

---

## 📋 RESUMEN EJECUTIVO

SmartOps Core es un **sistema cognitivo para demostraciones comerciales** que:
- Ingesta menús (PDF + fotos con GPT-4o Vision)
- Busca por similitud semántica (pgvector + OpenAI embeddings)
- Limpia sesiones de forma segura (THE NEURALIZER)

**Capacidades Actuales:** 100% Quest 1 & Quest 2 ✅  
**Próxima Fase:** LLM responses + Chat history (Week 2)

---

## 🎯 PLAN DE ENROLL (ESTA SEMANA)

### LUNES: Setup + Validación
```bash
# 1. Clonar repositorio
git clone https://github.com/emmiliotapia/smartops-core.git
cd smartops-core

# 2. Virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar ambiente
cp .env.example .env
# → Pedirme API KEY de OpenAI por privado (NO GIT)

# 5. VALIDAR (debe mostrar 7/7 checks en VERDE)
python setup_validation.py
```

✅ **Success Criteria:** Ver mensaje "All checks passed! Setup is ready."

---

### MARTES: Test Endpoints
```bash
# Terminal 1: Base de datos
docker-compose up -d postgres

# Terminal 2: API server
uvicorn app.main:app --reload

# Terminal 3: Test interactivo
python interactive_demo.py menus/steak_cortes.jpg
```

✅ **Success Criteria:** Ver flujo completo upload → chat → cleanup sin errores

---

### MIÉRCOLES: RAG Pipeline Deep Dive
- Probar con PDFs reales (facturas, menús, etc.)
- Probar con fotos de baja luz
- Verificar similitud de búsqueda
- **Consigna:** Usar `TESTING_GUIDE.md` para escenarios avanzados

---

### JUEVES: Integration con Waha/n8n
- Conectar webhook desde n8n
- Enviar mensajes desde WhatsApp
- Verificar respuestas RAG
- **Consigna:** Usar `app/routers/demo.py` como referencia

---

### VIERNES: Primera Demo Comercial
- Demostración real con prospecto
- Menú del cliente en vivo
- Chat multilingüe (ES/EN)
- **Consigna:** Usar `interactive_demo.py` para preludio

---

## 🏗️ ARQUITECTURA RÁPIDA

```
┌─────────────────────────────────────────┐
│        FastAPI Backend (8001)           │
├─────────────────────────────────────────┤
│  POST /demo/upload   → THE LOADER       │
│  POST /demo/message  → THE SHOW         │
│  POST /demo/reset    → THE NEURALIZER   │
└──────────────┬────────────────────────┬─┘
               │                        │
        ┌──────▼────────┐       ┌──────▼─────────┐
        │  RAG Pipeline │       │  PostgreSQL    │
        ├───────────────┤       │  + pgvector    │
        │ 1. Extract    │       │  (embeddings)  │
        │ 2. Chunk      │       └────────────────┘
        │ 3. Embed      │
        │ 4. Store      │
        │ 5. Search     │
        └───────────────┘
                 ↓
        OpenAI API (Embeddings + Vision)
```

---

## 📁 ESTRUCTURA DE PROYECTO

```
smartops-core/
│
├── 📄 QUICK_START.md         ← COMIENZA AQUÍ (5 min)
├── 📄 README.md              (Visión general)
├── 📄 ENROLL_SETUP.md        (Guía detallada)
├── 📄 ENV_REFERENCE.md       (Variables explicadas)
├── 📄 TESTING_GUIDE.md       (Escenarios de test)
├── 📄 GIT_DEVELOPER_GUIDE.md (Workflow Git)
│
├── .env.example              (Plantilla - NUNCA comitear valores reales)
├── .env.standard             (Referencia técnica)
├── requirements.txt          (10 paquetes core)
│
├── 📂 app/
│   ├── main.py               (FastAPI entry point)
│   ├── database.py           (PostgreSQL + pgvector config)
│   ├── routers/demo.py       (3 endpoints)
│   ├── services/demo_rag.py  (RAG pipeline)
│   └── modules/demo/         (Models, schemas, constants)
│
├── setup_validation.py       (7-point validation - RUN FIRST!)
├── interactive_demo.py       (End-to-end test tool)
├── test_demo_endpoints.ps1   (PowerShell tests)
└── test_demo_advanced.py     (Python test suite)
```

---

## 🔐 REGLAS DE ORO

### 1️⃣ NUNCA Commitear Secretos
```bash
# ❌ WRONG
echo "OPENAI_API_KEY=sk-..." >> .env
git add .env
git commit -m "Add API key"

# ✅ CORRECT
cp .env.example .env
# Editar manualmente (NO COMMIT)
git add .gitignore  # Solo esto
```

### 2️⃣ Si Funciona, Testea + Documenta
```bash
# Siempre validar antes de push
python setup_validation.py
python interactive_demo.py test_menu.pdf
```

### 3️⃣ Revenue > Perfection
- Solo codear lo que ayude a vender la demo
- Si no hay caso de uso, propone en el standup

### 4️⃣ Uso Limpio de Herramientas
```bash
# Usar interactive_demo.py para probar
python interactive_demo.py menus/steak.jpg

# NO hacer requests manuales al API durante desarrollo
# (usar tests en su lugar)
```

---

## 📞 ENDPOINTS DISPONIBLES

### 1. THE LOADER - Upload Menú
```bash
curl -X POST http://localhost:8001/demo/upload \
  -F "file=@menu.pdf" \
  -F "session_id=demo_001"
```
**Response:** `{"success": true, "chunks_indexed": 5}`

### 2. THE SHOW - Query RAG
```bash
curl -X POST http://localhost:8001/demo/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo_001",
    "question": "¿Qué cortes de carne tienes?"
  }'
```
**Response:** `{"response": "Tenemos...", "confidence": 0.95}`

### 3. THE NEURALIZER - Clean Session
```bash
curl -X POST http://localhost:8001/demo/reset \
  -H "Content-Type: application/json" \
  -d '{"session_id": "demo_001"}'
```
**Response:** `{"success": true}`

---

## 🧪 QUICK TEST CHECKLIST

Después de hacer `setup_validation.py`, ejecutar:

```bash
# Test 1: End-to-end demo
python interactive_demo.py menus/steak_cortes.jpg

# Test 2: PowerShell tests (Windows)
.\test_demo_endpoints.ps1

# Test 3: Advanced Python tests
python test_demo_advanced.py

# Si todo ✅ verde, listo para equipo
```

---

## 📊 VARIABLES DE ENTORNO

**Críticas (DEBEN tener valor):**
- `DATABASE_URL` - PostgreSQL connection
- `OPENAI_API_KEY` - OpenAI API key

**Importantes (valores por defecto):**
- `DEMO_SESSION_TIMEOUT_MINUTES=30`
- `RAG_SIMILARITY_THRESHOLD=0.5`
- `RAG_MAX_CHUNK_SIZE=1000`

**Completa lista:** Ver `ENV_REFERENCE.md`

---

## 🚨 TROUBLESHOOTING

### Error: "ModuleNotFoundError: No module named 'fastapi'"
```bash
# Solución
pip install -r requirements.txt
```

### Error: "Could not connect to database"
```bash
# Solución
docker-compose up -d postgres
# Esperar 10 segundos
```

### Error: "OPENAI_API_KEY not found"
```bash
# Solución
# Editar .env con valor real (pídeme por privado)
cat .env | grep OPENAI_API_KEY
```

**Para más troubleshooting:** Ver `ENROLL_SETUP.md`

---

## 🎯 PRÓXIMAS FASES

### Phase 2 (Next Week)
- [ ] GPT-4 Turbo para respuestas generadas
- [ ] Chat history + context persistence
- [ ] Fine-tuning de prompts por industria

### Phase 3 (Week After)
- [ ] Frontend Dashboard (Streamlit/React)
- [ ] Integration con Waha (WhatsApp real)
- [ ] Multi-tenant dashboard

---

## 📞 CONTACTO & RECURSOS

- **Repository:** https://github.com/emmiliotapia/smartops-core
- **Issues:** GitHub Issues (crear para bugs/features)
- **API Docs:** `http://localhost:8001/docs` (Swagger, cuando corre)
- **Code Reference:** Ver `app/README.md`

---

## ✅ CHECKLIST PREVIO AL ENROLL

- [ ] Todo el equipo clonó el repo
- [ ] Todos pasaron `setup_validation.py` (7/7 checks ✅)
- [ ] Todos ejecutaron `interactive_demo.py` exitosamente
- [ ] .env configurado con API KEY real (no en git)
- [ ] Docker Compose running (`docker-compose up -d postgres`)
- [ ] FastAPI server running (`uvicorn app.main:app --reload`)
- [ ] Swagger docs accessible (`http://localhost:8001/docs`)

---

## 🏆 META DEL SPRINT

**Semana 1:** Equipo operativo + Primera demo funcional ✅  
**Semana 2:** LLM integration + Chat history  
**Semana 3:** Frontend + WhatsApp integration  

**KPI:** Revenue-generating demo en vivo para prospecto

---

**Status:** 🟢 PRODUCTION READY  
**Last Updated:** 2025-12-01  
**Maintainer:** Root Admin (Emmilio Tapia)

---

*"If it works, document it. If it helps sell the demo, code it. Otherwise, standby."*
