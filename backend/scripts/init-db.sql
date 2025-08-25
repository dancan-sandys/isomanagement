-- Database initialization script for ISO 22000 FSMS
-- This script runs when the PostgreSQL container starts for the first time

-- Create extensions if they don't exist
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Set timezone
SET timezone = 'UTC';

-- Create additional databases if needed
-- CREATE DATABASE iso22000_fsms_test;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE iso22000_fsms TO iso22000_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO iso22000_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO iso22000_user;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO iso22000_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO iso22000_user;
