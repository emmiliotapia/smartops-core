# SmartOps Data Layer | PostgreSQL + pgvector

## Descripcion
Capa de persistencia que almacena:
- Documentos & Vectores: Para RAG (Retrieval-Augmented Generation)
- Estado del Sistema: Logs de ejecuciones, webhooks, errores
- Multi-Tenant Data: Aislamiento de datos por cliente

## Estructura

```
smartops_data/
└── postgres/          # Volumen persistente de PostgreSQL
    └── (datos en PostgreSQL 16 + pgvector)
```

## Schema de Base de Datos

### Tabla: documents (Almacenamiento RAG)

```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    document_name VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    source VARCHAR(100),      -- "pdf", "txt", "website", etc.
    metadata JSONB,           -- tags, categoria, fecha, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_tenant FOREIGN KEY(tenant_id) REFERENCES tenants(id)
);

CREATE INDEX idx_documents_tenant ON documents(tenant_id);
```

### Tabla: document_vectors (pgvector)

```sql
CREATE TABLE document_vectors (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER,      -- Si el doc esta dividido en chunks
    content_chunk TEXT NOT NULL,
    embedding vector(1536),   -- Embedding de OpenAI (1536 dims)
    chunk_metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_document FOREIGN KEY(document_id) REFERENCES documents(id)
);

-- Indice para busquedas rapidas (cosine similarity)
CREATE INDEX idx_embedding ON document_vectors USING ivfflat (embedding vector_cosine_ops);
```

### Tabla: executions (Auditoria)

```sql
CREATE TABLE executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(50) NOT NULL,
    intent VARCHAR(100) NOT NULL,
    parameters JSONB,
    status VARCHAR(20),       -- "pending", "success", "failed"
    result JSONB,
    n8n_workflow_id VARCHAR(100),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    CONSTRAINT fk_tenant FOREIGN KEY(tenant_id) REFERENCES tenants(id)
);

CREATE INDEX idx_executions_tenant ON executions(tenant_id);
CREATE INDEX idx_executions_status ON executions(status);
```

### Tabla: tenants (Multi-tenancy)

```sql
CREATE TABLE tenants (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    api_key VARCHAR(255) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);
```

## Inicializacion de BD

**Archivo: smartops_data/init.sql** (crear si no existe)

```sql
-- Activar extensiones necesarias
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Ejecutar schema anterior (documentos, vectores, etc.)
```

En docker-compose.yml, agregar al servicio db_core:

```yaml
db_core:
  environment:
    POSTGRES_INITDB_ARGS: "-c shared_preload_libraries=vector"
  volumes:
    - ./smartops_data/postgres:/var/lib/postgresql/data
    - ./smartops_data/init.sql:/docker-entrypoint-initdb.d/init.sql
```

## Consultas RAG Comunes

### Busqueda por similaridad (Cosine Distance)

```sql
SELECT 
    dv.id,
    dv.content_chunk,
    dv.document_id,
    1 - (dv.embedding <=> '[0.1, 0.2, ..., 0.5]'::vector) AS similarity
FROM document_vectors dv
JOIN documents d ON dv.document_id = d.id
WHERE d.tenant_id = 'acme-corp-001'
    AND (1 - (dv.embedding <=> '[...]'::vector)) > 0.7
ORDER BY similarity DESC
LIMIT 5;
```

## Backup & Restore

**Hacer backup:**
```bash
docker exec smartops_core_db pg_dump -U root smartops_core > backup_$(date +%Y%m%d_%H%M%S).sql
```

**Restaurar:**
```bash
docker exec -i smartops_core_db psql -U root smartops_core < backup.sql
```

## Monitoreo

**Verificar conexion:**
```bash
docker exec smartops_core_db psql -U root -d smartops_core -c "\dt"
```

**Ver tamano de BD:**
```sql
SELECT pg_size_pretty(pg_database_size('smartops_core')) AS size;
```

## Seguridad

- [ ] Cambiar contraseña por defecto root en produccion
- [ ] Usar PGPASS en scripts de backup
- [ ] Encriptar conexiones SSL en VPS
- [ ] Backups automaticos cada 6 horas
- [ ] Replicacion a standby en caso de fallos

## Performance Tips

1. **Indices pgvector**: Usar ivfflat para embeddings > 100k
2. **Particionamiento**: Por tenant_id si escala mucho
3. **Connection Pooling**: Usar PgBouncer en produccion
4. **Vacuum automatico**: autovacuum = on
