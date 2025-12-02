# 🎬 SmartOps Core Demo Script - Martín (Dec 1, 2025)

**Con:** Martín (Evaluador/Usuario)  
**Objetivo:** Demostrar capacidades de RAG + WhatsApp Integration  
**Duración:** 15-20 minutos  
**Formato:** Live Demo (en vivo)

---

## ⏰ Timeline

| Tiempo | Actividad | Owner |
|--------|-----------|-------|
| 0:00 | Bienvenida & Contexto | Emilio |
| 1:00 | Demo Setup Explicado | Emilio |
| 2:00 | **DEMO INICIA** | - |
| 2:00 | Primer mensaje WhatsApp | Martín |
| 2:05 | Respuesta en vivo | Sistema |
| 2:10 | Segundo mensaje (validación) | Martín |
| 2:15 | Respuesta #2 | Sistema |
| 3:00 | Tercera prueba (edge case) | Martín |
| 3:05 | Respuesta #3 + Explicación | Emilio |
| 5:00 | Q&A & Feedback | Ambos |
| 6:00 | **FIN DEMO** | - |

---

## 📝 Guión (Emilio)

### Minuto 0:00 - Bienvenida

```
"Martín, muchas gracias por tu tiempo. Hoy vamos a ver 
SmartOps Core v4.0 - un sistema cognitivo diseñado para 
demostraciones comerciales usando WhatsApp.

Lo especial: Tú envías un mensaje de WhatsApp, nuestro 
sistema busca en el menú usando IA, y te devuelve la 
respuesta en menos de 5 segundos.

Empecemos."
```

### Minuto 1:00 - Setup Explicación

```
"Detrás de escenas, esto es lo que está pasando:

1. Tú envías WhatsApp a este número [show number]
2. Nuestro servicio Waha recibe el mensaje
3. Lo envía a n8n (orquestador de workflows)
4. n8n hace una petición a mi computadora via SSH tunnel
5. Mi API busca en la base de datos (pgvector)
6. Genera una respuesta usando IA
7. La respuesta vuelve por el mismo camino
8. Aparece en tu WhatsApp

Todo esto en 2-5 segundos.

Ahora vamos a probarlo. Martín, ¿qué pregunta quieres hacer?"
```

### Minuto 2:00 - DEMO INICIA

```
"Perfecto. Cuando estés listo, envía tu primer mensaje 
por WhatsApp al número [show]. Yo voy a estar monitoreando 
los logs en tiempo real para que veas qué pasa."

[Mostrar Terminal 1 con FastAPI logs]

"En esta terminal ves cada request que llega a la API.
Cuando envíes el mensaje, deberías ver aparecer acá..."
```

### Minuto 2:05 - Primera Respuesta

```
"¡Mira! Acaba de llegar el request:
  POST /demo/message - Status 200

Y aquí está la respuesta que te llegó en WhatsApp:
'[respuesta del sistema]'

Exacto - buscó en la base de datos, encontró info de 
costillas, y generó esa respuesta automáticamente.

¿Qué te parece?"
```

### Minuto 2:10 - Segunda Prueba

```
"Vamos a hacerlo más difícil. Envía otra pregunta 
diferente - algo que requiera que el sistema 
busque en múltiples partes del menú."

[Esperar mensaje]
```

### Minuto 2:15 - Segunda Respuesta

```
"De nuevo en 3 segundos aproximadamente.
Ves el log acá - POST /demo/message, status 200.

Y tú ya recibiste la respuesta en WhatsApp.

Esto es lo que llamamos 'RAG' - Retrieval Augmented 
Generation. Significa que el sistema:
1. Recupera información relevante del menú
2. La usa para generar una respuesta contextual
3. Todo en vivo

¿Querés probar algo más?"
```

### Minuto 3:00 - Tercera Prueba (Edge Case)

```
"Vamos a probar algo más desafiante - algo que 
normalmente podría ser ambiguo o donde el sistema 
podría cometer un error."

[Esperar mensaje tricky]
```

### Minuto 3:05 - Tercera Respuesta + Explicación

```
"Interesante respuesta. El sistema hizo una búsqueda 
semántica (no solo matching de palabras, sino de significado) 
y encontró la mejor coincidencia en el menú.

Aquí es donde el pgvector entra en juego - es una 
extensión de PostgreSQL que permite búsquedas por 
similaridad en vectores (embeddings de IA)."

[Opcional: Mostrar diagrama de RAG pipeline]
```

### Minuto 5:00 - Q&A & Feedback

```
"Ahora - ¿preguntas? ¿Qué te pareció? ¿Hay algo 
específico que quieras ver o probar?"

Puntos para discutir:
- Latencia (¿aceptable?)
- Calidad de respuestas (¿preciso?)
- Casos de uso adicionales
- Escalabilidad (¿múltiples usuarios simultáneamente?)
```

