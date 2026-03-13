-- PersonaKB PostgreSQL initialization script
-- Run automatically by Docker on first start

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable uuid generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Verify extensions
DO $$
BEGIN
    RAISE NOTICE 'Extensions loaded: vector, pgcrypto';
END
$$;
