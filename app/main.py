from fastapi import FastAPI
from pydantic import BaseModel
from app.routers import demo_router

app = FastAPI(
    title="SmartOps Core API",
    version="4.0.0",
    description="SmartOps Core - Motor Semantico de Automatizacion Empresarial con demos comerciales",
)

# Incluir routers
app.include_router(demo_router, prefix="")

class ActionPayload(BaseModel):
    intent: str
    parameters: dict

@app.get("/")
def read_root():
    return {
        "system": "SmartOps Core",
        "status": "ONLINE",
        "mode": "Dockerized",
        "version": "4.0.0",
        "endpoints": {
            "demo": "/demo (Quest 1: Demo Comercial)",
            "docs": "/docs (Swagger UI)",
            "redoc": "/redoc (ReDoc)"
        }
    }

@app.post("/semantic-engine/execute")
def execute_action(payload: ActionPayload):
    # Aquí irá tu lógica de BIBLIA.md
    return {
        "status": "processed",
        "decision": f"Enviando accion {payload.intent} a n8n",
        "n8n_dispatched": False  # Todavía no conectado
    }
