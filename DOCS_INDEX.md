# 📚 SmartOps Core - Documentation Index

> **Fecha:** Diciembre 2025  
> **Estado:** 🟢 PRODUCTION READY  
> **Version:** 4.0 (Clean Genesis Commit)

---

## 🚀 START HERE (Para Nuevos)

1. **👉 [QUICK_LAUNCH.md](QUICK_LAUNCH.md)** ⭐ **START HERE**
   - 5 minutos para tener todo corriendo
   - `python local_test_setup.py` + `python run_local_test.py`
   - Perfecto si tienes prisa

2. **[QUICK_START.md](QUICK_START.md)** - Setup Inicial (10 minutos)
   - Guía paso a paso de instalación
   - Configuración de ambiente
   - Validación del sistema

---

## 📋 LEARNING PATH (Recomendado)

### Day 1: Setup & Understanding
- [ ] Read: [QUICK_LAUNCH.md](QUICK_LAUNCH.md) (5 min)
- [ ] Run: `python local_test_setup.py` (5 min)
- [ ] Read: [ARCHITECTURE_LOCAL_TESTING.md](ARCHITECTURE_LOCAL_TESTING.md) (10 min)
- [ ] Run: `python run_local_test.py` (stays running)

### Day 2: First Endpoints
- [ ] Read: [TEAM_HANDOFF.md](TEAM_HANDOFF.md) - MARTES section (5 min)
- [ ] Run: `python interactive_demo.py` (Terminal #2)
- [ ] Test: `curl http://localhost:8001/docs`

### Day 3: Deep Dive
- [ ] Read: [TESTING_GUIDE.md](TESTING_GUIDE.md) (15 min)
- [ ] Explore: Code in `app/routers/demo.py`
- [ ] Try: Different PDF files and images

### Day 4-5: Integration
- [ ] Read: [TEAM_HANDOFF.md](TEAM_HANDOFF.md) - JUEVES section (10 min)
- [ ] Setup: VPS tunnel with `python vps_tunnel_setup.py`
- [ ] Test: With n8n/Waha webhooks

---

## 🎯 Quick Reference by Task

### "I just want to run it locally"
→ [QUICK_LAUNCH.md](QUICK_LAUNCH.md)

### "I'm setting up for the first time"
→ [QUICK_START.md](QUICK_START.md)

### "I need to understand the architecture"
→ [ARCHITECTURE_LOCAL_TESTING.md](ARCHITECTURE_LOCAL_TESTING.md)

### "I want to run all the launchers"
→ [RUN_LOCAL_TEST_README.md](RUN_LOCAL_TEST_README.md)

### "I'm part of the team - show me the schedule"
→ [TEAM_HANDOFF.md](TEAM_HANDOFF.md)

### "How do I test the endpoints?"
→ [TESTING_GUIDE.md](TESTING_GUIDE.md)

### "What's this project about?"
→ [README.md](README.md)

### "I need to understand environment variables"
→ [ENV_REFERENCE.md](ENV_REFERENCE.md)

### "I'm a developer - show me the workflow"
→ [GIT_DEVELOPER_GUIDE.md](GIT_DEVELOPER_GUIDE.md)

### "I need the VPS tunnel setup"
→ Run: `python vps_tunnel_setup.py` (interactive guide)

### "I need to enroll this week"
→ [ENROLL_SETUP.md](ENROLL_SETUP.md)

### "Show me the file structure"
→ [DOCUMENTACION.md](DOCUMENTACION.md)

---

## 📖 ALL DOCUMENTATION FILES

### Getting Started (New Users)
- [QUICK_LAUNCH.md](QUICK_LAUNCH.md) ⭐ **START HERE** - 5 min quickstart
- [QUICK_START.md](QUICK_START.md) - Detailed setup (10 min)
- [README.md](README.md) - Project overview

### Local Development (Developers)
- [RUN_LOCAL_TEST_README.md](RUN_LOCAL_TEST_README.md) - Launcher guide (all options)
- [ARCHITECTURE_LOCAL_TESTING.md](ARCHITECTURE_LOCAL_TESTING.md) - Full architecture diagrams
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing scenarios & endpoints
- [ENV_REFERENCE.md](ENV_REFERENCE.md) - Environment variables explained

### Team & Project Management
- [TEAM_HANDOFF.md](TEAM_HANDOFF.md) - Weekly schedule & responsibilities
- [ENROLL_SETUP.md](ENROLL_SETUP.md) - Team enrollment guide
- [GIT_DEVELOPER_GUIDE.md](GIT_DEVELOPER_GUIDE.md) - Git workflow & config rules

### Reference
- [DOCUMENTACION.md](DOCUMENTACION.md) - Complete navigation hub
- [ENV_REFERENCE.md](ENV_REFERENCE.md) - All .env variables
- [BIBLIA_v1.md](BIBLIA_v1.md) - Historical context & decisions

### Advanced Topics
- [DEMO_COMERCIAL.md](docs/DEMO_COMERCIAL.md) - Commercial demo guide
- [n8n_workflows/README.md](n8n_workflows/README.md) - n8n integration

---

## 🔧 LAUNCH SCRIPTS (Choose ONE)

### Option 1: Python (BEST - All platforms)
```bash
python run_local_test.py
```

### Option 2: PowerShell (Windows recommended)
```powershell
.\run_local_test.ps1
```

### Option 3: Batch (Windows legacy)
```cmd
run_local_test.bat
```

### Setup (First time only)
```bash
python local_test_setup.py
```

### VPS Tunnel (When needed)
```bash
python vps_tunnel_setup.py
```

---

## 🎯 WEEKLY SCHEDULE

**What:** Team learns SmartOps Core  
**When:** Monday - Friday (This week)  
**Where:** [TEAM_HANDOFF.md](TEAM_HANDOFF.md)

- **Monday:** Setup + Validation
- **Tuesday:** Test Endpoints
- **Wednesday:** RAG Pipeline Deep Dive
- **Thursday:** Integration with Waha/n8n
- **Friday:** First Commercial Demo

---

## 🔄 Typical Developer Workflow

```bash
# Day starts:
python run_local_test.py          # Terminal 1 - keeps running

# In Terminal 2:
python interactive_demo.py         # Run tests

# Edit code in app/ 
# (auto-reload will restart FastAPI automatically)

# Test your changes:
curl http://localhost:8001/docs   # See live API docs

# Before committing:
git add ...
git commit -m "feat: ..."
git push

# Troubleshoot if needed:
cat logs/
docker-compose logs postgres       # Check DB logs
```

---

## 🐛 Troubleshooting

**Quick Problems:**
| Issue | Solution |
|-------|----------|
| venv not found | `python local_test_setup.py` |
| Port 8001 in use | Kill other FastAPI or use port 8002 |
| Docker not running | Start Docker Desktop |
| Import error | `cd smartops-core` (verify directory) |
| PostgreSQL slow | Wait 20+ seconds for init |

**Detailed Help:**
→ See [TESTING_GUIDE.md](TESTING_GUIDE.md) Troubleshooting section

---

## 📊 Technology Stack

- **Backend:** FastAPI 0.123.0 + Uvicorn
- **Database:** PostgreSQL 16 + pgvector 1536-dim
- **ORM:** SQLAlchemy 2.0
- **Validation:** Pydantic 2.12
- **AI:** OpenAI SDK (embeddings + GPT-4o Vision)
- **Infrastructure:** Docker Compose, SSH tunnels
- **Python:** 3.10+

---

## 🎯 Success Criteria ✅

After following this guide, you should have:

- [ ] ✅ FastAPI running on http://localhost:8001
- [ ] ✅ PostgreSQL with pgvector initialized
- [ ] ✅ All 7 setup validation checks passing
- [ ] ✅ Swagger UI accessible
- [ ] ✅ One successful end-to-end test
- [ ] ✅ Understanding of the 3 main endpoints:
  - `/demo/upload` (THE LOADER)
  - `/demo/message` (THE SHOW)
  - `/demo/reset` (THE NEURALIZER)

---

## 📞 Support

- **Setup Issues?** → Start with [QUICK_LAUNCH.md](QUICK_LAUNCH.md)
- **Technical Questions?** → Check [TESTING_GUIDE.md](TESTING_GUIDE.md)
- **Team Schedule?** → See [TEAM_HANDOFF.md](TEAM_HANDOFF.md)
- **Git Workflow?** → Review [GIT_DEVELOPER_GUIDE.md](GIT_DEVELOPER_GUIDE.md)
- **Environment Vars?** → Reference [ENV_REFERENCE.md](ENV_REFERENCE.md)

---

## 🚀 Next Steps

1. **Right now:** Read [QUICK_LAUNCH.md](QUICK_LAUNCH.md) (5 min)
2. **Next:** Run `python local_test_setup.py` (5 min)
3. **Then:** Run `python run_local_test.py` (stays open)
4. **While running:** Read [ARCHITECTURE_LOCAL_TESTING.md](ARCHITECTURE_LOCAL_TESTING.md) (10 min)
5. **After:** Run `python interactive_demo.py` in Terminal #2 (5 min)

**Total time to working system:** ~30 minutes

---

**Last Updated:** December 2025  
**Maintained by:** SmartOps Team  
**Status:** ✅ All documentation current
