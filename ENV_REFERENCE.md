# Environment Variables Reference

**IMPORTANT:** This document explains all environment variables. For template, see `.env.example`. For actual credentials, edit `.env` (NOT tracked in git).

---

## 🔑 Critical Variables (MUST be configured)

### DATABASE_URL
```
Description: PostgreSQL connection string with pgvector support
Format:      postgresql://user:password@host:port/database
Example:     postgresql://root:mypassword@localhost:5433/smartops_core
Location:    .env (NEVER in git)
Impact:      Without this, API cannot start
```

**Alternative:** Use individual components instead of DATABASE_URL:
```env
DB_HOST=localhost
DB_PORT=5433
DB_USER=root
DB_PASSWORD=mypassword
DB_NAME=smartops_core
```

### OPENAI_API_KEY
```
Description: OpenAI API key for embeddings + vision
Format:      sk-... (from https://platform.openai.com/api-keys)
Location:    .env (NEVER in git)
Impact:      Without this, RAG and image processing will fail
Models:      
  - text-embedding-3-small (1536 dims for RAG)
  - gpt-4o (for image OCR/Vision)
```

---

## 📊 Important Variables (Recommended to configure)

### RAG Configuration
```env
# Maximum characters per chunk when splitting documents
RAG_MAX_CHUNK_SIZE=1000

# Similarity threshold (0.0-1.0) for vector search
RAG_SIMILARITY_THRESHOLD=0.5
```

### Demo Session Configuration
```env
# Session timeout in minutes before auto-cleanup
DEMO_SESSION_TIMEOUT_MINUTES=30

# Secret word for THE NEURALIZER endpoint (cleanup)
DEMO_NEURALIZER_SECRET=your_secret_word
```

---

## 🎛️ Optional Variables (Have sensible defaults)

### Server Configuration
```env
APP_ENV=development          # development or production
APP_PORT=8000               # Server port
APP_HOST=0.0.0.0            # Server bind address
```

### OpenAI Models
```env
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_VISION_MODEL=gpt-4o
OPENAI_LLM_MODEL=gpt-4-turbo     # For Phase 2: LLM responses
```

### Logging
```env
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json             # json or text
LOG_FILE=logs/smartops.log  # Log file path
```

### CORS
```env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Feature Flags
```env
ENABLE_VISION=true          # Enable image processing
ENABLE_RAG=true             # Enable document indexing
ENABLE_LLM_RESPONSES=false  # Phase 2 feature
```

---

## 📋 By Component

### PostgreSQL + pgvector
**Variables:**
- `DATABASE_URL` or `(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)`
- `DB_POOL_SIZE=5`
- `DB_MAX_OVERFLOW=10`

**Purpose:** Connect to PostgreSQL database with pgvector extension for vector storage

**Models:** DemoSession, DemoLead, DemoVector (1536-dim embeddings)

---

### OpenAI Integration
**Variables:**
- `OPENAI_API_KEY` (CRITICAL)
- `OPENAI_EMBEDDING_MODEL` (default: text-embedding-3-small)
- `OPENAI_VISION_MODEL` (default: gpt-4o)
- `OPENAI_REQUEST_TIMEOUT=30`

**Purpose:** Generate embeddings for RAG and process images for OCR

**Usage:**
- Embeddings: Extract text features from documents
- Vision: Transcribe menus and images

---

### RAG Pipeline
**Variables:**
- `RAG_CATEGORY=demo_comercial` (multi-tenant support)
- `RAG_INDEX_PREFIX=demo_v1` (vector naming)
- `RAG_MAX_CHUNK_SIZE=1000` (document chunking)
- `RAG_SIMILARITY_THRESHOLD=0.5` (search threshold)

**Purpose:** Index documents, chunk text, generate embeddings, search vectors

---

### Demo Sessions
**Variables:**
- `DEMO_SESSION_TIMEOUT_MINUTES=30` (auto-cleanup)
- `DEMO_NEURALIZER_SECRET` (cleanup authentication)

**Purpose:** Manage user sessions, cleanup old data

---

## 🚀 Quick Setup

1. **Copy template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit .env** with your values:
   ```env
   # REQUIRED
   DATABASE_URL=postgresql://root:mypass@localhost:5433/smartops_core
   OPENAI_API_KEY=sk-proj-...

   # OPTIONAL (can use defaults)
   DEMO_SESSION_TIMEOUT_MINUTES=30
   ```

3. **Verify setup:**
   ```bash
   python setup_validation.py
   ```

---

## 🔐 Security Best Practices

✅ **DO:**
- Store credentials in `.env` (NOT in git)
- Use `.env.example` with placeholders only
- Rotate API keys regularly
- Use strong database passwords

❌ **DON'T:**
- Commit `.env` to git
- Hardcode credentials in code
- Share credentials in documentation
- Use default passwords in production

---

## 📚 Additional Resources

- **Full list:** See `.env.standard` for complete reference
- **Template:** See `.env.example` for getting started
- **Setup:** See `QUICK_START.md` for installation guide
