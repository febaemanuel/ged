-- ============================================
-- Script de Inicialização do Banco de Dados
-- Sistema GED EBSERH
-- ============================================

-- Garante encoding UTF-8
SET client_encoding = 'UTF8';

-- Cria database evolution_db para Evolution API (se usar WhatsApp)
-- NOTA: Este comando pode falhar se já executado dentro do container
-- mas não causa problemas
DO
$$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'evolution_db') THEN
        CREATE DATABASE evolution_db
            WITH ENCODING = 'UTF8'
            LC_COLLATE = 'pt_BR.UTF-8'
            LC_CTYPE = 'pt_BR.UTF-8'
            TEMPLATE = template0;
    END IF;
END
$$;

-- Extensões úteis para ged_db
\c ged_db;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- Para busca full-text

-- Mensagem de sucesso
SELECT 'Banco de dados inicializado com sucesso!' as status;
