# 🧪 Unit Tests - SmartOps Demo Framework

Pruebas unitarias completas para validar que el framework funciona correctamente en nuevas instalaciones.

## 📋 Contenido de Tests

### 1. **test_schemas.py** - Validación de Pydantic DTOs
Verifica que todos los esquemas de entrada/salida funcionan:
- ✅ `DemoUploadMetadata` - Metadatos de carga
- ✅ `NeuralizerRequest` - Requests para cerrar sesión
- ✅ `MessageRequest/Response` - Esquemas de mensajes
- ✅ `DemoSessionResponse` - Responses de sesión
- ✅ Validaciones de campos (min/max length, required, etc)

**Casos de prueba:**
```
✓ Valid metadata acceptance
✓ Missing field rejection
✓ Empty string rejection
✓ Max length validation
```

### 2. **test_database.py** - SQLAlchemy ORM Models
Verifica operaciones CRUD en modelos:
- ✅ `DemoSession` - Ciclo de vida de sesiones
- ✅ `DemoLead` - Captura de prospectos
- ✅ `DemoVector` - Almacenamiento de embeddings
- ✅ Relaciones FK entre tablas

**Casos de prueba:**
```
✓ Create session in database
✓ Session defaults (active, created_at)
✓ Close session (update)
✓ Lead creation with foreign key
✓ Multiple vectors per session
✓ Full CRUD operations
```

### 3. **test_rag_service.py** - Demo RAG Service Logic
Verifica servicios de embeddings y búsqueda vectorial:
- ✅ Inicialización con API key
- ✅ Chunking de texto (división inteligente)
- ✅ Generación de embeddings (OpenAI)
- ✅ Extracción de PDF (pypdf)
- ✅ Extracción de imágenes (GPT-4o Vision)
- ✅ Indexación de documentos
- ✅ Búsqueda vectorial (pgvector)
- ✅ Limpieza de sesiones

**Casos de prueba:**
```
✓ RAG service initialization
✓ Text chunking respects max size
✓ Embedding generation via OpenAI API
✓ PDF extraction and error handling
✓ Image extraction with GPT-4o Vision
✓ Document indexing creates vectors
✓ Vector search returns relevant chunks
✓ Session cleanup deletes vectors
```

### 4. **test_endpoints.py** - FastAPI Endpoints
Verifica los 3 endpoints principales:
- ✅ **THE LOADER** - `POST /demo/upload` - Carga de documentos
- ✅ **THE SHOW** - `POST /demo/message` - Interacción con bot
- ✅ **THE NEURALIZER** - `POST /demo/reset` - Cierre de sesión
- ✅ Health check - `GET /demo/health`

**Casos de prueba:**
```
LOADER:
✓ Accept PDF files
✓ Accept image files (JPG/PNG)
✓ Reject invalid file types
✓ Validate required fields
✓ Create session in database

THE SHOW:
✓ Send message to valid session
✓ Reject invalid session
✓ Reject closed session
✓ Validate message length (1-2000 chars)
✓ Return proper response structure

THE NEURALIZER:
✓ Close valid session
✓ Validate secret word
✓ Reject invalid sessions
✓ Save lead if requested
✓ Return proper response structure

INTEGRATION:
✓ Complete workflow: upload → message → reset
```

## 🚀 Ejecutar Tests

### Instalar dependencias de testing
```bash
pip install pytest pytest-cov fastapi httpx sqlalchemy
```

### Correr todos los tests
```bash
pytest tests/ -v
```

### Correr tests específicos
```bash
# Solo schemas
pytest tests/test_schemas.py -v

# Solo database
pytest tests/test_database.py -v

# Solo RAG service
pytest tests/test_rag_service.py -v

# Solo endpoints
pytest tests/test_endpoints.py -v
```

### Ver cobertura de código
```bash
pytest tests/ --cov=app --cov-report=html
```

### Ejecutar un test específico
```bash
pytest tests/test_endpoints.py::TestTheLoaderEndpoint::test_upload_valid_pdf -v
```

