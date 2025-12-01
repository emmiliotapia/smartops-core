# 📖 BIBLIA SMARTOPS CORE
**Versión:** 1.0  
**Fecha:** 01-Dic-2025  
**Owner:** Emmilio Tapia (Root Admin)  
**Proyecto:** SmartOps Core / SmartOps Vault  

---

## 0. Propósito de este documento

Esta “Biblia” define **cómo se piensa y se diseña** dentro de SmartOps Core.

Sirve para que cualquier persona cercana (Martín, amigos, futuros devs) pueda:

- Entender el **marco completo** (técnico + conceptual).
- Replicar el sistema para **nuevos clientes/tenants**.
- Diseñar nuevas soluciones **sin romper** seguridad, multi-tenancy ni la filosofía del motor semántico.

> Si algo cambia en: intents, RAG, contratos JSON, seguridad base o modelo de datos → **SE ACTUALIZA ESTE ARCHIVO**.

---

## 1. Visión general del sistema

SmartOps Core es un **sistema cognitivo híbrido** para PYMES:

- Backend núcleo: **SmartOps Vault** (FastAPI + PostgreSQL + pgvector).
- Capa cognitiva: **SmartOps Semantic Engine** (Modelo B).
- Orquestador de acciones: **n8n**.
- Pasarela de WhatsApp: **Waha**.
- Panel humano: **Streamlit** (admin / dashboards).

### 1.1 Metáfora oficial

Para pensar el sistema de forma consistente usamos esta analogía:  

- **Framework / Motor semántico = Grimorio**  
  Libro de reglas, hechizos (acciones) y rituales (prompts).
- **Acciones canon = Hechizos**  
  Operaciones permitidas, bien definidas (`crear_pedido`, `capture_lead`, etc.).
- **n8n = Neurona determinista**  
  Cada nodo es una función pura; el flujo completo ejecuta el JSON del agente.
- **FastAPI = Sistema nervioso**  
  Conecta frontends, WhatsApp, n8n, DB y RAG.
- **RAG + pgvector = Memoria episódica**  
  Chunks de texto etiquetados por tenant, tipo, categoría.
- **Prompt = Ritual de invocación**  
  Identidad, límites y contratos JSON del agente.
- **Versionado = Árbol de skills**  
  Cada módulo estable se convierte en skill reusable.

---

## 2. Arquitectura técnica (foto objetiva)

### 2.1 Infraestructura

- **Arquitectura:** Híbrida (Cerebro Local + Cuerpo VPS).
- **Local Brain (WSL/Ubuntu):**
  - `FastAPI` (puerto interno 8000 → mapeado 8001): Semantics & RAG.
  - `PostgreSQL + pgvector` (5432 → 5433): memoria vectorial multi-tenant.
  - `Streamlit` (8501): panel administrativo.
  - Todo corre en **Docker**.
- **VPS Body (DigitalOcean Ubuntu 24.04):**:contentReference[oaicite:1]{index=1}  
  - Nginx Proxy Manager (80/443).
  - `n8n` (5678) – **solo interno Docker**.
  - `Waha` (3000) – **solo interno Docker**.
  - Túnel SSH reverso a Cerebro Local (para acceder al FastAPI local desde el VPS).

### 2.2 Regla crítica de red

> **API y DB NUNCA se exponen por puerto público.**  
> Solo se accede:
> - Por red interna Docker.
> - O por túnel SSH autenticado.  

---

## 3. Políticas de diseño (SMARTOPS-CORE)

Estas políticas aplican a **todo módulo nuevo**:

```yaml
smartops_core_policy:
  tenancy: "Todo filtra por tenant_id."

  auth:
    roles: ["owner","admin","editor","viewer"]
    rule: "Permiso mínimo por endpoint; nunca confiar solo en la UI."

  documents:
    upload_limits: "size/type controlados por .env"
    rag:
      chunk_size: "800-1200 chars recomendado"
      index: "pgvector"
      filter: "tenant_id primero, luego similitud."
      metadata_required: ["tenant_id","document_id","category","doc_type","tags"]

  modules:
    api_prefix: "/modules/<modulo>"
    data_contract:
      common_fields:
        ["id","tenant_id","created_at","created_by","updated_at","updated_by","metadata_"]
    versioning: "/api/v1"

  observability:
    audit: ["user_create","role_change","doc_upload","doc_delete"]
    logs: "Errores con 'detail' consistente y trazable."
Puntos clave:

Multi-tenancy estricto: ningún query se hace sin tenant_id en filtro.

RAG SIEMPRE lleva category en metadata para cortar alucinaciones.

Nada se implementa solo en la UI: siempre se valida en backend.

4. Seguridad (Fortress Mode)
Resumen operativo del protocolo de seguridad SmartOps:

Perímetro:

Cloudflare como proxy (modo Full Strict).

UFW: deny incoming / allow outgoing.

Puertos abiertos:

22222 SSH (solo para gestión, con llave).

80/443 para Nginx Proxy Manager.

Puertos de RustDesk si aplica.

Puertos cerrados al público:

5432/5433 (Postgres).

5678 (n8n).

3000 (Waha).

8000/8001 (FastAPI).

Acceso:

Root deshabilitado.

Login solo por llave SSH.

Basic Auth en herramientas internas (n8n, waha, tools).

Datos:

.env y llaves privadas NUNCA van a Git.

Backups periódicos: snapshot VPS + dump Postgres + export flujos n8n.

Si alguien toca firewall, puertos o política de llaves → actualizar también Protocolo de seguridad.md.

5. Backend núcleo: SmartOps Vault
Definición: monolito FastAPI modularizable que maneja autenticación, tenants, documentos y chat RAG.

5.1 Componentes principales
app/main.py

Crea la app FastAPI.

Configura CORS, carga .env.

Monta endpoints:

/ health.

/tenants, /users, /groups.

/upload, /documents.

/chat (RAG).

app/database.py

create_engine(DATABASE_URL) → PostgreSQL/pgvector.

SessionLocal y Base.

app/auth.py

JWT HS256, SECRET_KEY por env.

create_access_token, get_current_user, hashing Bcrypt.

app/models.py

Tablas: tenants, users, folders, documents, document_vectors, executions, etc.

app/schemas.py

Modelos Pydantic para requests/responses.

app/rag.py (o similar)

Funciones de ingesta y consulta RAG.

app/semantic_engine.py

Implementa pipeline de Semantic Engine.

6. Modelo de datos clave
6.1 Tenancy
tenants

id (UUID, PK)

name

config (JSONB)

created_at

users

id (UUID, PK)

email, hashed_password, full_name

role (owner/admin/editor/viewer)

tenant_id (FK → tenants)

6.2 Documentos + RAG
documents

id (UUID)

tenant_id

folder_id (opcional)

name, doc_type (policy, menu, faq, etc.)

category (OBLIGATORIO)

metadata (JSONB)

document_vectors

id

document_id

tenant_id

category (misma que el documento padre)

chunk_text

embedding (vector)

Regla: ningún vector se guarda sin tenant_id + category.

7. Gestión de conocimiento (RAG)
7.1 Principios base
No todo va a RAG.

Catálogo, stock, precios, estados → SQL directo.

RAG solo para lenguaje difuso: políticas, textos largos, PDFs, preguntas raras.

Niveles de potencia:

Nivel 0 → Sin IA (SQL + plantillas).

Nivel 1 → IA sin RAG (clasificador de intención).

Nivel 2 → IA + RAG (texto largo, contexto complejo).

7.2 Pipeline de ingesta
Tomar documento (PDF, texto, etc.).

Limpiar ruido (headers, pies, basura).

Cortar en chunks de 800–1200 caracteres (≈ 300–800 tokens) por sentido.

Generar embedding por chunk.

Guardar en document_vectors con metadata:

json
Copy code
{
  "tenant_id": "uuid",
  "document_id": "uuid",
  "category": "politicas_envio",    // OBLIGATORIO
  "doc_type": "policy",
  "tags": ["envios", "tiempos"],
  "chunk_text": "Texto del fragmento..."
}
7.3 Consulta RAG eficiente
Cuando llega un mensaje:

Clasificar intención (modelo barato / reglas).

Preguntar: ¿requiere texto largo?

NO → resolver con SQL/plantillas.

SÍ → hacer RAG filtrando por:

tenant_id = X

category IN (...)

LIMIT 3–5 chunks

Enviar al modelo solo:

Mensaje usuario.

3–5 chunks relevantes.

Prompt estructurado (grimorio).

Esquema de Action Contract.

8. SmartOps Semantic Engine (Modelo B)
Definición: evolución de bots de FAQ a agentes que devuelven JSON de acciones.

8.1 Pipeline
text
Copy code
input (WhatsApp/Web)
  -> classifier (intención: venta/soporte/info)
  -> semantic_engine (prompt + RAG selectivo)
  -> LLM responde con JSON (Action Contract)
  -> n8n ejecuta acciones contra APIs/DB
8.2 Action Contracts (contratos JSON)
Regla central:

Si el JSON no valida contra el esquema → NO se ejecuta nada.

Ejemplo simplificado:

json
Copy code
{
  "intent": "crear_pedido",
  "tenant_id": "uuid-del-negocio",
  "channel": "whatsapp",
  "actions": [
    {
      "type": "create_order",
      "payload": {
        "customer_phone": "+52...",
        "items": [
          {"sku": "PIZZA_FAM", "qty": 1},
          {"sku": "COCA_600", "qty": 2}
        ],
        "notes": "Sin cebolla"
      }
    }
  ],
  "trace": {
    "confidence": 0.92,
    "source": "semantic_engine_v1",
    "rag_used": true,
    "categories": ["menu","promociones"]
  }
}
intent debe pertenecer a un catálogo de intents permitidos.

type de cada acción debe existir como flujo en n8n.

tenant_id se pasa siempre (multi-tenancy).

8.3 Diseño de un nuevo “hechizo”
Para crear una nueva acción canon:

Definir el nombre (capture_lead, enviar_cotizacion, etc.).

Definir el schema JSON del payload.

Crear el flujo en n8n que recibe exactamente ese JSON.

Actualizar el grimorio/prompt del Semantic Engine para que use esa acción.

Agregar ejemplos de few-shot con ese intent.

9. Módulos externos
9.1 n8n (Neurona determinista)
Cada acción canon tiene:

Un webhook de entrada.

Validación Pydantic/JSON antes de tocar DB/APIs.

Logs mínimos (éxito/error).

9.2 Waha (WhatsApp HTTP API)
Maneja sesiones de WhatsApp.

Entrega los mensajes entrantes a:

n8n, o

FastAPI (webhook directo), según diseño.

9.3 Streamlit (Panel Admin)
Frontend simple para:

Gestionar tenants, usuarios, documentos.

Ver ejecuciones del Semantic Engine.

Monitorear errores de RAG / JSON.

10. Cómo crear un nuevo cliente (Checklist operativo)
Esta es la guía rápida para replicar SmartOps con un negocio nuevo.

Alta de tenant

Crear tenant con nombre del negocio.

Crear usuario owner con correo del cliente.

Config base

Definir config del tenant (horarios, canales, branding básico).

Crear carpeta raíz de documentos.

Ingesta inicial

Subir:

Menú / catálogo (a DB, no RAG).

Políticas de envío, cambios, etc. (a RAG).

Chunks con category clara (politicas_envio, faq_generales, etc.).

Definir acciones canon para ese negocio

Mínimo:

capture_lead

crear_pedido

consultar_estado_pedido

Crear contratos JSON y flujos n8n correspondientes.

Configurar canal

Vincular número de WhatsApp en Waha.

Crear flujo inicial en n8n: WA → classifier → semantic_engine → actions.

Pruebas

Casos de prueba escritos: 5–10 diálogos típicos.

Verificar:

Que los JSON validan.

Que los flujos terminan sin error.

Que RAG trae texto correcto por category.

Demo al cliente

Explicar:

Qué hace hoy.

Qué se puede agregar después (Fase 2).

Dejar claro que los cambios se controlan vía contratos y flujos, no “magia negra”.

11. Convenciones y versionado
Ramas:

main: estable / producción.

develop: pruebas internas.

Commits:

Prefijo por área: [core], [rag], [security], [n8n], etc.

Versionado de motor semántico:

semantic_engine_v1, v1.1, v2, etc.

Cada versión se documenta con:

Cambios en prompt.

Cambios en intents.

Cambios en contratos.

12. Cuándo actualizar la BIBLIA
Actualizar este archivo cuando:

Se agregue o elimine una acción canon importante.

Cambie la política de RAG (chunking, metadata, filtros, etc.).

Cambien reglas de multi-tenancy o roles.

Se modifique el modelo de datos de:

tenants, users, documents, document_vectors.

Se modifiquen puertos, VPNs, túneles o política de seguridad base.

Se defina una nueva versión del Semantic Engine.
---

## 13. Motor RAG para Demo Comercial (Quest 2.1)

### 13.1 Propósito

La Demo Comercial requiere un **RAG independiente y efímero** que:

- Se aisle completamente del RAG de producción (multi-tenant).
- Permita subir un PDF de menú y generar respuestas contextualizadas.
- Se limpie completamente al cerrar la sesión (Neuralizer).
- No contamina índices o datos de otros clientes.

### 13.2 Arquitectura de aislamiento

**Categoría reservada:**

\\\
DEMO_RAG_CATEGORY = "demo_comercial"
\\\

Todos los chunks indexados en la Demo llevan esta categoría explícita en metadata.

**Prefijo de índice:**

\\\
DEMO_INDEX_PREFIX = "demo_v1"
\\\

Todos los vectores demo se crean bajo este prefijo, permitiendo limpieza masiva.

**Session-based isolation:**

Cada sesión demo crea un session_id (UUID). Los vectors se ligan a:
- session_id (ciclo de vida corto)
- DEMO_RAG_CATEGORY (filtro explícito)

Al cerrar la sesión (endpoint POST /demo/reset / Neuralizer), se borran **todos los vectores** con ese session_id + category.

### 13.3 Pipeline de ingesta (Demo)

1. Usuario sube PDF vía **POST /demo/upload** (THE LOADER).
2. Sistema procesa:
   - Valida que sea PDF (no admite otro formato).
   - Divide en chunks de ≤ MAX_CHUNK_SIZE = 1000 caracteres.
   - Genera embeddings (mock en Quest 2.1, OpenAI en Quest 2.2).
3. Almacena en document_vectors con metadata:
   \\\json
   {
     "session_id": "uuid-de-sesion",
     "category": "demo_comercial",
     "document_id": "uuid-del-pdf",
     "doc_type": "menu",
     "chunk_text": "Fragmento del PDF...",
     "embedding": [... vector ...]
   }
   \\\
4. Retorna estadística: {"chunks": N, "status": "indexed"}.

### 13.4 Pipeline de consulta (Demo)

1. Usuario envía pregunta vía **POST /demo/message** (THE SHOW).
2. Sistema:
   - Convierte pregunta a embedding.
   - Busca vectors con filtro session_id + DEMO_RAG_CATEGORY.
   - Retorna top-3 chunks más similares.
   - Envía a LLM: prompt + chunks + pregunta.
   - LLM devuelve respuesta contextualizada.
3. Respuesta se retorna al usuario.

### 13.5 Limpieza (Neuralizer)

1. Usuario llama **POST /demo/reset** con palabra clave secreta.
2. Sistema valida credencial (contraseña).
3. Ejecuta cleanup_session_vectors(session_id):
   - Borra **todos** los vectors con session_id + DEMO_RAG_CATEGORY.
   - Borra metadata asociada.
   - Cierra sesión en DB.
4. Retorna confirmación: {"status": "cleaned", "deleted_vectors": N}.

### 13.6 Protecciones y límites

**Tamaño de chunks:**
- Máximo: MAX_CHUNK_SIZE = 1000 caracteres (≈ 250 tokens).
- Razón: Mantener chunks relevantes y reducir latencia.

**Límite de documentos por sesión:**
- 1 PDF por sesión (para simplificar MVP).
- Si usuario sube otro, reemplaza el anterior (limpia vectores viejos primero).

**Timeout de sesión:**
- DEMO_SESSION_TIMEOUT_MINUTES = 30.
- Sesiones inactivas se limpian automáticamente (job async).

**No hay persistencia:**
- Los datos de demo se pierden al cerrar sesión.
- No se exportan ni se guardan para auditoría (es demo, no producción).

### 13.7 Constantes definidas (Quest 2.1)

Ubicación: pp/modules/demo/constants.py

\\\python
DEMO_RAG_CATEGORY = "demo_comercial"
DEMO_INDEX_PREFIX = "demo_v1"
MAX_CHUNK_SIZE = 1000
DEMO_SESSION_TIMEOUT_MINUTES = 30
DEMO_NEURALIZER_SECRET = "neuralizer"
\\\

### 13.8 Servicio RAG (Quest 2.1 - Contrato definido)

Ubicación: pp/services/demo_rag.py

**Clase:** DemoRAGService

**Métodos (firmas definidas, implementación en Quest 2.2):**

\\\python
def index_demo_document(
    self,
    session_id: str,
    file_path: str,
    db: Session
) -> dict:
    """
    Ingesta PDF → chunks → embeddings → indexación.
    
    Quest 2.1: Mock que retorna {"chunks": 0, "status": "pending_impl"}
    Quest 2.2: Implementación real con PDFLoader + OpenAI embeddings.
    """

def query_demo(
    self,
    session_id: str,
    question: str,
    db: Session
) -> str:
    """
    Búsqueda vectorial filtrada por session_id + categoría.
    
    Quest 2.1: Mock que retorna respuesta de prueba.
    Quest 2.2: Implementación real con similarity search + LLM.
    """

def cleanup_session_vectors(
    self,
    session_id: str,
    db: Session
) -> dict:
    """
    Borra todos los vectores de la sesión (Neuralizer).
    
    Quest 2.1: Mock que retorna {"deleted_vectors": 0, "status": "nothing_to_clean"}
    Quest 2.2: Implementación real con eliminación en vector DB.
    """
\\\

### 13.9 Integración con endpoints demo

- **THE LOADER** (\POST /demo/upload\):
  - Llama a \DemoRAGService.index_demo_document()\.
  - Retorna confirmación de chunks indexados.

- **THE SHOW** (\POST /demo/message\):
  - Llama a \DemoRAGService.query_demo()\.
  - Usa resultado para contexto de respuesta.

- **THE NEURALIZER** (\POST /demo/reset\):
  - Llama a \DemoRAGService.cleanup_session_vectors()\.
  - Verifica palabra clave secreta antes.

### 13.10 Roadmap (Quest 2.2 y más)

**Quest 2.2:** Integración OpenAI
- Implementar index_demo_document() con PDFLoader real.
- Implementar query_demo() con embeddings reales y similarity search.
- Implementar cleanup_session_vectors() en vector DB.

**Quest 2.3:** Multi-documento Demo
- Permitir n PDFs por sesión.
- Metadatos de fuente en cada chunk.

**Quest 2.4:** Analytics
- Logging de preguntas realizadas.
- Métricas de calidad de respuestas (feedback usuario).
``

### 13.11 Quest 2.2: Implementación Real (OpenAI + pgvector)

**Status:** COMPLETO - Commits 3b6894 → 9f9f080

**Cambios implementados:**

**1. Modelo DemoVector** (pp/modules/demo/models.py)
- Tabla demo_vectors con pgvector integration
- Campos:
  - mbedding: Vector(1536) para OpenAI text-embedding-3-small
  - chunk_number: Ordenamiento secuencial
  - chunk_text: Contenido del fragmento
  - chunk_metadata: JSON con category, source, etc.
  - session_id: FK a DemoSession (aislamiento por sesión)

**2. DemoRAGService real** (pp/services/demo_rag.py)
- _get_embedding(text): OpenAI API call
  - Modelo: text-embedding-3-small
  - Retorna: List[float] (1536 dims)
  
- _extract_text_from_pdf(file_path): pypdf PdfReader
  - Extrae texto de todas las páginas
  - Valida existencia y legibilidad
  
- _chunk_text(text): Smart chunking
  - Respeta MAX_CHUNK_SIZE (1000 chars)
  - Divide por párrafos (preserva contexto)
  - Retorna List[str]
  
- index_demo_document() (REAL):
  - Flujo: Extract → Chunk → Embed → Save
  - Genera embeddings con OpenAI para cada chunk
  - Guarda DemoVector en pgvector
  - Transaccional (rollback si falla)
  - Retorna: {chunks: N, status: 'indexed', ...}
  
- query_demo() (REAL):
  - Embed pregunta con OpenAI
  - Busca similaridad con <-> operator (pgvector cosine)
  - Retorna top-3 chunks como contexto
  
- cleanup_session_vectors() (REAL):
  - Borra todos los vectors de la sesión
  - Retorna: {deleted_vectors: N, status: 'cleaned', ...}

**3. Integración Router** (pp/routers/demo.py)
- POST /demo/upload:
  - Valida PDF (solo PDF permitido)
  - Llama index_demo_document() después de guardar
  - No falla si RAG falla (graceful degradation)
  - Retorna chunks_indexed en respuesta
  
- POST /demo/message:
  - Llama query_demo() para retrieval
  - Retorna contexto RAG como respuesta bot
  - Fallback a error message si RAG falla
  
- POST /demo/reset (Neuralizer):
  - Llama cleanup_session_vectors() antes de cerrar
  - Retorna deleted_vectors_count
  - Limpia vectores automáticamente

**Manejo de errores:**
- try/catch en todos los niveles
- db.rollback() en transacciones fallidas
- Logging detallado para debugging
- Graceful degradation: RAG errors no rompen funcionalidad core

**Testing:**
✓ Imports validados
✓ Router carga con 4 endpoints
✓ Type annotations correctas
✓ pgvector Vector(1536) funcionando
✓ OpenAI API ready

**Próximos pasos (Quest 2.3+):**
- Integrar OpenAI GPT para generar respuestas con contexto RAG
- Agregar multi-PDF support
- Implementar metadata extraction mejorada (fuente, página)
- Analytics: logging de preguntas y calidad de respuestas

### 13.12 Quest 2.2 Extension: GPT-4o Vision Support

**Status:** COMPLETO - Commit c37ca89

**Objetivo:** Permitir ingesta de imágenes (JPG/PNG) además de PDF, usando GPT-4o para extracción de texto.

**Casos de uso:**
- Menús de restaurante (foto del cartel/pizarra)
- Documentos escaneados (pólizas, recibos, contratos)
- Fotos de pizarras/notas manuscritas
- Capturas de pantalla de tablas o catálogos

**Cambios implementados:**

**1. Router** (pp/routers/demo.py)
- Validación por MIME type (no extensión):
  - pplication/pdf → .pdf
  - image/jpeg → .jpg
  - image/png → .png
- Error claro si tipo no permitido

**2. RAG Service** (pp/services/demo_rag.py)

New method: _extract_text_from_image(file_path: str) -> str
- Lee archivo binario
- Codifica a base64 string
- Llama GPT-4o Vision API:
  `python
  client.chat.completions.create(
      model="gpt-4o",
      messages=[
          {
              "role": "user",
              "content": [
                  {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}},
                  {"type": "text", "text": "Prompt de transcripción..."},
              ]
          }
      ],
      max_tokens=4096
  )
  `
- Prompt: "Transcribe todo el texto. Si es menú, lista platos con precios."
- Retorna: Texto extraído (raises ValueError si falla)

Updated: index_demo_document()
- Detecta extensión:
  - .pdf → _extract_text_from_pdf()
  - .jpg/.png → _extract_text_from_image()
- Ambas rutas convergen en:
  - Chunking (MAX_CHUNK_SIZE = 1000 chars)
  - Embedding (text-embedding-3-small)
  - Guardado (pgvector)
- Response incluye "file_type": "pdf" | "image"

**Flujo unificado:**

`
PDF Input:
  pypdf.PdfReader → texto completo → _chunk_text()
  
