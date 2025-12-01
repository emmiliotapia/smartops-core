# SmartOps Admin Panel | Streamlit

## Descripcion
Panel de administracion y debugging para SmartOps Core. No es cliente final, es herramienta para:
- Monitorear estado del sistema
- Ejecutar acciones manuales
- Ver logs y ejecuciones
- Gestionar documentos (RAG)
- Testear endpoints

## Estructura

```
frontend/
├── app.py              # Punto de entrada Streamlit
├── requirements.txt    # Dependencias
└── components/
    ├── dashboard.py    # Pagina principal: KPIs
    ├── executions.py   # Ver historial de ejecuciones
    ├── rag_manager.py  # Upload/delete documentos
    ├── system_health.py # Health check del API
    └── webhooks.py     # Testear webhooks n8n
```

## Variables de Entorno

```
API_URL=http://api_core:8000          # URL del backend
STREAMLIT_SERVER_PORT=8501            # Puerto del panel
STREAMLIT_SERVER_ADDRESS=0.0.0.0      # Escuchar todas las IPs
STREAMLIT_LOGGER_LEVEL=info
```

## Paginas Principales

### 1. Dashboard (dashboard.py)
KPIs en tiempo real:
- Estado del API (Online/Offline)
- Ejecuciones ultimas 24h
- Errores/exitos ratio
- Documentos en RAG
- Usuarios activos

### 2. Executions (executions.py)
Tabla de historial:
- Intencion ejecutada
- Tenant
- Estado (pending/success/failed)
- Timestamp
- Logs detallados

Filtros:
- Por rango de fechas
- Por tenant_id
- Por estado
- Por intent

### 3. RAG Manager (rag_manager.py)
Gestion de documentos:
- Upload PDF/TXT/JSON
- Visualizar embeddings
- Buscar documentos por similaridad
- Eliminar documentos
- Ver metadata

### 4. System Health (system_health.py)
Status checks:
- Ping al API
- Conexion a BD
- Tamano de BD
- Cantidad de vectores
- Queue de ejecuciones pendientes

### 5. Webhooks (webhooks.py)
Testeo manual:
- Simular payload de n8n
- Ver respuesta del semantic-engine
- Ejecutar intenciones custom

## Desarrollo Local

**Instalar dependencias:**
```bash
cd frontend
pip install -r requirements.txt
```

**Correr Streamlit:**
```bash
streamlit run app.py --logger.level=debug
```

**Acceder:**
- http://localhost:8501

## Estructura de Componentes (Ejemplo)

**frontend/components/dashboard.py:**
```python
import streamlit as st
import requests
import pandas as pd

def show_dashboard(api_url: str):
    st.set_page_config(page_title="SmartOps Dashboard", layout="wide")
    
    st.title("SmartOps Core | Dashboard")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("API Status", "Online", "+1 uptime")
    with col2:
        st.metric("Executions 24h", "145", "+12%")
    with col3:
        st.metric("Success Rate", "94.2%", "-0.3%")
    with col4:
        st.metric("Docs en RAG", "1,250", "+50")
```

## Seguridad

- [ ] No exponer API_KEY en UI (solo backend)
- [ ] Autenticacion simple con contraseña (Streamlit secrets)
- [ ] CORS solo desde localhost en desarrollo
- [ ] Rate-limiting: max 100 requests/min por sesion
- [ ] Logs de acceso al panel

## Error Handling

**Ejemplo de conexion segura:**
```python
import streamlit as st

def api_request(endpoint: str, method: str = "GET", data=None):
    try:
        url = f"{st.secrets['API_URL']}{endpoint}"
        if method == "GET":
            resp = requests.get(url, timeout=5)
        else:
            resp = requests.post(url, json=data, timeout=5)
        
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error(f"Error {resp.status_code}: {resp.text}")
    except requests.exceptions.Timeout:
        st.error("Advertencia: API timeout. Intenta de nuevo.")
    except Exception as e:
        st.error(f"Error: {str(e)}")
```

## Diseno Multi-Device

- Usar st.columns() para responsive layouts
- Mobile-first: Streamlit adapta automaticamente
- Sidebars para navegacion en desktop

## Roadmap UI

- [ ] Dark mode toggle
- [ ] Tabla de usuarios/tenants con CRUD
- [ ] Graficos avanzados (Plotly)
- [ ] Exportar reportes (CSV/PDF)
- [ ] Integracion de notificaciones en tiempo real (WebSocket)
