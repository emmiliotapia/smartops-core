# SmartOps Core - Índice de Documentación Técnica

## Documentación Disponible

### 🚀 COMIENZA AQUÍ

| Documento | Tiempo | Descripción |
|-----------|--------|-------------|
| **[QUICK_START.md](./QUICK_START.md)** | 5 min | Setup + primeros pasos |
| **[README.md](./README.md)** | 2 min | Vista general del proyecto |

---

### 📖 Guías Completas

| Documento | Tiempo | Descripción |
|-----------|--------|-------------|
| **[ENROLL_SETUP.md](./ENROLL_SETUP.md)** | 20 min | Guía completa para desarrolladores |
| **[ENV_REFERENCE.md](./ENV_REFERENCE.md)** | 10 min | Todas las variables de entorno |
| **[TESTING_GUIDE.md](./TESTING_GUIDE.md)** | 15 min | Testing avanzado y scripts |
| **[GIT_DEVELOPER_GUIDE.md](./GIT_DEVELOPER_GUIDE.md)** | 10 min | Workflow Git + pre-commit hooks |

---

### 📚 Modular Documentation

**Backend:** [`app/README.md`](./app/README.md)
- Estructura de endpoints
- Modelos Pydantic
- Pipeline RAG
- Setup local

**Workflows n8n:** [`n8n_workflows/README.md`](./n8n_workflows/README.md)
- Descripción de workflows
- Payloads entrada/salida
- Configuración webhooks

**Frontend:** [`frontend/README.md`](./frontend/README.md)
- Componentes
- Desarrollo local
- Deployment

---

### 🏗️ Referencia Técnica

- **[BIBLIA_v1.md](./BIBLIA_v1.md)** - Filosofía de diseño y contexto histórico (referencia)
- **[.env.standard](./.env.standard)** - Referencia técnica de variables
- **[GENESIS_CHECKLIST.md](./GENESIS_CHECKLIST.md)** - Verificación pre-producción

---

### ✨ Herramientas de Utilidad

```bash
# Validar el setup (verifica Python, deps, .env, DB, etc.)
python setup_validation.py

# Test automático end-to-end (upload → chat → cleanup)
python interactive_demo.py menus/example.pdf

# Validar scripts antes de commit
.\validate-scripts.ps1
```

---

## Flujo de Aprendizaje Recomendado

### Para Nuevo Desarrollador
1. Leer: **README.md** (2 min)
2. Leer: **QUICK_START.md** (5 min)
3. Ejecutar: `python setup_validation.py`
4. Ejecutar: `python interactive_demo.py menus/example.pdf`
5. Consultar: **ENROLL_SETUP.md** según necesite
6. Consultar: **ENV_REFERENCE.md** para config avanzada

### Para Debugging
1. Consultar: **TESTING_GUIDE.md**
2. Ejecutar: `python setup_validation.py`
3. Ver: **GIT_DEVELOPER_GUIDE.md** si hay issues de commit

### Para Arquitectura
- Referencia: **BIBLIA_v1.md** (histórico + decisiones)
- Referencia: **app/README.md** (modular)

---

## API Documentation (Interactiva)

Cuando corre la aplicación:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Variables de Entorno

**Inicio rápido:**
- Copiar: `.env.example` → `.env`
- Editar: `OPENAI_API_KEY` y `DATABASE_URL`
- Referencia: Ver [`ENV_REFERENCE.md`](./ENV_REFERENCE.md)

**Referencia completa:** Ver [`.env.standard`](./.env.standard)

---

## Estado del Proyecto

✅ **100% Completado** - Production Ready

- ✅ FastAPI backend con 3 endpoints
- ✅ RAG pipeline (PDF + Image)
- ✅ PostgreSQL + pgvector
- ✅ Testing completo
- ✅ Documentación exhaustiva
- ✅ Variables de entorno estandarizadas
- ✅ 0 secretos expuestos

---

*Last Updated: 2025-12-01*
- Error handling patterns
- Deployment en VPS

**Plantillas:** `n8n_workflows/templates/`

## Cómo Navegar la Documentacion

1. **Entender arquitectura:** Lee este archivo + context-transfer.yml
2. **Setup local:** Sigue instrucciones en app/README.md y frontend/README.md
3. **Crear tablas BD:** Consulta smartops_data/README.md
4. **Configurar workflows:** Sigue n8n_workflows/README.md
5. **Integrar todo:** Revisa flujo en context-transfer.yml seccion "INFRASTRUCTURE_STRATEGY"

## Variables de Entorno Clave

```bash
# Backend
DATABASE_URL=postgresql://root:password@db_core:5432/smartops_core
OPENAI_API_KEY=sk-...
N8N_WEBHOOK_URL=http://n8n:5678/webhook/smartops

# Frontend
API_URL=http://api_core:8000

# Database
DB_PASSWORD=...

# VPS SSH Tunnel
REMOTE_HOST=your-vps.com
REMOTE_USER=root
SSH_PORT=22
```

## Ports Homologados

```
8000  -> FastAPI Backend
8001  -> FastAPI Backend (Docker external)
8501  -> Streamlit UI
5432  -> PostgreSQL (internal)
5433  -> PostgreSQL (external)
5678  -> n8n (VPS)
3000  -> Waha (VPS)
```

## Comandos Utiles

```bash
# Ver logs del backend
docker logs -f smartops_core_api

# Ver logs de BD
docker logs -f smartops_core_db

# Conectar a BD
docker exec -it smartops_core_db psql -U root -d smartops_core

# Rebuild containers
docker-compose down && docker-compose build && docker-compose up

# Ver health del sistema (desde SmartOps UI)
# Acceder a http://localhost:8501 -> System Health
```

## Proximo Paso: Paso 2 - VPS Provisioning

Consulta context-transfer.yml seccion "NEXT_STEPS_ROADMAP" para:
1. SSH al VPS
2. Crear SWAP de 4GB
3. Instalar Docker & Docker Compose
4. Clonar repo
5. Configurar .env productivo
6. Establecer SSH reverse tunnel

---

Generado: 01-Dic-2025
Proyecto: SmartOps Core v2.0.0 (Dockerized Modular Architecture)