Image Input:
  base64 encode → GPT-4o Vision → texto extraído → _chunk_text()

Ambos:
  → chunks lista
  → for each chunk: _get_embedding() → Vector(1536)
  → db.add_all(demo_vectors)
  → pgvector similarity search (query_demo)
`

**Ventajas de Vision:**
- Multi-idioma (GPT-4o es multilingual)
- Comprensión de contexto (entiende qué es un menú vs. un contrato)
- Limpieza de ruido (ignora marcas de agua, sombras)
- Tablas parseadas a formato legible

**Error handling:**
- FileNotFoundError si archivo no existe
- ValueError si GPT-4o retorna empty
- Graceful fallback: Log error pero no rompe upload

**Testing:**
✓ _extract_text_from_image() signature verified
✓ _extract_text_from_pdf() signature preserved
✓ Router valida MIME types correctamente
✓ File routing logic functional

**Limitaciones actuales:**
- 1 documento por sesión (diseño MVP)
- Max 4096 tokens por imagen (tunable)
- Timeout de sesión 30 min

**Próximos pasos (Quest 2.3+):**
- Integrar GPT-4 Turbo para respuestas + contexto RAG
- Multi-doc: permitir multiple files por sesión
- Metadata extraction mejorada (extractar fuente, página, fecha si visible)
- Analytics: log preguntas, calidad de respuestas (feedback loop)
- Cached embeddings para documentos repetidos
