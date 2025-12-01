# 🏗️ SmartOps Core - Arquitectura Local de Testing

## 📊 Diagrama de Flujo Completo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SMARTOPS CORE LOCAL SETUP                          │
└─────────────────────────────────────────────────────────────────────────────┘

STEP 1: INITIAL SETUP (Primera vez)
════════════════════════════════════════════════════════════════════════════
        ┌─────────────────────────────┐
        │  python local_test_setup.py │  ← Ejecutar UNA SOLA VEZ
        └────────────┬────────────────┘
                     │
        ┌────────────▼────────────┐
        │ ✓ Check Python 3.10+    │
        │ ✓ Create .venv          │
        │ ✓ Install requirements  │
        │ ✓ Start Docker PostgreSQL
        │ ✓ Run setup_validation  │
        └────────────┬────────────┘
                     │
                     ▼
            ✅ Setup Complete


STEP 2: LAUNCH LOCAL SERVER (Cada que quieras probar)
════════════════════════════════════════════════════════════════════════════

Opción A: PYTHON (Multiplataforma - RECOMENDADO)
┌─────────────────────────────┐
│   python run_local_test.py  │ ← ✅ Windows, Mac, Linux
└────────────┬────────────────┘
             │
             ▼
        ┌─────────────────┐
        │ Check venv      │
        │ Check packages  │
        │ Start Docker    │
        │ Test DB        │
        │ Launch uvicorn │
        └────────┬────────┘
                 │
                 ▼
        FastAPI @ 8001


Opción B: POWERSHELL (Windows optimizado)
┌──────────────────────────────┐
│   .\run_local_test.ps1       │ ← ✅ Windows + colores bonitos
└────────────┬─────────────────┘
             │
             ▼
        [Lo mismo que Opción A]


Opción C: BATCH (.bat - Windows legacy)
┌──────────────────────────────┐
│   run_local_test.bat         │ ← ⚠️ Windows CMD
└────────────┬─────────────────┘
             │
             ▼
        [Lo mismo que Opción A]


STEP 3: DEVELOPMENT LOOP
════════════════════════════════════════════════════════════════════════════

        Terminal 1                          Terminal 2
    ┌─────────────────────┐            ┌──────────────────────┐
    │ run_local_test.py   │            │  python             │
    │ (FastAPI running)   │            │  interactive_demo.py│
    │                     │────────────│                      │
    │ :8001 listening     │  HTTP      │  Testing endpoints  │
    │ Auto-reload ON      │            │  Debugging RAG      │
    │                     │            │  Demo simulation    │
    └─────────────────────┘            └──────────────────────┘
            │
            │ Modifica archivos en app/
            │
            ▼
        Auto-reload detects cambios
        FastAPI reinicia automáticamente
            │
            ▼
    Terminal 2 re-testa


STEP 4: VPS TUNNEL (Para conectar con producción)
════════════════════════════════════════════════════════════════════════════

Ejecutar DESPUÉS que esté corriendo local:

        ┌──────────────────────────┐
        │ python vps_tunnel_setup.py
        └────────────┬─────────────┘
                     │
        ┌────────────▼──────────────────┐
        │  SSH Reverse Tunnel Guide     │
        │  - Opción 1: Local → VPS      │
        │  - Opción 2: VPS → Local      │
        │  - Opción 3: Docker compose   │
        └────────────┬──────────────────┘
                     │
        ┌────────────▼──────────────────┐
        │ Local :8001 ←→ VPS :8002      │
        │ Test con n8n/Waha             │
        └───────────────────────────────┘


ARCHITECTURE DIAGRAM
════════════════════════════════════════════════════════════════════════════

                          Your Computer
    ┌─────────────────────────────────────────────────────────┐
    │                                                           │
    │  ┌──────────────┐              ┌────────────────────┐   │
    │  │   FastAPI    │              │  PostgreSQL +      │   │
    │  │  (Uvicorn)   │◄────────────►│   pgvector         │   │
    │  │  :8001       │  SQLAlchemy  │   (Docker)         │   │
    │  │              │              │   :5433            │   │
    │  └──────┬───────┘              └────────────────────┘   │
    │         │                                                │
    │         │ JSON endpoints                                 │
    │         │ • POST /demo/upload                            │
    │         │ • POST /demo/message                           │
    │         │ • POST /demo/reset                             │
    │         │                                                │
    │  ┌──────▼──────────┐                                     │
    │  │  Testing Client │                                     │
    │  │  • curl         │                                     │
    │  │  • interactive_ │                                     │
    │  │    demo.py      │                                     │
    │  │  • Swagger UI   │                                     │
    │  └─────────────────┘                                     │
    │                                                           │
    └─────────────────────────────────────────────────────────┘
                          │
                (SSH Reverse Tunnel)
                          │
            ┌─────────────▼────────────────┐
            │    PRODUCTION VPS            │
            │   164.92.110.179             │
            │   (:8002 ←→ local :8001)     │
            │   n8n + Waha integration     │
            └──────────────────────────────┘


