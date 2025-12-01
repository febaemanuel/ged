-- ============================================
-- Migration: Adiciona Índices de Performance
-- Data: 2025-12-01
-- Descrição: Corrige problema crítico de performance
-- ============================================

-- DOCUMENTOS: Índices simples
CREATE INDEX IF NOT EXISTS ix_documentos_setor ON documentos(setor);
CREATE INDEX IF NOT EXISTS ix_documentos_abrangencia ON documentos(abrangencia);
CREATE INDEX IF NOT EXISTS ix_documentos_tipo_documento ON documentos(tipo_documento);
CREATE INDEX IF NOT EXISTS ix_documentos_data_vencimento ON documentos(data_vencimento);
CREATE INDEX IF NOT EXISTS ix_documentos_data_publicacao ON documentos(data_publicacao);
CREATE INDEX IF NOT EXISTS ix_documentos_data_criacao ON documentos(data_criacao);

-- DOCUMENTOS: Índices compostos para queries complexas
CREATE INDEX IF NOT EXISTS ix_doc_setor_tipo ON documentos(setor, tipo_documento);
CREATE INDEX IF NOT EXISTS ix_doc_status_vencimento ON documentos(status, data_vencimento);
CREATE INDEX IF NOT EXISTS ix_doc_abrangencia_setor ON documentos(abrangencia, setor);
CREATE INDEX IF NOT EXISTS ix_doc_criador_status ON documentos(criador_id, status);
CREATE INDEX IF NOT EXISTS ix_doc_data_criacao_status ON documentos(data_criacao DESC, status);

-- DOCUMENTOS: Índice GIN para busca em JSON (metadados)
CREATE INDEX IF NOT EXISTS ix_doc_metadados_gin ON documentos USING GIN (metadados_json jsonb_path_ops);

-- DOCUMENTOS: Adiciona coluna deleted_at para soft delete
ALTER TABLE documentos ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
CREATE INDEX IF NOT EXISTS ix_documentos_deleted_at ON documentos(deleted_at);

-- DOCUMENTOS: Adiciona colunas de auditoria
ALTER TABLE documentos ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();
ALTER TABLE documentos ADD COLUMN IF NOT EXISTS updated_by_id INTEGER REFERENCES usuarios(id);

-- TAREFAS: Índices de performance
CREATE INDEX IF NOT EXISTS ix_tarefas_responsavel_concluida ON tarefas(responsavel_id, concluida);
CREATE INDEX IF NOT EXISTS ix_tarefas_documento_concluida ON tarefas(documento_id, concluida);
CREATE INDEX IF NOT EXISTS ix_tarefas_prazo ON tarefas(prazo) WHERE concluida = false;

-- LOGS_IA: Índice para consultas de auditoria
CREATE INDEX IF NOT EXISTS ix_logs_ia_data_chamada ON logs_ia(data_chamada DESC);

-- NOTIFICACOES: Índices para queries de usuário
CREATE INDEX IF NOT EXISTS ix_notificacoes_usuario_lida ON notificacoes(usuario_id, lida);
CREATE INDEX IF NOT EXISTS ix_notificacoes_data_criacao ON notificacoes(data_criacao DESC);

-- COMENTARIOS: Índices para threads
CREATE INDEX IF NOT EXISTS ix_comentarios_documento_criacao ON comentarios(documento_id, data_criacao DESC);
CREATE INDEX IF NOT EXISTS ix_comentarios_pai_id ON comentarios(pai_id) WHERE pai_id IS NOT NULL;

-- BLOCOS_ASSINATURA: Índices
CREATE INDEX IF NOT EXISTS ix_blocos_documento_status ON blocos_assinatura(documento_id, status);

-- ITENS_BLOCO_ASSINATURA: Índices
CREATE INDEX IF NOT EXISTS ix_itens_bloco_aprovador_status ON itens_bloco_assinatura(aprovador_id, status);

-- CONVERSACOES_WHATSAPP: Índice único para telefone
CREATE UNIQUE INDEX IF NOT EXISTS ix_conversacoes_telefone ON conversacoes_whatsapp(telefone);

-- LOGS_WHATSAPP: Índices para auditoria
CREATE INDEX IF NOT EXISTS ix_logs_whatsapp_criado_em ON logs_whatsapp(criado_em DESC);
CREATE INDEX IF NOT EXISTS ix_logs_whatsapp_usuario ON logs_whatsapp(usuario_id);

-- Atualiza estatísticas do PostgreSQL
ANALYZE;

-- Mensagem de sucesso
SELECT 'Migration concluída: Índices adicionados com sucesso!' AS status;
