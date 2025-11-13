-- Migração: Adiciona campo chefia_imediata_id para Workflow Automático
-- Data: 2025-11-13
-- Descrição: Implementa fluxo de aprovação automático estilo EBSERH

-- Adiciona coluna chefia_imediata_id na tabela documentos
ALTER TABLE documentos
ADD COLUMN IF NOT EXISTS chefia_imediata_id INTEGER REFERENCES usuarios(id);

-- Adiciona índice para performance
CREATE INDEX IF NOT EXISTS idx_documentos_chefia_imediata
ON documentos(chefia_imediata_id);

-- Comentários para documentação
COMMENT ON COLUMN documentos.chefia_imediata_id IS 'ID da chefia imediata responsável pela primeira análise no fluxo de aprovação';

-- Atualiza documentos existentes (opcional - define chefia_imediata como NULL por padrão)
-- Se quiser definir uma chefia padrão para documentos existentes, descomente:
-- UPDATE documentos
-- SET chefia_imediata_id = (SELECT id FROM usuarios WHERE perfil = 'gerente' LIMIT 1)
-- WHERE chefia_imediata_id IS NULL AND status = 'Novo';

-- Adiciona tipo de tarefa "Realizar Correção" no config se necessário
-- (Já existe no código, apenas documentando)
