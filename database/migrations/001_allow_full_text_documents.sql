-- CampusIQ now uses PostgreSQL full-text search instead of remote embeddings.
-- Existing vector values are retained but are no longer queried.
ALTER TABLE campus_documents
ALTER COLUMN embedding DROP NOT NULL;
