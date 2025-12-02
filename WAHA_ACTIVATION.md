# 🤖 WAHA ACTIVATION - WHATSAPP REAL

**Objetivo:** Conectar WhatsApp real via Waha → n8n → Túnel SSH → Tu PC FastAPI  
**Duración estimada:** 20-30 minutos  
**Status:** 🟡 EN PROCESO

---

## 🔌 PASO 1: Verificar Contenedor Waha

### En VPS Terminal:

```bash
# Accede al VPS (si aún no estás)
ssh smartops@164.92.110.179

# Verifica que Waha está corriendo
docker compose ps | grep smartops-whatsapp

# Expected output:
# smartops-whatsapp   devlikeapro/waha   /usr/bin/tini -- /...   Up 6 hours   0.0.0.0:3000->3000/tcp
```

**Status:** [ ] COMPLETADO

**Output:**
```
[Paste output here]
```

---

## 📱 PASO 2: Acceder Dashboard Waha

### En tu navegador:

1. **Abre:** `http://164.92.110.179:3000/dashboard`
2. **Login:** 
   - Usuario: `admin`
   - Contraseña: `admin` (si no lo cambiaste)

**Expected:**
- Ves página de dashboard
- Opción para "Add Device" o "Create Session"

**Status:** [ ] COMPLETADO

**Screenshot o confirmación:**
```
[Describe what you see]
```

---

## 📲 PASO 3: Escanear QR de WhatsApp

### En Dashboard Waha:

1. Haz click en **"Create New Session"** o **"Add Device"**
2. Escoge el nombre: `default`
3. Haz click en **"Generate QR"**
4. Con tu teléfono (el que será HOST), abre WhatsApp
5. Ve a **Settings → Linked Devices → Link a Device**
6. **Escanea el código QR** que aparece en el dashboard
7. **Espera:** El estado debe cambiar a **"CONNECTED"** o **"ACTIVE"**

**⏱️ Tiempo esperado:** 30-60 segundos

**Status:** [ ] COMPLETADO

**Confirmación:**
```
Código QR escaneado: [SÍ / NO]
Estado en Dashboard: ___________________
Teléfono conectado: [SÍ / NO]
```

---

## 🔗 PASO 4: Configurar Webhook (Waha → n8n)

### En Dashboard Waha - Sección Sesión `default`:

1. **Busca "Webhook URL"** o **"Configuration"**
2. **URL a poner:**
   ```
   http://smartops-n8n:5678/webhook/demo-message
   ```
   (Esto es URL **INTERNA** de Docker, no la pública)

3. **Eventos a capturar:**
   ```
   message.any  (captura TODOS los mensajes entrantes)
   ```

4. **Guarda cambios**

**Status:** [ ] COMPLETADO

**Confirmación:**
```
Webhook URL configurada: [SÍ / NO]
URL exacta: ________________________________________
Eventos: [message.any / otro]
```

---

## 🧠 PASO 5: Verificar n8n Workflow

### En navegador:

1. **Abre:** `http://164.92.110.179:5678`
2. **Login:** (credenciales que estableciste)
3. **Busca** un workflow llamado **"Demo Comercial V1"**

**Si NO existe**, necesitamos crear uno:

### Crear Workflow "Demo Comercial V1":

**Node 1 - Webhook (Listener):**
```
- Type: Webhook
- Method: POST
- Path: /webhook/demo-message
- Authentication: None
```

**Node 2 - Transform (Parse Message):**
```javascript
{
  "session_id": "{{ $json.body.from }}",
  "message": "{{ $json.body.body }}"
}
```

**Node 3 - HTTP Request (Send to Local API):**
```
- Method: POST
- URL: http://localhost:8001/demo/message
  (Via SSH tunnel, activo desde tu PC)
- Headers: Content-Type: application/json
- Body: {{ $json }}
```

**Node 4 - Response Node:**
```
- Return: {{ $node["HTTP Request"].json }}
```

**Connect:** Node 1 → 2 → 3 → 4

**SAVE + ACTIVATE** (should turn green)

**Status:** [ ] COMPLETADO

**Confirmación:**
```
Workflow encontrado: [SÍ / NO]
Si lo creaste:
  - Node 1 (Webhook): [✓ / ✗]
  - Node 2 (Transform): [✓ / ✗]
  - Node 3 (HTTP): [✓ / ✗]
  - Node 4 (Response): [✓ / ✗]
  - Workflow ACTIVADO: [SÍ / NO]
```

---

## 💻 PASO 6: Setup en Tu PC Local

### Terminal 1 - FastAPI:

```bash
# En tu PC
python start.py

# Expected:
# INFO: Uvicorn running on http://0.0.0.0:8001
# INFO: Application startup complete
```

**Status:** [ ] COMPLETADO

---

### Terminal 2 - SSH Tunnel (IMPORTANTE):

```bash
# En tu PC (terminal NUEVA)
ssh -R 8001:localhost:8001 smartops@164.92.110.179

# Expected:
# (SSH prompt, conexión abierta)
# Mantén esto ABIERTO durante todo el testing
```

