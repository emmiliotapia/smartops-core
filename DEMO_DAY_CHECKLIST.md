# ✅ DEMO DAY - Operaciones Minuto a Minuto

**Fecha:** [Demo Date]  
**Hora:** [Demo Time]  
**Durán:** 15-20 minutos  
**Participantes:** Emilio (Coder), Martín (Evaluador)

---

## 📋 T-60 MIN (1 Hora Antes)

```
□ Revisar este documento
□ Revisar INTEGRATION_PHASE3.md
□ Revisar DEMO_SCRIPT_MARTIN.md
□ Preparar 3 preguntas de backup para probar
□ Revisar logs esperados
□ Verificar battery/power en PC (no crashes!)
```

---

## ⚙️ T-30 MIN (30 Min Antes)

### Terminal 1: FastAPI

```bash
# Terminal 1 - DEJAR ABIERTO
python start.py

# Esperar:
# INFO: Application startup complete
```

**Checklist:**
```
□ Ningún error en startup
□ Logs visibles y legibles
□ Puertos limpios (netstat -an | grep 8001)
□ Base de datos conectada
```

### Terminal 2: SSH Tunnel

```bash
# Terminal 2 - DEJAR ABIERTO
ssh -R 8001:localhost:8001 smartops@164.92.110.179

# Esperar:
# smartops@vps:~$
# (Se queda conectado)
```

**Checklist:**
```
□ SSH conectado sin errores
□ Terminal 2 no muestra activity (normal)
□ No cierres esta terminal!
```

### Terminal 3: Verificación

```bash
# Terminal 3 - TESTING
# Test local
curl http://localhost:8001/

# Test vía túnel (desde VPS)
ssh smartops@164.92.110.179 "curl http://localhost:8001/"

# Ambos deben responder con JSON
```

**Checklist:**
```
□ Local response: 200 OK
□ Tunnel response: 200 OK
□ JSON valido
□ Sin errors de conectividad
```

### Browser: n8n

```
Abrir: http://164.92.110.179:5678
Workflow: Demo Comercial V1
Estado: ACTIVE (debe estar verde)
```

**Checklist:**
```
□ Workflow visible
□ Status: Active
□ Sin errores en historial
```

---

## 🧪 T-10 MIN (10 Min Antes)

### Test Manual de Webhook

```bash
# Terminal 3: Simular webhook
curl -X POST http://localhost:8001/demo/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_preprueba",
    "message": "¿Qué tienen de costillas?"
  }'

# Esperar respuesta JSON:
# {"response": "..."}
```

**Checklist:**
```
□ Response recibido en < 5 seg
□ JSON válido
□ Terminal 1 mostró POST request
□ Sin errores de autenticación
```

### Confirmación WhatsApp

```
Enviar desde tu celular al número de prueba:
"Hola! Sistema de prueba"

Esperar:
- Recibir respuesta en 3-5 seg
- Respuesta debe ser del sistema (no error)
```

**Checklist:**
```
□ Mensaje llegó al sistema
□ Respuesta recibida en WhatsApp
□ Tiempo aceptable
□ No hay mensajes de error
```

---

## 🟢 T-0 MIN (DEMO INICIA)

### Setup Física

```
□ Martín con su celular listo
□ Emilio con 3 terminals visibles
□ Monitor/Screen compartido (si zoom call)
□ Chat/Email abierto para feedback
```

### Ambiente Digital

```
□ Terminal 1: FastAPI logs (limpio, scrolled to bottom)
□ Terminal 2: SSH Tunnel (silencioso, conectado)
□ Terminal 3: Listo para tests manuales si es necesario
□ Browser: n8n workflow page
```

### Rol de Emilio

```
- Esperar instrucciones de Martín
- Explicar qué está pasando
- Monitor los logs en vivo
- Ready para troubleshoot si es necesario
```

### Rol de Martín

```
- Enviar 3 mensajes WhatsApp
- Evaluar respuestas
- Dar feedback
- Hacer preguntas
```

---

## 📊 DURANTE DEMO (Timeline)

### 0:00-1:00 min: Introducción

```
□ Emilio explica el sistema (ver DEMO_SCRIPT_MARTIN.md)
□ Muestra las 3 terminales
□ Explica n8n workflow
□ Prepara Martín para enviar primer mensaje
```

### 1:00-2:00 min: PRIMER MENSAJE

```
□ Martín envía WhatsApp #1
□ Emilio dice: "Mira los logs..."
□ FastAPI recibe POST en Terminal 1
□ Sistema responde en 2-5 seg
□ Martín recibe respuesta en WhatsApp
□ Emilio explica qué pasó

ESPERADO: Status 200 OK, respuesta correcta
```

**Si falla:**
```
□ Check Terminal 1 logs (error?)
□ Check n8n logs (error?)
□ Check SSH tunnel (¿conected?)
→ Si todo falla: Switch a `interactive_demo.py`
```

### 2:00-3:00 min: SEGUNDO MENSAJE

```
□ Martín envía WhatsApp #2 (diferente pregunta)
□ Similar al anterior pero diferente contenido
□ Sistema responde nuevamente en 2-5 seg
□ Emilio valida respuesta
□ Menciona: "Cada búsqueda es única, sin cache"

ESPERADO: Status 200 OK, respuesta diferente pero correcta
```

