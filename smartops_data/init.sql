-- ========================================================================
-- SmartOps Database Initialization
-- Initializes PostgreSQL with pgvector extension
-- ========================================================================

-- Create pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create demo_sessions table
CREATE TABLE IF NOT EXISTS demo_sessions (
    id UUID PRIMARY KEY,
    business_name VARCHAR(255) NOT NULL,
    business_type VARCHAR(100) NOT NULL,
    active BOOLEAN DEFAULT true,
    source_file_path VARCHAR(500),
    vector_collection_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create demo_leads table
CREATE TABLE IF NOT EXISTS demo_leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES demo_sessions(id) ON DELETE CASCADE,
    prospect_name VARCHAR(255),
    prospect_phone VARCHAR(20),
    prospect_email VARCHAR(255),
    interest_level VARCHAR(50),
    notes JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create demo_vectors table (for RAG)
CREATE TABLE IF NOT EXISTS demo_vectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES demo_sessions(id) ON DELETE CASCADE,
    chunk_number INTEGER,
    chunk_text TEXT NOT NULL,
    embedding vector(1536),
    chunk_metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_demo_sessions_active ON demo_sessions(active);
CREATE INDEX IF NOT EXISTS idx_demo_sessions_created_at ON demo_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_demo_leads_session_id ON demo_leads(session_id);
CREATE INDEX IF NOT EXISTS idx_demo_vectors_session_id ON demo_vectors(session_id);
CREATE INDEX IF NOT EXISTS idx_demo_vectors_embedding ON demo_vectors USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create indexes for pgvector similarity search
CREATE INDEX IF NOT EXISTS idx_demo_vectors_embedding_cosine 
ON demo_vectors USING ivfflat (embedding vector_cosine_ops);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO smartops;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO smartops;

-- Create views for quick access
CREATE OR REPLACE VIEW active_demo_sessions AS
SELECT 
    id,
    business_name,
    business_type,
    source_file_path,
    created_at,
    (SELECT COUNT(*) FROM demo_vectors WHERE session_id = demo_sessions.id) as vector_count,
    (SELECT COUNT(*) FROM demo_leads WHERE session_id = demo_sessions.id) as lead_count
FROM demo_sessions
WHERE active = true
ORDER BY created_at DESC;

GRANT SELECT ON active_demo_sessions TO smartops;

-- Insert default data (optional)
-- INSERT INTO demo_sessions (id, business_name, business_type) 
-- VALUES (gen_random_uuid(), 'Demo Restaurant', 'food');
