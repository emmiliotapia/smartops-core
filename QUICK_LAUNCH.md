# ⚡ QUICK START GUIDE - 5 Minutos para Tener Todo Corriendo

## 🎯 Objetivo
Tener FastAPI + PostgreSQL corriendo en local y listo para testing

---

## PASO 1: Primera Vez (5 minutos)

```bash
# Abre terminal en la raíz del proyecto
# Ejecuta esto UNA SOLA VEZ:

python local_test_setup.py
```

**Espera a que termine - verás algo como:**
```
✓ All 7 checks passed! Setup is ready.
```

---

## PASO 2: Cada Vez Que Quieras Desarrollar (1 línea)

```bash
python run_local_test.py
```

**O en Windows PowerShell:**
```powershell
.\run_local_test.ps1
```

**Espera a que veas:**
```
📍 FastAPI will run on: http://localhost:8001
Press Ctrl+C to stop the server
```

---

## PASO 3: En Otra Terminal - Testing (Opcional)

```bash
# En terminal #2, mantén este corriendo en fondo:
python interactive_demo.py
```

---

## ✅ Success!

```
✓ API en: http://localhost:8001
✓ Docs en: http://localhost:8001/docs
✓ Database: PostgreSQL con pgvector
✓ Auto-reload activado (cambias código → reinicia automático)
```

---

## 🧪 Quick Test

Abre nueva terminal:

```bash
# Test 1: Root endpoint
curl http://localhost:8001/

# Test 2: Health check
curl http://localhost:8001/semantic-engine/health

# Test 3: Open en navegador
http://localhost:8001/docs
```

---

## 🔄 Si Algo Falla

| Error | Solución |
|-------|----------|
| Port in use | `lsof -i :8001` (Mac/Linux) o mata el proceso |
| venv not found | `python local_test_setup.py` |
| Docker error | Abre Docker Desktop primero |
| Import error | Verifica estés en carpeta raíz (`cd smartops-core`) |
| DB connection | Espera 20s más (PostgreSQL init lento) |

---

## 📚 Docs Completos

- **TEAM_HANDOFF.md** - Plan semanal completo
- **RUN_LOCAL_TEST_README.md** - Explicación detallada de launchers
- **ARCHITECTURE_LOCAL_TESTING.md** - Diagramas y flujos
- **TESTING_GUIDE.md** - Escenarios avanzados

---

## 🚀 Próximo Nivel: VPS Tunnel

Cuando necesites conectar con el VPS de producción:

```bash
python vps_tunnel_setup.py
```

---

**¿Preguntas?** Busca en TEAM_HANDOFF.md o contacta admin.