## 📊 Cobertura Esperada

```
app/modules/demo/schemas.py    ✅ 100%
app/modules/demo/models.py     ✅ 100%
app/routers/demo.py           ✅ 95%+
app/services/demo_rag.py      ✅ 90%+
app/database.py               ✅ 85%+
```

## 🔍 Qué Validan los Tests

### 1. **Entrada de Datos**
- ✅ Tipos de archivo (PDF, JPG, PNG)
- ✅ Campos requeridos y validación
- ✅ Límites de tamaño (nombres, mensajes)
- ✅ Formatos UUID y timestamps

### 2. **Lógica de Negocio**
- ✅ Ciclo de vida de sesiones (activa → cerrada)
- ✅ Captura de leads
- ✅ Índices vectoriales
- ✅ Búsqueda de contexto

### 3. **Integración de Componentes**
- ✅ FastAPI ↔ Database
- ✅ FastAPI ↔ RAG Service
- ✅ RAG Service ↔ OpenAI API (mockeada)
- ✅ RAG Service ↔ pgvector (simulada)

### 4. **Manejo de Errores**
- ✅ Validación de input
- ✅ Manejo de excepciones
- ✅ Códigos HTTP correctos (200, 400, 403, 404, 422)
- ✅ Mensajes de error descriptivos

## 📈 Workflow para Nuevos Desarrolladores

```bash
# 1. Clonar repo
git clone <repo>
cd smartops-core

# 2. Crear venv
python -m venv .venv
source .venv/bin/activate  # o .\.venv\Scripts\Activate.ps1 en Windows

# 3. Instalar dependencias
pip install -r requirements.txt
pip install pytest pytest-cov fastapi httpx

# 4. Configurar .env
cp .env.example .env
# Editar .env con valores reales

# 5. Ejecutar tests
pytest tests/ -v

# 6. Ver que TODO está ✅ GREEN
# Si todos los tests pasan, el framework está listo para usar
```

## 🎯 Beneficios

1. **Validación Rápida** - Nuevos devs pueden verificar setup en segundos
2. **Documentación Viva** - Tests son ejemplos de cómo usar cada componente
3. **Confianza** - Si tests pasan, sistema está operacional
4. **Debugging** - Tests ayudan a aislar problemas
5. **Refactoring Seguro** - Cambios se validan automáticamente

## 🔧 Mocking & Fixtures

### Dependencias Mockeadas
- ✅ OpenAI API (para no gastar tokens en tests)
- ✅ PyPDF Reader (para no requerir PDFs reales)
- ✅ GPT-4o Vision (para no procesar imágenes reales)
- ✅ PostgreSQL/pgvector (SQLite en memoria para speed)

### Fixtures Disponibles
```python
@pytest.fixture
def test_db()          # BD de prueba (SQLite en memoria)

@pytest.fixture
def client(test_db)    # Cliente de prueba FastAPI

@pytest.fixture
def mock_rag_service() # DemoRAGService con APIs mockeadas
```

## 📝 Ejemplo: Usar Tests para Entender el Código

```bash
# 1. Ver cómo funciona el endpoint upload
pytest tests/test_endpoints.py::TestTheLoaderEndpoint::test_upload_valid_pdf -vv

# 2. Ver cómo funciona RAG indexing
pytest tests/test_rag_service.py::TestIndexing -vv

# 3. Ver flujo completo
pytest tests/test_endpoints.py::TestEndpointIntegration::test_full_demo_workflow -vv
```

## ✨ Próximas Mejoras

- [ ] Tests de performance (carga, vectores grandes)
- [ ] Tests de seguridad (SQL injection, auth)
- [ ] Tests de concurrencia (múltiples sesiones paralelas)
- [ ] Integration tests con BD real (PostgreSQL + pgvector)
- [ ] E2E tests con navegador (Selenium/Playwright)

---

**Estado:** ✅ Listos para usar  
**Última actualización:** Diciembre 2024  
**Maintainer:** SmartOps Development Team