### Minuto 6:00 - Cierre

```
"Gracias Martín. Tu feedback es crucial para mejorar esto.
Próximos pasos:
[Explicar roadmap - Fase 4, mejoras de UX, etc.]
"
```

---

## 🎯 Puntos Clave para Emiliar

### Si falla algo:

**Respuesta Lenta (>5 seg):**
```
"El backend a veces tarda por latencia de red o porque 
la búsqueda encontró demasiadas coincidencias. Déjame 
ver el log... [revisar] Ah, está procesando. Ya debería 
llegar."
```

**Respuesta Incorrecta:**
```
"Esto es interesante - el sistema hizo su mejor búsqueda 
pero la información en el menú era ambigua. En fases futuras 
vamos a mejorar cómo interpreta consultas complejas."
```

**N8n Workflow Falla:**
```
"Tengo un backup - déjame usar interactive_demo.py 
directamente para mostrarte la funcionalidad core."
[Switch a modo manual si es necesario]
```

---

## 📊 Métricas a Monitorear (En Vivo)

Mientras ves los logs, menciona:

```
Latencia: ~2-3 segundos
Tokens usados: [mostrar en logs]
Vectores buscados: [quantity]
Respuesta confidence: [si aplica]
```

---

## 🎁 Preparar Antes

### Física
- [ ] PC con FastAPI corriendo
- [ ] Terminal con SSH Tunnel activo
- [ ] Terminal 3 lista para tests manuales
- [ ] Celular/WhatsApp del número de prueba

### Digital
- [ ] n8n workflow activo en VPS
- [ ] Base de datos con menú cargado
- [ ] Waha conectado y escuchando
- [ ] Logs configurados para ser legibles

### Documentación
- [ ] Este guión impreso o en pantalla
- [ ] INTEGRATION_PHASE3.md abierto (por si preguntas)
- [ ] Backup: interactive_demo.py listo

---

## 🎤 Talking Points

Si Martín pregunta:

**"¿Qué pasa si hay múltiples respuestas?"**
```
"El sistema usa pgvector para buscar las 3 mejores 
coincidencias y luego elige la más relevante. Es como 
un motor de búsqueda pero para menús."
```

**"¿Qué pasa con errores de tipeo?"**
```
"Como usamos embeddings semánticos (no solo word matching), 
pequeños typos no importan. El sistema entiende la intención."
```

**"¿Se puede escalar a 1000 usuarios?"**
```
"Sí, por eso usamos PostgreSQL con pgvector. Es escalable 
horizontalmente. Actualmente optimizado para 100-500 
usuarios concurrentes sin problemas."
```

**"¿Puedo entrenar el modelo con mi propio menú?"**
```
"Exactamente. Sube un PDF o fotos del menú y el sistema 
procesa todo automáticamente con IA (OCR + embeddings)."
```

---

## ⏱️ Contingency Timing

Si todo va rápido (~3 min en lugar de 6):

```
Opción 1: Hacer más pruebas de edge cases
Opción 2: Mostrar código/architecture detrás
Opción 3: Discutir roadmap más profundamente
Opción 4: Q&A más extenso
```

Si todo va lento:

```
Enfócate en: 
- Primer mensaje (impactante)
- Segunda prueba (validación)
- Skip edge case si es necesario
- Ir directo a Q&A si surge un issue
```

---

## ✅ Pre-Demo Checklist

### 30 min Antes:
- [ ] FastAPI corriendo: `python start.py`
- [ ] Túnel activo: `ssh -R 8001:localhost:8001 smartops@164.92.110.179`
- [ ] n8n workflow activo
- [ ] Test manual: `curl http://localhost:8001/`
- [ ] Terminal logs visible y limpio
- [ ] PostgreSQL running: `docker ps`

### 5 min Antes:
- [ ] Número WhatsApp listo
- [ ] Martín confirma que puede enviar WhatsApp
- [ ] Guión abierto en otra pantalla
- [ ] Backup (interactive_demo.py) listo
- [ ] Respirar 😌

---

## 📹 Recording (Si es requerido)

```
Start recording: Pantalla + Audio
- Terminal con logs
- WhatsApp messages
- Emilio explicando

Useful for:
- Feedback review
- Team learning
- Future iterations
```

---

## 🎉 Goal

**No es mostrar perfección, es demostrar:**
1. ✓ Funcionalidad real (no mockups)
2. ✓ Velocidad aceptable
3. ✓ Capacidad de escalado
4. ✓ UX intuitivo
5. ✓ Potencial comercial

**Éxito =** Martín envía 3 mensajes → Sistema responde correctamente 3 veces

---

**Buena suerte Emilio! 🚀**
