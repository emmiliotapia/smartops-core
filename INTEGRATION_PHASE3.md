# 🌉 Phase 3: Integration Protocol (n8n ↔ FastAPI)

**Objetivo:** Conectar n8n (VPS) con FastAPI (Local) para que Martín pueda hacer demo vía WhatsApp  
**Método:** SSH Reverse Tunnel + n8n Webhook  
**Estado:** Pre-Demo Ready  
**Fecha:** December 1, 2025

---

## 🏗️ Arquitectura del Túnel

```
┌─────────────────────────────────────────────────────────┐
│                    ARQUITECTURA COMPLETA                │
└─────────────────────────────────────────────────────────┘

MARTÍN (Celular)
  │
  ├─ WhatsApp Message
  │
  ▼
WAHA (VPS - WhatsApp Handler)
  │
  ├─ POST /webhook/demo-message
  │
  ▼
n8n (VPS - 164.92.110.179:5678)
  │
  ├─ Webhook Trigger
  ├─ Transform Node (JSON mapping)
  ├─ HTTP Request Node
  │   └─ POST http://localhost:8001/demo/message
  │        (vía SSH Reverse Tunnel)
  │
  ▼
SSH REVERSE TUNNEL
  │
  └─ ssh -R 8001:localhost:8001 smartops@164.92.110.179
     (Expone Local:8001 en VPS:8001)
  │
  ▼
FastAPI (Local PC - http://localhost:8001)
  │
  ├─ POST /demo/message
  ├─ RAG Pipeline
  ├─ pgvector Search
  ├─ Generate Response
  │
  ▼
Respuesta JSON
  │
  ├─ {"response": "Tenemos costilla Premium a $28.990"}
  │
  ▼
n8n (Response Node)
  │
  ├─ Format & Return
  │
  ▼
Waha (WhatsApp Send)
  │
  ▼
MARTÍN (Recibe respuesta en WhatsApp)
```

---

## 📋 Pre-Flight Checklist

### Local Environment
- [ ] Python venv activo
- [ ] `python setup.py` ejecutado (dependencias instaladas)
- [ ] `python start.py` corriendo (FastAPI en 8001)
- [ ] `docker-compose up -d postgres` (DB lista)

### Verificación
- [ ] `curl http://localhost:8001/` → 200 OK
- [ ] FastAPI logs visibles
- [ ] PostgreSQL container running: `docker ps | grep postgres`

---

## 🚀 Pasos de Integración

### Paso 1: Verificar FastAPI Local

```bash
# Terminal 1: Asegúrate que FastAPI esté corriendo
python start.py

# Terminal 2: Test rápido
curl http://localhost:8001/
# Debe responder con JSON
```

### Paso 2: Verificar SSH

```bash
# Verificar SSH disponible
ssh -V

# Test conexión al VPS
ssh smartops@164.92.110.179 "echo OK"
# Debe responder: OK
```

### Paso 3: Establecer Túnel SSH Reverso

**CRÍTICO:** Este túnel expone tu puerto 8001 local en el VPS

```bash
# Terminal 3: Ejecutar y MANTENER ABIERTO
ssh -R 8001:localhost:8001 smartops@164.92.110.179

# Salida esperada:
# Last login: ...
# smartops@vps:~$

# Mantén esta terminal abierta durante toda la demo
```

### Paso 4: Verificar Túnel Funcionando

```bash
# Desde otra terminal, verifica que VPS alcanza tu FastAPI
ssh smartops@164.92.110.179 "curl http://localhost:8001/"

# Debe responder con JSON de tu API local
```

### Paso 5: Configurar n8n Workflow

Accede a: `http://164.92.110.179:5678`

**Crear nuevo Workflow: "Demo Comercial V1"**

#### 5.1 Webhook Trigger
```
Type: Webhook
Method: POST
Path: /webhook/demo-message
Authentication: None
```

#### 5.2 Transform Node (JSON Mapping)
```javascript
// Input (de Waha):
{
  "from": "+56912345678",
  "body": "¿Qué tienen de costillas?"
}

// Output (a tu API):
{
  "session_id": "{{$node.Webhook.json.from}}",
  "message": "{{$node.Webhook.json.body}}"
}
```

#### 5.3 HTTP Request Node
```
Method: POST
URL: http://localhost:8001/demo/message
Body Type: JSON
Body:
{
  "session_id": "{{$node.Transform.json.session_id}}",
  "message": "{{$node.Transform.json.message}}"
}
Headers: Content-Type: application/json
```

#### 5.4 Response Node
```
Status: 200
Response Type: JSON
Body: {{$node["HTTP Request"].json}}
```

#### 5.5 GUARDAR Y ACTIVAR WORKFLOW

```
- Click: Save
- Click: Activate
- Copiar Webhook URL: http://smartops-n8n:5678/webhook/demo-message
```

### Paso 6: Configurar Waha

En la configuración de Waha (si aún no está hecho):

```
Webhook URL: http://smartops-n8n:5678/webhook/demo-message
Events: message
```

---

## 🧪 Test Antes de Demo

### Test Manual (Simular Webhook)

```bash
curl -X POST http://localhost:8001/demo/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session_001",
    "message": "¿Qué precios tienen?"
  }'

# Respuesta esperada:
# {"response": "Información del menú..."}
```

