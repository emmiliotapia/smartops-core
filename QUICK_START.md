# SmartOps Core - Quick Start Guide

**Versión:** 3.0 | **Actualizado:** 2025-12-01 | **Status:** ✅ Producción Ready

---

## 📖 Tabla de Contenidos

1. [Setup Inicial (5 min)](#setup-inicial)
2. [Estructura del Proyecto](#estructura)
3. [Ejecutar Servidor](#ejecutar-servidor)
4. [Endpoints Principales](#endpoints)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)

---

## Setup Inicial

### Requisitos Previos
```bash
python --version          # Python 3.10+ requerido
pip --version             # pip 21.0+
git --version             # git 2.0+

# Windows: Verificar PowerShell v5+
$PSVersionTable.PSVersion
```

### Paso 1️⃣: Clonar Repositorio
```bash
git clone https://github.com/emmiliotapia/smartops-core.git
cd smartops-core
```

### Paso 2️⃣: Crear Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Paso 3️⃣: Instalar Dependencias (10 paquetes)
```bash
pip install -r requirements.txt
```

**Packages instalados:**
- ✅ fastapi, uvicorn (web framework)
- ✅ sqlalchemy, psycopg2-binary, pgvector (database)
- ✅ pydantic (validation)
- ✅ python-dotenv (config)
- ✅ requests, openai (APIs)
- ✅ pypdf (documents)

### Paso 4️⃣: Configurar Ambiente
```bash
# Copiar template
cp .env.example .env

# Editar .env con tus valores:
# OPENAI_API_KEY=sk-...
# DATABASE_URL=postgresql://root:<password>@localhost:5433/smartops_core
```

### Paso 5️⃣: Validar Setup
```bash
python setup_validation.py

# Deberías ver: ✅ All checks passed! Setup is ready.
```

---

## Estructura del Proyecto

```
smartops-core/
├── 📄 requirements.txt          # ← 10 dependencias esenciales
├── 📄 .env.example              # ← Variables de entorno template
├── 📄 ENROLL_SETUP.md           # ← Guía detallada para nuevos devs
├── 📄 setup_validation.py       # ← Script de validación
├── 📄 interactive_demo.py       # ← Test interactivo
│
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── core/
│   │   ├── config.py           # Settings
│   │   └── database.py         # PostgreSQL + pgvector
│   │
│   ├── modules/demo/
│   │   ├── models.py           # SQLAlchemy models
│   │   ├── schemas.py          # Pydantic schemas (DTOs)
│   │   └── constants.py        # RAG constants
│   │
│   ├── services/
│   │   └── demo_rag.py         # RAG: indexing, search, embeddings
│   │
│   └── routers/
│       └── demo.py             # 3 endpoints: upload, message, reset
│
├── docker-compose.yml           # PostgreSQL + pgvector stack
└── Dockerfile.backend          # Production image
```

---

## Ejecutar Servidor

### Opción A: Development Mode (Recomendado)
```bash
# Terminal 1: Base de datos (opcional - solo si usas local PostgreSQL)
docker-compose up -d postgres

# Terminal 2: Backend FastAPI (con hot-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Acceder a:**
- 📍 API Docs: http://localhost:8000/docs (Swagger)
- 📍 ReDoc: http://localhost:8000/redoc

### Opción B: Production Mode (Docker)
```bash
# Construir y ejecutar todo
docker-compose up -d

# Ver logs
docker-compose logs -f app
```

---

## Endpoints Principales

### 1. Health Check
```bash
curl http://localhost:8000/demo/health

# Response: {"status": "ok"}
```

### 2. THE LOADER - Upload PDF/Image
```bash
curl -X POST http://localhost:8000/demo/upload \
  -F "file=@menus/steak.pdf" \
  -F "session_id=demo_001"

# Response:
#{
#  "success": true,
#  "session_id": "demo_001",
#  "chunks_indexed": 5,
#  "message": "PDF indexed successfully"
#}
```

### 3. THE SHOW - Chat with RAG
```bash
curl -X POST http://localhost:8000/demo/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo_001",
    "question": "¿Qué cortes de carne tienes?"
  }'

# Response:
#{
#  "session_id": "demo_001",
#  "response": "Tenemos los siguientes cortes...",
#  "context": ["chunk_text_1", "chunk_text_2"],
#  "confidence": 0.95
#}
```

### 4. THE NEURALIZER - Clean Session
```bash
curl -X POST http://localhost:8000/demo/reset \
  -H "Content-Type: application/json" \
  -d '{"session_id": "demo_001"}'

# Response: {"success": true, "message": "Session cleaned"}
```

---

## Testing

### Prueba Interactiva (Automática)
```bash
# El script hace todo: upload → chat loop → cleanup
python interactive_demo.py menus/example.pdf
```

### Prueba Manual con Postman
1. Importar en Postman: `http://localhost:8000/docs` (copiar URLs)
2. Ejecutar requests en orden: upload → message (varias veces) → reset
3. Ver respuestas en JSON

---

## Modelo de Datos

### DemoSession
Controla el ciclo de vida de cada usuario
```
session_id: str (unique)
created_at: datetime
expires_at: datetime (30 min default)
status: active/expired/cleaned
```

### DemoVector
Chunks + embeddings del documento
```
id: int
session_id: str (FK)
chunk_text: str (max 1000 chars)
embedding: Vector(1536)  ← OpenAI text-embedding-3-small
source_file: str
created_at: datetime
```

---

## Troubleshooting

### ❌ `ModuleNotFoundError: No module named 'fastapi'`
```bash
# Solución: Verificar venv activo
which python  # o: where python (Windows)
# Debería ser: /path/to/.venv/bin/python

# Reinstalar
pip install -r requirements.txt
```

### ❌ `ERROR: Could not connect to database`
```bash
# Verificar .env tiene DATABASE_URL correcto
cat .env | grep DATABASE_URL

# Verificar PostgreSQL está corriendo
docker ps | grep postgres
```

### ❌ `OpenAI API Error: Invalid API key`
```bash
# Verificar clave en .env
echo $OPENAI_API_KEY  # o: $env:OPENAI_API_KEY (Windows)

# Obtener nueva clave: https://platform.openai.com/api-keys
```

### ❌ `Port 8000 already in use`
```bash
# Cambiar puerto
uvicorn app.main:app --reload --port 8001
```

---

## Para el Equipo - Enroll Esta Semana

### Checklist ✅

- [ ] **Lunes:** Clone repo → Setup env → Run validation
- [ ] **Martes:** Test endpoints con curl/Postman
- [ ] **Miércoles:** Upload PDFs/Images → Verify RAG indexing
- [ ] **Jueves:** Chat loop → Verify similarity search
- [ ] **Viernes:** Deploy en staging → Final validation

### Recursos

| Recurso | Ubicación | Descripción |
|---------|-----------|-------------|
| Full Guide | `ENROLL_SETUP.md` | Guía completa + modelos + flujos |
| Validation | `python setup_validation.py` | Verificar setup |
| Testing | `python interactive_demo.py` | Prueba automática end-to-end |
| API Docs | `http://localhost:8000/docs` | Swagger interactivo |

---

## Próximos Pasos

### 🔴 Phase 2: LLM Integration (Next Week)
- [ ] Implementar GPT-4 Turbo para respuestas
- [ ] Agregar chat history
- [ ] Fine-tune prompts

---

**¡Listo para empezar! 🚀**

*Last Updated: 2025-12-01 | Version: 3.0 | Status: Production Ready*
