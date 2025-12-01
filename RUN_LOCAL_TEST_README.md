# 🚀 Local Test Launcher - Guía de Uso

Tres formas para lanzar el servidor FastAPI localmente:

---

## Opción 1️⃣: Python (RECOMENDADO - Multiplataforma)

**Mejor para:** macOS, Linux, Windows (WSL) - Funciona igual en todas partes

```bash
python run_local_test.py
```

### Qué hace:
✅ Verifica venv  
✅ Instala dependencias  
✅ Inicia Docker PostgreSQL  
✅ Prueba conexión BD  
✅ Lanza FastAPI con reload  

### Output esperado:
```
═══════════════════════════════════════════════════════════
  SmartOps Core - Local Test Launcher
═══════════════════════════════════════════════════════════

[✓] Virtual environment found
[✓] All required packages installed
[ℹ] Starting PostgreSQL + pgvector in Docker...
[✓] PostgreSQL started
[✓] Database connection successful

═══════════════════════════════════════════════════════════
✓ READY TO START FASTAPI
═══════════════════════════════════════════════════════════

📍 FastAPI will run on:
   http://localhost:8001

📍 Documentation:
   http://localhost:8001/docs (Interactive)
   http://localhost:8001/redoc (ReDoc)

Press Ctrl+C to stop the server

INFO:     Application startup complete
```

---

## Opción 2️⃣: PowerShell (RECOMENDADO para Windows)

**Mejor para:** Windows 10/11 con PowerShell

```powershell
.\run_local_test.ps1
```

### Características:
✅ Colores bonitos en terminal  
✅ Mejor manejo de errores  
✅ Verificación Docker mejorada  
✅ Outputs formateados  

### Nota:
Si gets error de "cannot be loaded because running scripts is disabled", ejecuta primero:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Opción 3️⃣: Batch (.bat - Legacy)

**Mejor para:** Windows CMD antiguo

```cmd
run_local_test.bat
```

### ⚠️ Nota:
Menos elegante que PowerShell pero funciona en cualquier Windows

---

## 🔄 Primera vez? ANTES de usar qualquier launcher:

```bash
# Ejecutar setup PRIMERO
python local_test_setup.py
```

Esto:
- ✅ Verifica Python 3.10+
- ✅ Crea virtual environment
- ✅ Instala todas las dependencias
- ✅ Inicia PostgreSQL
- ✅ Valida todo (7/7 checks)

---

## 🚀 Quick Test (después de iniciar)

En otra terminal:

```bash
# Test root endpoint
curl http://localhost:8001/

# Test health check
curl http://localhost:8001/semantic-engine/health

# Ver docs interactivas
# Abre en navegador: http://localhost:8001/docs
```

---

## 🐛 Troubleshooting

### Error: "Virtual environment not found"
```bash
python local_test_setup.py
```

### Error: "Package X not installed"
```bash
python local_test_setup.py
```

### Error: "Cannot connect to Docker daemon"
```bash
# Inicia Docker Desktop primero, luego:
python run_local_test.py
```

### Error: "Port 8001 already in use"
```bash
# Otra FastAPI corriendo? Termina eso primero
# O usa otro puerto:
uvicorn app.main:app --reload --port 8002
```

### Error: "Database connection failed"
```bash
# Espera 20 segundos más para que PostgreSQL inicie
# O inicia manualmente:
docker-compose up -d postgres
```

---

## 📋 VPS Tunnel Setup

¿Necesitas conectar con VPS remoto? Ejecuta:

```bash
python vps_tunnel_setup.py
```

Esto te guiará paso a paso para:
- ✅ Configurar SSH reverse tunnel
- ✅ Conectar a producción desde local
- ✅ Testing con endpoint real

---

## 📚 Documentación Relacionada

- **TEAM_HANDOFF.md** - Plan de enroll semanal completo
- **QUICK_START.md** - Setup inicial (5 minutos)
- **TESTING_GUIDE.md** - Escenarios avanzados de testing
- **ENV_REFERENCE.md** - Variables de ambiente explicadas

---

## ✨ Pro Tips

1. **Usar reload automático:**
   - Python detects cambios en `app/` y reinicia automáticamente
   - Solo modifica archivos en `app/` para verlo funcionar

2. **Ver logs en vivo:**
   - FastAPI muestra todos los requests en terminal
   - Perfecto para debugging

3. **Database reset:**
   - Detén FastAPI (Ctrl+C)
   - Ejecuta: `docker-compose down` (borra BD)
   - Reinicia con: `python run_local_test.py`

4. **Keep it running:**
   - Abre 2 terminales:
     - Terminal 1: `python run_local_test.py` (servidor)
     - Terminal 2: `python interactive_demo.py` (testing)

---

**¿Problemas?** Revisa TEAM_HANDOFF.md o contacta al admin.
