# ⚡ QUICK START - WAHA ACTIVATION

**TL;DR:** Los 5 comandos que necesitas ejecutar ahora.

---

## 🚀 ANTES DE EMPEZAR

**Tienes 3 terminales abiertas:**

### Terminal 1: FastAPI (Tu PC)
```bash
python start.py
# Escucha en http://localhost:8001
```

### Terminal 2: SSH Tunnel (Tu PC)
```bash
ssh -R 8001:localhost:8001 smartops@164.92.110.179
# Mantén esto ABIERTO. Es el puente.
```

### Terminal 3: VPS Shell (Tu PC)
```bash
ssh smartops@164.92.110.179
# Para ejecutar comandos en VPS
```

---

## 📋 CHECKLIST EN ORDEN

### 1. VPS: Verificar Waha

```bash
# Terminal 3 (VPS)
docker compose ps | grep smartops-whatsapp
# Debe estar UP, puerto 3000
```

### 2. Browser: Dashboard Waha

```
Abre: http://164.92.110.179:3000/dashboard
Login: admin / admin
Acción: Create Session "default"
QR: Escanea con tu teléfono
Estado: Espera "CONNECTED"
```

### 3. Browser: Configurar Webhook

```
En Dashboard Waha → Sesión "default"
Webhook URL: http://smartops-n8n:5678/webhook/demo-message
Events: message.any
Save
```

### 4. Browser: n8n Workflow

```
Abre: http://164.92.110.179:5678
Busca workflow: "Demo Comercial V1"
Si no existe: Créalo (ver WAHA_ACTIVATION.md)
Estado: ACTIVE (debe estar verde)
```

### 5. VPS: Test Manual

```bash
# Terminal 3 (VPS)
curl -X POST http://localhost:5678/webhook/demo-message \
  -H "Content-Type: application/json" \
  -d '{"body": {"from": "+56912345678", "body": "Test"}}'

# Debe devolver JSON
```

### 6. WhatsApp Real

```
Desde tu teléfono: Envía un mensaje
Al número configurado en Waha
Espera respuesta (< 5 seg)
```

---

## 🔍 VERIFICAR CADA PARTE

| Componente | Comando | OK? |
|-----------|---------|-----|
| **Waha** | `curl http://164.92.110.179:3000/sessions` | [ ] |
| **n8n** | `curl http://164.92.110.179:5678` | [ ] |
| **FastAPI** | `curl http://localhost:8001` | [ ] |
| **SSH Tunnel** | `ssh -R 8001:localhost:8001 smartops@164.92.110.179` | [ ] |

---

## 🆘 SI ALGO FALLA

### Waha no responde
```bash
docker compose restart smartops-whatsapp
docker compose logs smartops-whatsapp
```

### n8n no responde
```bash
docker compose restart smartops-n8n
docker compose logs smartops-n8n
```

### FastAPI no responde
```bash
# En Terminal 1
python start.py
```

### SSH Tunnel falla
```bash
# En Terminal 2
ssh -R 8001:localhost:8001 smartops@164.92.110.179
```

---

## ✅ CUANDO TODO FUNCIONE

Deberías ver:
- ✅ Dashboard Waha → Estado "CONNECTED"
- ✅ n8n Workflow → Estado verde "ACTIVE"
- ✅ curl test → Devuelve respuesta JSON
- ✅ WhatsApp → Respuesta en < 5 segundos

---

## 📖 DOCUMENTACIÓN COMPLETA

Para detalles: Ver **WAHA_ACTIVATION.md**

**EMPECEMOS!** 🚀
