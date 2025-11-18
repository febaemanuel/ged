-- Migração: Adicionar campos abrangencia e autores
-- Data: 2025-11-18
-- Descrição: Adiciona campo de abrangência aos modelos Documento e ListaMestra,
--            e campo de autores ao modelo Documento para suportar o novo
--            padrão de codificação TIPO.SETOR-ABRANGENCIA.NUMERO

-- 1. Adicionar campo abrangencia à tabela documentos
ALTER TABLE documentos ADD COLUMN IF NOT EXISTS abrangencia VARCHAR(100);

-- 2. Adicionar campo autores à tabela documentos
ALTER TABLE documentos ADD COLUMN IF NOT EXISTS autores TEXT;

-- 3. Adicionar campo abrangencia à tabela lista_mestra
ALTER TABLE lista_mestra ADD COLUMN IF NOT EXISTS abrangencia VARCHAR(100);

-- 4. Comentários nas colunas
COMMENT ON COLUMN documentos.abrangencia IS 'Abrangência do documento (CHUFC, HUWC, MEAC, etc)';
COMMENT ON COLUMN documentos.autores IS 'Autores do documento extraídos pela IA (formato: Nome1, Nome2, ...)';
COMMENT ON COLUMN lista_mestra.abrangencia IS 'Abrangência do documento (CHUFC, HUWC, MEAC, etc)';

-- 5. Atualizar registros existentes com abrangência padrão (se necessário)
-- Comentário: Ajuste conforme necessário para sua base de dados
-- UPDATE documentos SET abrangencia = 'CHUFC' WHERE abrangencia IS NULL;
-- UPDATE lista_mestra SET abrangencia = 'CHUFC' WHERE abrangencia IS NULL;
