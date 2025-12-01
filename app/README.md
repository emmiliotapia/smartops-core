# SmartOps Core Backend API

## Descripcion
Cerebro semantico del sistema SmartOps. Procesa intenciones del usuario, ejecuta RAG (Retrieval-Augmented Generation), y orquesta acciones a traves de n8n.

## Estructura

```
app/
├── main.py              # Punto de entrada FastAPI
├── requirements.txt     # Dependencias Python
├── core/               # Logica de Nucleo (Semantic Engine, RAG)
│   ├── __init__.py
│   ├── biblia.py       # Motor de reglas y logica de negocio
│   └── rag.py          # Vector retrieval & context building
├── routers/            # Endpoints organizados por funcionalidad
│   ├── __init__.py
│   ├── semantic.py     # POST /semantic-engine/execute
│   ├── documents.py    # CRUD de documentos para RAG
│   └── webhooks.py     # Webhooks entrantes de n8n
└── services/           # Servicios transversales
    ├── __init__.py
    ├── database.py     # Conexion a PostgreSQL + pgvector
    ├── openai_client.py # Integraciones con LLM
    └── n8n_dispatcher.py # Envio de acciones a n8n
```

## Endpoints Principales

### POST /semantic-engine/execute
Ejecuta la logica semantica sobre una intencion del usuario.

**Request:**
```json
{
  "intent": "enviar_reporte_ventas",
  "parameters": {
    "tenant_id": "acme-corp-001",
    "fecha_inicio": "2025-01-01",
    "fecha_fin": "2025-01-31",
    "canal": "whatsapp"
  }
}
```

**Response:**
```json
{
  "status": "processed",
  "decision": "Accion enviada a n8n",
  "n8n_dispatched": true,
  "workflow_id": "wf_sales_report_v2",
  "execution_id": "exec_abc123xyz"
}
```

### POST /documents/ingest
Ingesta documentos para RAG (PDFs, TXTs, JSONs).

**Request:** multipart/form-data
- file: Documento a procesar
- tenant_id: Identificador del inquilino
- metadata: JSON con tags/categoria

**Response:**
```json
{
  "document_id": "doc_xyz789",
  "vectors_created": 250,
  "status": "indexed"
}
```

## Modelos Pydantic

### ActionPayload
```python
from pydantic import BaseModel
from typing import Optional, Dict

class ActionPayload(BaseModel):
    intent: str                    # e.g., "enviar_reporte", "guardar_contacto"
    parameters: Dict[str, any]    # Parametros dinamicos por intencion
    tenant_id: str                # Multi-tenant identifier
    source: Optional[str] = "webhook"  # Origen: webhook, ui, api, etc.
```

## Flujo de Procesamiento

```
1. Usuario envia intencion via WhatsApp → Waha (VPS)
   |
2. Waha → n8n Webhook (VPS) → Reverse SSH Tunnel
   |
3. Llega a FastAPI (Local): POST /semantic-engine/execute
   |
4. Semantic Engine:
   - Validar intencion
   - Recuperar contexto (RAG)
   - Llamar LLM si es necesario
   - Generar plan de acciones
   |
5. Despachar a n8n: {"action": "...", "params": {...}}
   |
6. n8n ejecuta nodo final
```

## Desarrollo Local

**Instalar dependencias:**
```bash
cd app
pip install -r requirements.txt
```

**Correr servidor:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Acceder a documentacion:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Variables de Entorno Requeridas

```
DATABASE_URL=postgresql://root:password@db_core:5432/smartops_core
OPENAI_API_KEY=sk-...
N8N_WEBHOOK_URL=http://n8n:5678/webhook/smartops
```

## Checklist de Seguridad

- [ ] Validar tenant_id en cada request
- [ ] Rate-limiting en /semantic-engine/execute
- [ ] Encriptar credenciales en .env
- [ ] CORS configurado solo para n8n y Streamlit
- [ ] Logging de todas las ejecuciones
