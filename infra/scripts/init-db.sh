#!/bin/bash
# PostgreSQL Database Initialization Script
# This script runs automatically when the PostgreSQL container starts for the first time.
# It's mounted to /docker-entrypoint-initdb.d/ which PostgreSQL executes on initialization.

set -e

# Database is already created by POSTGRES_DB environment variable
# This script can be used for:
# 1. Creating additional databases
# 2. Setting up extensions
# 3. Running initial migrations
# 4. Seeding initial data

echo "Running database initialization script..."

# Enable required PostgreSQL extensions if needed
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Example: Enable extensions
    -- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    -- CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    
    -- Example: Create additional schemas
    -- CREATE SCHEMA IF NOT EXISTS qonfido;
    
    -- Log initialization
    SELECT 'Database initialized successfully' AS status;
EOSQL

echo "Database initialization completed!"