### 3:00-4:00 min: TERCER MENSAJE (Optional Edge Case)

```
□ Martín envía WhatsApp #3 (más desafiante)
□ Por ej: pregunta ambigua o typo
□ Sistema intenta responder
□ Emilio explica decisiones del sistema

ESPERADO: Status 200 OK, respuesta best-effort
(Si falla: Esto es OK, explica por qué)
```

### 4:00-5:00 min: Explicación Técnica

```
□ Mostrar estructura de directorio (/app)
□ Explicar RAG pipeline
□ Explicar pgvector search
□ Opcional: Mostrar código del endpoint

FOCUS: Impresionar con complejidad subyacente
```

### 5:00-6:00 min: Q&A y Feedback

```
□ Martín hace preguntas
□ Emilio responde (usar talking points)
□ Recolectar feedback específico:
  - Latencia: ¿Aceptable?
  - Precisión: ¿Correctas las respuestas?
  - Casos de uso: ¿Dónde lo usarías?
  - Escalabilidad: ¿Múltiples usuarios?
  - Mejoras: ¿Qué falta?
```

---

## 🚨 EMERGENCY PROTOCOLS

### Si Sistema Cae (FastAPI)

```
Terminal 1 muestra error:
1. Ctrl+C para detener
2. Revisar logs: ¿Error de import?
3. python start.py de nuevo
4. Si persiste: Switch a `interactive_demo.py`
```

### Si Túnel Falla

```
Terminal 2 se desconecta o muestra error:
1. Ctrl+C para detener
2. Volver a conectar: ssh -R 8001:localhost:8001 ...
3. Test desde Terminal 3
4. Si no recupera: Explicar a Martín y continuar con local testing
```

### Si n8n Falla

```
Workflow no responde:
1. Check n8n status: http://164.92.110.179:5678
2. Si offline: Contactar DevOps
3. Contingency: Use `interactive_demo.py` directamente
   → Muestra mismo functionality pero no vía WhatsApp
```

### Si Todo Falla

```
Plan B - Interactive Demo:
1. python interactive_demo.py
2. Explica a Martín: "El pipeline es idéntico, 
   pero sin el paso de WhatsApp/n8n"
3. Continúa con demo usando terminal
4. Martín ve: Funcionalidad, velocidad, precisión
5. Still successful demo!
```

---

## 📈 KPIs para Monitorear

### En Vivo Durante Demo

```
LATENCIA:
□ Primer request: ___ seg
□ Segundo request: ___ seg
□ Tercer request: ___ seg
Objetivo: < 5 seg

ACCURACY:
□ Respuesta #1: Correcta? (Yes/No) → Notas:
□ Respuesta #2: Correcta? (Yes/No) → Notas:
□ Respuesta #3: Correcta? (Yes/No) → Notas:
Objetivo: 3/3 o al menos 2/3

UPTIME:
□ Sistema disponible: Yes/No
□ Cero crashes: Yes/No
□ Logs limpios: Yes/No
```

---

## 💬 Feedback Form (Para Martín)

```
Escala: 1-5 (5=Excelente, 1=Muy malo)

Velocidad de respuesta:     □ □ □ □ □
Precisión de respuestas:    □ □ □ □ □
Facilidad de uso:           □ □ □ □ □
Impacto comercial:          □ □ □ □ □
Disposición a usar:         □ □ □ □ □

Mejoras sugeridas:
_________________________________

Casos de uso adicionales:
_________________________________

Siguiente paso:
_________________________________
```

---

## 📝 Después de Demo (Post-Mortem)

### Dentro de 30 Min

```
□ Guardar logs: cp logs/* backup_demo_[DATE].txt
□ Documentar cualquier issue
□ Notas de feedback de Martín
□ Screenshots si aplica
□ Video/Recording review
```

### Dentro de 2 Horas

```
□ Email a Martín: Gracias + Resumen
□ Documento de issues encontrados
□ Propuesta para mejoras
□ Timeline para next steps
```

---

## ✅ Final Checklist

### Antes de Empezar

```
Terminal 1 (FastAPI):
  □ Corriendo sin errores
  □ Logs visibles
  □ Responde a curl

Terminal 2 (Túnel SSH):
  □ Conectado
  □ No muestra errores
  □ Abierto

Terminal 3 (Testing):
  □ Tests pasando
  □ Webhook funciona
  □ Listo para emergencias

n8n:
  □ Workflow activo
  □ Sin errores recientes
  □ Abierto en browser

Base de Datos:
  □ PostgreSQL running
  □ Datos cargados
  □ pgvector ready

Martín:
  □ Confirmó hora
  □ Tiene celular listo
  □ Conoce número WhatsApp
  □ Está mentalmente prepared
```

---

**Remember:**
- 💪 **Confía en tu código** - Funciona (ya lo probaste)
- 😌 **Stay calm** - Issues son resolubles
- 🎯 **Focus en feedback** - Eso es lo realmente valioso
- 🚀 **You got this!**

---

*Good luck Emilio! 🚀*