DATA FLOW - RAG Pipeline
════════════════════════════════════════════════════════════════════════════

1. Upload PDF/Image:
   Client → FastAPI /demo/upload → THE LOADER
                                    ↓
                        Extract text + embeddings
                                    ↓
                        Store in PostgreSQL + pgvector


2. Query Semantic:
   Client → FastAPI /demo/message → THE SHOW
                                     ↓
                        Search similar vectors (pgvector)
                                     ↓
                        Return top 3 matches


3. Cleanup Session:
   Client → FastAPI /demo/reset → THE NEURALIZER
                                  ↓
                        Delete session data
                        Delete vectors
                        Clean memory


FILES INVOLVED
════════════════════════════════════════════════════════════════════════════

Start Scripts (choose ONE):
  • run_local_test.py        ← Python (BEST)
  • run_local_test.ps1       ← PowerShell (BEST for Windows)
  • run_local_test.bat       ← Batch (legacy)

Setup & Configuration:
  • local_test_setup.py      ← First-time setup
  • .env                      ← Your secrets (don't commit!)
  • docker-compose.yml        ← PostgreSQL config

Backend Code:
  • app/main.py              ← FastAPI entry point
  • app/routers/demo.py      ← Endpoints (THE LOADER, SHOW, NEURALIZER)
  • app/services/demo_rag.py ← RAG pipeline
  • app/database.py          ← PostgreSQL connection

Testing:
  • interactive_demo.py      ← End-to-end testing
  • setup_validation.py      ← System validation (7 checks)

Documentation:
  • TEAM_HANDOFF.md          ← Weekly schedule
  • RUN_LOCAL_TEST_README.md ← This file (basically)
  • TESTING_GUIDE.md         ← Advanced scenarios


TYPICAL DAILY WORKFLOW
════════════════════════════════════════════════════════════════════════════

Morning: Start Server
  $ python run_local_test.py
  [✓] All systems ready
  INFO: Application startup complete


Development: Make Changes
  $ Edit app/routers/demo.py
  (saved)
  [auto-reload detected]
  INFO: Application startup complete


Testing: Run Tests
  Terminal 2:
  $ python interactive_demo.py menus/steak_cortes.jpg
  [✓] Session created
  [✓] PDF processed
  [✓] Messages sent
  [✓] Session cleaned


Debugging: Check Logs
  Terminal 1 shows all requests:
  INFO: "POST /demo/upload HTTP/1.1" 200
  INFO: "POST /demo/message HTTP/1.1" 200
  INFO: "POST /demo/reset HTTP/1.1" 200


Shutdown: Stop Server
  Ctrl+C in Terminal 1
  INFO: Shutdown complete


TROUBLESHOOTING MATRIX
════════════════════════════════════════════════════════════════════════════

Problem                     Solution
────────────────────────    ────────────────────────────────────────────
Port 8001 in use            Kill other process or use port 8002
venv not found              python local_test_setup.py
Package not found           python local_test_setup.py
Docker not running          Start Docker Desktop
PostgreSQL not starting     Check docker logs: docker logs postgres
Connection refused          Wait 20 seconds for PostgreSQL init
Import error (app.*)        Verify working directory is repo root
CORS error                  Check .env ALLOWED_ORIGINS
API Key invalid             Check .env OPENAI_API_KEY


SUCCESS CHECKLIST ✅
════════════════════════════════════════════════════════════════════════════

□ Python 3.10+ installed
□ Virtual environment created (.venv/)
□ Dependencies installed (pip install -r requirements.txt)
□ .env file configured with OPENAI_API_KEY
□ Docker running
□ PostgreSQL container running (docker ps shows postgres)
□ local_test_setup.py ran with 7/7 checks PASSED
□ run_local_test.py starts without errors
□ FastAPI responds on http://localhost:8001
□ Swagger UI accessible on http://localhost:8001/docs
□ interactive_demo.py runs and completes
□ All endpoints return 200 status codes


NEXT: See TEAM_HANDOFF.md for full weekly schedule!