**⚠️ CRÍTICO:** No cierres este terminal. Es el puente entre VPS y tu PC.

**Status:** [ ] COMPLETADO

---

### Terminal 3 - Monitoring (Opcional):

```bash
# En tu PC (terminal NUEVA) - para ver logs
ssh smartops@164.92.110.179
docker logs -f smartops-n8n

# Esto mostrará los logs de n8n en tiempo real
```

**Status:** [ ] COMPLETADO

---

## 🧪 PASO 7: Test Manual (Curl)

### Desde Terminal en VPS (Terminal 2):

```bash
# Test: Enviar un mensaje fake al webhook
curl -X POST http://localhost:5678/webhook/demo-message \
  -H "Content-Type: application/json" \
  -d '{
    "body": {
      "from": "+56912345678",
      "body": "¿Qué tienen de costillas?"
    }
  }'

# Expected response:
# { "message": "Se consultó exitosamente", "data": {...} }
```

**¿Qué pasa internamente?**
1. Waha recibe el mensaje fake
2. Envía POST a n8n webhook
3. n8n transforma el JSON
4. n8n hace POST a http://localhost:8001/demo/message (vía túnel)
5. Tu FastAPI responde
6. n8n devuelve la respuesta

**Status:** [ ] COMPLETADO

**Output:**
```
[Paste the curl response here]
```

**Verificar logs:**
```bash
# En Terminal 3 (monitoring):
# Deberías ver en logs de n8n algo como:
# [Node "Webhook"] received POST
# [Node "Transform"] executed
# [Node "HTTP Request"] sent to http://localhost:8001/demo/message
# [Node "Response"] returned 200
```

---

## 📲 PASO 8: Test Real (WhatsApp)

### Envía un mensaje de verdad:

1. **Desde tu teléfono** (o de un amigo), abre WhatsApp
2. **Busca el contacto** que configuraste como HOST en Waha (el número conectado)
3. **Envía un mensaje de prueba:**
   ```
   ¿Qué tienen de costillas?
   ```

4. **Espera respuesta** (máximo 5 segundos)

**¿Qué debería pasar?**
1. Waha recibe el mensaje real
2. Envía webhook a n8n
3. n8n transforma + envía a tu API
4. Tu API consulta PostgreSQL
5. Respuesta vuelve por el túnel
6. n8n responde a Waha
7. Waha envía respuesta de vuelta por WhatsApp

**Status:** [ ] COMPLETADO

**Resultado:**
```
Mensaje enviado: [SÍ / NO]
Respuesta recibida: [SÍ / NO]
Tiempo de respuesta: ___ segundos
Contenido de respuesta: ____________________________
```

---

## 🐛 TROUBLESHOOTING

### Error: "Connection refused" en curl

```bash
# Verifica que Waha está corriendo
docker compose ps | grep smartops-whatsapp

# Si no está:
docker compose up -d smartops-whatsapp
docker compose logs smartops-whatsapp
```

### Error: Webhook no recibe mensajes

```bash
# Verifica que el webhook está configurado
docker exec smartops-whatsapp curl http://localhost:3000/api/sessions/default

# Deberías ver la configuración del webhook en la respuesta
```

### Error: n8n no responde

```bash
# Verifica que está corriendo
docker ps | grep n8n

# Ve logs
docker logs smartops-n8n

# Si problema persiste:
docker restart smartops-n8n
```

### Error: SSH Tunnel no funciona

```bash
# Verifica que el túnel está activo
# En Terminal 2, deberías ver prompt de SSH

# Si falla: Reconecta
ssh -R 8001:localhost:8001 smartops@164.92.110.179

# Verifica desde VPS que funciona:
curl http://localhost:8001  # Debería responder
```

### Error: FastAPI no responde

```bash
# En tu PC:
# Verifica que start.py está corriendo
# Debería ver: "Uvicorn running on http://0.0.0.0:8001"

# Si no:
python start.py

# Verifica que está escuchando:
curl http://localhost:8001
```

---

## 📊 CHECKLIST FINAL

```
[ ] Paso 1: Waha verificado en VPS
[ ] Paso 2: Dashboard Waha accesible
[ ] Paso 3: QR escaneado, teléfono conectado
[ ] Paso 4: Webhook configurado en Waha
[ ] Paso 5: n8n workflow existente y ACTIVE
[ ] Paso 6: FastAPI corriendo en tu PC
[ ] Paso 7: SSH Tunnel abierto y funcionando
[ ] Paso 8: Curl test manual exitoso
[ ] Paso 9: WhatsApp test real exitoso
```

---

## ✅ ÉXITO = ...

Cuando veas:
1. **Dashboard Waha** muestra "CONNECTED"
2. **n8n workflow** está en estado "ACTIVE" (verde)
3. **Curl test** devuelve respuesta JSON
4. **WhatsApp test** recibe respuesta en < 5 segundos

**🎉 ESTÁS LISTO PARA LA DEMO CON MARTÍN**

---

## 🔄 SIGUIENTE PASO

Cuando completes estos pasos, reporta en Telegram:

```
✅ Paso X completado
[Output o confirmación]
```

Y pasamos al siguiente. 👇
