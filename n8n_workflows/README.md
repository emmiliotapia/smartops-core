# n8n Workflows | Orquestacion de Acciones

## Descripcion
Flujos de automatizacion que reciben decisiones del Semantic Engine (FastAPI) y ejecutan acciones:
- Enviar mensajes WhatsApp
- Guardar datos en BD
- Llamar APIs externas
- Procesar archivos
- Generar reportes

## Estructura

```
n8n_workflows/
├── README.md
├── workflows/
│   ├── send_whatsapp_message.json      # Enviar mensaje por WhatsApp
│   ├── save_contact.json               # Guardar/actualizar contacto
│   ├── generate_sales_report.json      # Generar reporte de ventas
│   └── webhook_trigger.json            # Webhook entrante principal
├── credentials/
│   ├── openai.json                     # Config OpenAI
│   ├── whatsapp_waha.json              # Config Waha
│   └── postgres.json                   # Conexion BD
└── templates/
    ├── webhook_payload_template.json   # Formato de payload esperado
    └── response_template.json          # Respuesta del semantic-engine
```

## Flujo General

```
WhatsApp User
    |
Waha (VPS) → Receives message
    |
n8n Webhook (VPS) → Parses message
    |
FastAPI (Local) → /semantic-engine/execute
    |
Semantic Engine → Decide action
    |
n8n Workflow Node → Execute (send msg, save data, etc.)
    |
Response to user
```

## Webhook Endpoint en n8n

**Configuracion en n8n:**

1. Crear un nuevo workflow
2. Agregar nodo Webhook (entrada)
3. Configurar:
   - URL: http://your-n8n:5678/webhook/smartops-main
   - Method: POST
   - Auth: API Key (en SmartOps backend)

## Payload de Entrada (desde SmartOps Core)

**POST /webhook/smartops-main**

```json
{
  "action": "send_whatsapp_message",
  "tenant_id": "acme-corp-001",
  "parameters": {
    "recipient": "+5491123456789",
    "message": "Hola! Tu reporte esta listo.",
    "media_url": "https://..."
  },
  "execution_id": "exec_abc123xyz"
}
```

## Workflows Clave

### 1. send_whatsapp_message.json
Envia mensaje por WhatsApp usando Waha.

**Nodos:**
1. Webhook (entrada)
2. HTTP Request → Waha API
3. Update Execution (marcar como completado)
4. Response

### 2. save_contact.json
Guarda/actualiza contacto en BD.

**Nodos:**
1. Webhook (entrada)
2. PostgreSQL Node → INSERT/UPDATE
3. Trigger next workflow si es necesario
4. Response

### 3. generate_sales_report.json
Genera reporte de ventas dinamico.

**Nodos:**
1. Webhook (entrada)
2. HTTP Request → Query datos
3. Aggregate & Format (convertir a tabla)
4. Export to PDF/Excel
5. Upload result
6. Send link to user

## Credenciales (En n8n UI)

### OpenAI
```
API Key: sk-...
Model: gpt-4-turbo
```

### Waha (WhatsApp)
```
Base URL: http://waha:3000
API Key: tu-api-key-waha
```

### PostgreSQL
```
Host: smartops_core_db (local via SSH tunnel)
User: root
Password: ${DB_PASSWORD}
Database: smartops_core
Port: 5432 (internamente), 5433 (externamente desde VPS)
```

## Testing Workflows

**Opcion 1: Desde n8n UI**
1. Abrir workflow
2. Click en "Test"
3. Completar datos de prueba
4. Click "Execute"

**Opcion 2: Desde SmartOps Admin (Streamlit)**
- Panel "Webhooks" → Simular payload

**Opcion 3: Desde terminal (curl)**
```bash
curl -X POST http://localhost:5678/webhook/smartops-main \
  -H "Content-Type: application/json" \
  -d '{
    "action": "send_whatsapp_message",
    "parameters": {"recipient": "+549...", "message": "Test"}
  }'
```

## Variables Globales en n8n

```javascript
// Configurar en n8n Settings → Variables
WAHA_BASE_URL = "http://waha:3000"
SEMANTIC_ENGINE_URL = "http://localhost:8000" (via SSH tunnel)
POSTGRES_HOST = "smartops_core_db"
OPENAI_API_KEY = "sk-..."
```

## Error Handling

**Patron en cada workflow:**

```
Nodo Principal
    | SUCCESS
    └→ Log to DB + Notify user
    | ERROR
    └→ Retry (3 veces)
       └→ Still error?
           └→ Send alert to admin
           └→ Log error in Execution table
```

## Monitoreo

**Ver ejecuciones en n8n:**
1. Abrir workflow
2. Tab "Executions"
3. Filtrar por estado/fecha

**Integracion con SmartOps Admin:**
- Los logs tambien se guardan en tabla executions de PostgreSQL
- Streamlit panel muestra historial centralizado

## Ciclo de Vida de un Workflow

1. **Trigger**: Webhook recibe payload
2. **Transform**: Validar y estructurar datos
3. **Execute**: Accion principal (send msg, save data, etc.)
4. **Response**: Confirmar a SmartOps backend
5. **Log**: Guardar en DB para auditoria

## Deployment en VPS

```bash
# En VPS DigitalOcean:
docker pull n8nio/n8n:latest
docker run -d \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=SecurePass \
  n8nio/n8n
```

Luego:
1. Acceder a http://your-vps:5678
2. Setup inicial
3. Importar workflows (archivos .json)
4. Configurar credenciales
5. Activar workflows