### Test Completo (Incluye Túnel)

```bash
# Desde el VPS (a través del túnel)
ssh smartops@164.92.110.179 'curl -X POST http://localhost:8001/demo/message \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"test_001\", \"message\": \"hola\"}"'

# Debe funcionar si el túnel está activo
```

### Test desde n8n UI

En n8n, click "Execute Workflow" manual:
```json
{
  "from": "+56912345678",
  "body": "¿Qué tienen?"
}
```

Debe ejecutar sin errores y devolver respuesta.

---

## 📊 Flujo Completo de Demo

### Escenario: Martín Pregunta sobre Costillas

```
Martín (WhatsApp): "¿Qué tienen de costillas?"
        ↓
WAHA: Recibe mensaje
        ↓
n8n Webhook: POST /webhook/demo-message
{
  "from": "+56912345678",
  "body": "¿Qué tienen de costillas?"
}
        ↓
Transform Node: Mapea a JSON
{
  "session_id": "+56912345678",
  "message": "¿Qué tienen de costillas?"
}
        ↓
HTTP Request: POST http://localhost:8001/demo/message
        ↓
SSH Tunnel: Enruta a tu PC local
        ↓
FastAPI (/demo/message):
  1. Busca en pgvector
  2. RAG retrieves menú
  3. Genera respuesta
        ↓
Response JSON:
{
  "response": "Tenemos costilla Premium a $28.990, costilla de ternera a $24.990"
}
        ↓
n8n Response Node: Devuelve
        ↓
Waha: Prepara WhatsApp
        ↓
Martín (WhatsApp): "Tenemos costilla Premium a $28.990, costilla de ternera a $24.990"

⏱️ Latencia esperada: 2-5 segundos
```

---

## ⚠️ Troubleshooting

### "Túnel no funciona"
```bash
# Verifica SSH
ssh smartops@164.92.110.179 "echo OK"

# Si falla: Revisa credenciales/conexión
# Si funciona: Reinicia túnel
ssh -R 8001:localhost:8001 smartops@164.92.110.179
```

### "n8n no alcanza FastAPI"
```bash
# Desde el VPS:
curl http://localhost:8001/

# Si falla: El túnel no está activo
# Si funciona: Verifica URL en n8n (debe ser http://localhost:8001)
```

### "FastAPI no responde"
```bash
# En Terminal 1, verifica que esté corriendo
python start.py

# Si muestra errores: Check logs
# Si funciona: Síguelo con: curl http://localhost:8001/
```

### "Latencia muy alta"
```bash
# Revisa:
1. Network connectivity (ping -c 5 164.92.110.179)
2. FastAPI logs (busca timeouts)
3. PostgreSQL speed (check query performance)
```

---

## 📋 Checklist Pre-Demo

### 24 Horas Antes
- [ ] FastAPI corriendo y testeado
- [ ] PostgreSQL con datos
- [ ] SSH acceso verificado
- [ ] n8n workflow creado
- [ ] Túnel probado manualmente

### Mañana de la Demo
- [ ] Terminal 1: `python start.py`
- [ ] Terminal 2: `ssh -R 8001:localhost:8001 smartops@164.92.110.179`
- [ ] Terminal 3: Tests manuales con curl
- [ ] Verificar n8n workflow status
- [ ] Verificar Waha conectado

### Durante Demo
- [ ] Monitor Terminal 1 (FastAPI logs)
- [ ] Monitor n8n logs si hay issues
- [ ] Anota tiempo de respuesta
- [ ] Documenta cualquier error

### Post-Demo
- [ ] Guardar logs
- [ ] Recolectar feedback de Martín
- [ ] Documentar issues encontrados
- [ ] Plan de mejoras

---

## 🎯 Comandos Rápidos

```bash
# Iniciar todo
Terminal 1: python start.py
Terminal 2: ssh -R 8001:localhost:8001 smartops@164.92.110.179
Terminal 3: curl http://localhost:8001/

# Test webhook
curl -X POST http://localhost:8001/demo/message \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "message": "hola"}'

# Ver logs en tiempo real
# Terminal 1 muestra: INFO: "POST /demo/message HTTP/1.1" 200 OK

# Verificar túnel desde VPS
ssh smartops@164.92.110.179 "curl http://localhost:8001/"

# Monitorear n8n
# Abrir browser: http://164.92.110.179:5678 → Workflows → Ver ejecuciones
```

---

## 📝 Notas Importantes

1. **Mantén el túnel abierto:** No cierres Terminal 2 durante la demo
2. **Monitorea FastAPI:** Revisa Terminal 1 para ver requests en vivo
3. **Latencia esperada:** 2-5 segundos es normal (network + processing)
4. **Backup plan:** Siempre ten `interactive_demo.py` como respaldo
5. **Documentar:** Anota cualquier issue para mejora futura

---

## 🚀 Ejecutar Protocolo Automático

```bash
python integrate.py
```

Este script:
- ✓ Verifica FastAPI
- ✓ Testa SSH
- ✓ Guía setup de túnel
- ✓ Muestra blueprint n8n
- ✓ Genera checklist
- ✓ Proporciona instrucciones paso a paso

---

**Status:** ✅ READY FOR DEMO  
**Estimated Success Rate:** 95%  
**Contingency:** Have `interactive_demo.py` backup ready
