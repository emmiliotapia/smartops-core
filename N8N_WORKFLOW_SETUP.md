# 🧠 n8n WORKFLOW SETUP - "Demo Comercial V1"

**Objetivo:** Crear workflow que reciba mensaje de Waha → transforma → envía a tu API local  
**Duración:** 10 minutos  
**Status:** 🔴 PENDIENTE

---

## 📋 PASO A PASO

### 1. En n8n Dashboard

**URL:** http://164.92.110.179:5678

**Login:**
```
Usuario: (tu email configurado)
Contraseña: (tu password)
```

**Si es la primera vez:** Se te pedirá que crees una cuenta. Úsala y guarda credenciales.

---

### 2. Crear Nuevo Workflow

En el dashboard, busca el botón:
- **"+ New Workflow"** o 
- **"Create New"** o
- Haz click en el ícono **+**

**Name:** `Demo Comercial V1`

---

### 3. Agregar Node 1: Webhook (Listener)

**En n8n:**
1. Click en "Add Node" (o hace click vacío en canvas)
2. Busca: `Webhook`
3. Selecciona: **"Webhook" (el que dice "Wait for incoming requests")**

**Configura:**
```
- Method: POST
- Path: /webhook/demo-message
- Authentication: None
- Response Code: 200
```

**Save/OK**

---

### 4. Agregar Node 2: Transform (Parse Data)

**En n8n:**
1. Click en el output del Webhook (el punto a la derecha)
2. Busca: `Transform` o `Code`
3. Selecciona: **"Function" node** o **"Transform"**

**Configura (en el campo de código):**

```javascript
return [
  {
    json: {
      "session_id": $json.body.from,
      "message": $json.body.body,
      "timestamp": new Date().toISOString()
    }
  }
];
```

**Save/OK**

---

### 5. Agregar Node 3: HTTP Request (Enviar a tu API)

**En n8n:**
1. Click en el output del Transform node
2. Busca: `HTTP`
3. Selecciona: **"HTTP Request"**

**Configura:**
```
- Method: POST
- URL: http://localhost:8001/demo/message
  (Esto funciona porque tu PC tiene SSH tunnel activo)

- Headers:
  - Content-Type: application/json

- Body:
  - Use Body: JSON
  - Body: {{ $json }}
  
- Response Format: JSON
```

**Save/OK**

---

### 6. Agregar Node 4: Response (Devolver al cliente)

**En n8n:**
1. Click en el output del HTTP Request node
2. Busca: `Respond`
3. Selecciona: **"Respond to Webhook"**

**Configura:**
```
- Response Code: 200
- Response Body: {{ $json }}
```

**Save/OK**

---

### 7. Conectar todos los nodes

**En canvas, deberías ver:**
```
Webhook (Node 1)
    ↓
Transform (Node 2)
    ↓
HTTP Request (Node 3)
    ↓
Response (Node 4)
```

Si las conexiones no están claras, haz click en los puntos output/input de cada node para conectarlos.

---

### 8. GUARDAR el Workflow

**Top izquierda:** Click en **"Save"**

**Aparecerá:**
- Un campo para guardar
- Click en **"Save"** nuevamente

**Resultado:** Workflow guardado con nombre "Demo Comercial V1"

---

### 9. ACTIVAR el Workflow

**Top derecha:** Busca el botón **"Activate"** (o toggle verde/rojo)

**Click en ACTIVATE**

**Resultado:** El workflow debe pasar a estado **ACTIVE** (debe verse verde)

---

## ✅ VERIFICACIÓN

Cuando termines, deberías ver en n8n:

```
┌─────────────────────────────────────┐
│ Demo Comercial V1                   │
│ [ACTIVE] ✅                         │
├─────────────────────────────────────┤
│                                     │
│  Webhook              Transform     │
│     ↓                    ↓          │
│    HTTP Request      Response       │
│                                     │
└─────────────────────────────────────┘
```

---

## 🧪 TEST RÁPIDO

**En VPS terminal:**

```bash
cd /opt/smartops-tools

curl -X POST http://localhost:5678/webhook/demo-message \
  -H "Content-Type: application/json" \
  -d '{
    "body": {
      "from": "+56912345678",
      "body": "Test message"
    }
  }'

# Debería devolver algo como:
# {"message":"...","data":{...}}
```

Si ves respuesta JSON: ✅ **Workflow funciona**

---

## 🆘 PROBLEMAS COMUNES

### Error: "Cannot find webhook path"

**Solución:** El workflow no está ACTIVE. Haz click en ACTIVATE.

### Error: "HTTP Request failed"

**Causa:** Tu PC no tiene SSH tunnel abierto o FastAPI no está corriendo.

**Solución:**
- Terminal 1 (tu PC): `python start.py`
- Terminal 2 (tu PC): `ssh -R 8001:localhost:8001 smartops@164.92.110.179`

### Error: "Transform node failed"

**Causa:** El payload de Waha es diferente al esperado.

**Solución:** Ve a Terminal 2 (n8n logs) y verifica qué estructura recibe:
```bash
# En VPS, en otra terminal:
docker logs -f smartops-n8n
```

---

## 📝 CHECKLIST

```
[ ] n8n accesible en http://164.92.110.179:5678
[ ] Logged in a n8n
[ ] Nuevo workflow: "Demo Comercial V1"
[ ] Node 1 - Webhook: Configurado
[ ] Node 2 - Transform: Configurado
[ ] Node 3 - HTTP Request: Configurado
[ ] Node 4 - Response: Configurado
[ ] Todos conectados: Webhook → Transform → HTTP → Response
[ ] Workflow SAVED
[ ] Workflow ACTIVATED (estado verde)
[ ] curl test exitoso
```

---

**SIGUIENTE:** Cuando confirmes que está todo listo, pasamos a configurar Waha webhook.

👇 **Reporta cuando hayas completado esto.**
