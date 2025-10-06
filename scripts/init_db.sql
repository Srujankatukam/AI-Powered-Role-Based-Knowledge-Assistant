-- Initialize database for AI Knowledge Assistant

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS knowledge_assistant;

-- Use the database
\c knowledge_assistant;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create indexes for better performance
-- These will be created by SQLAlchemy, but we can add additional ones here

-- Full-text search index for documents
-- CREATE INDEX IF NOT EXISTS idx_documents_content_fts ON documents USING gin(to_tsvector('english', content));

-- Performance indexes
-- CREATE INDEX IF NOT EXISTS idx_documents_access_level ON documents(access_level);
-- CREATE INDEX IF NOT EXISTS idx_documents_department ON documents(department);
-- CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);
-- CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
-- CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE knowledge_assistant TO postgres;