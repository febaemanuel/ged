-- ============================================================================
-- MIGRATION: Workflow UGQ Centralizado - Sistema GED EBSERH
-- Versão: 2.0
-- Data: 2025-01-13
-- Descrição: Adiciona tabelas e campos para o workflow oficial EBSERH
--            centralizado na Unidade de Gestão da Qualidade (UGQ)
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. TABELA: lista_mestra
-- Descrição: Controle de códigos definitivos e versionamento de documentos
-- ============================================================================
CREATE TABLE IF NOT EXISTS lista_mestra (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,                    -- POP.SETOR-001
    tipo VARCHAR(50) NOT NULL,                             -- POP, Manual, Protocolo, Formulário
    titulo VARCHAR(200) NOT NULL,
    setor VARCHAR(100) NOT NULL,
    versao VARCHAR(20) NOT NULL,                           -- v1.0, v2.0
    data_publicacao TIMESTAMP NOT NULL,
    documento_id INTEGER REFERENCES documentos(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'EM_APROVACAO',             -- EM_APROVACAO, VIGENTE, ANTIGO, OBSOLETO
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_lista_mestra_codigo ON lista_mestra(codigo);
CREATE INDEX idx_lista_mestra_documento_id ON lista_mestra(documento_id);
CREATE INDEX idx_lista_mestra_status ON lista_mestra(status);
CREATE INDEX idx_lista_mestra_tipo_setor ON lista_mestra(tipo, setor);

COMMENT ON TABLE lista_mestra IS 'Lista Mestra de Documentos da UGQ - Controle de códigos e versões';
COMMENT ON COLUMN lista_mestra.codigo IS 'Código definitivo do documento (ex: POP.OPERACOES-001)';
COMMENT ON COLUMN lista_mestra.status IS 'EM_APROVACAO | VIGENTE | ANTIGO | OBSOLETO';

-- ============================================================================
-- 2. TABELA: blocos_assinatura
-- Descrição: Bloco de Assinatura gerenciado pelo Validador UGQ
-- ============================================================================
CREATE TABLE IF NOT EXISTS blocos_assinatura (
    id SERIAL PRIMARY KEY,
    documento_id INTEGER NOT NULL REFERENCES documentos(id) ON DELETE CASCADE,
    criador_id INTEGER NOT NULL REFERENCES usuarios(id),   -- Validador UGQ
    modo VARCHAR(20) NOT NULL,                             -- 'sequencial' ou 'concomitante'
    status VARCHAR(50) DEFAULT 'Em Andamento',             -- Em Andamento, Aprovado, Reprovado
    observacoes TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_conclusao TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_blocos_assinatura_documento_id ON blocos_assinatura(documento_id);
CREATE INDEX idx_blocos_assinatura_criador_id ON blocos_assinatura(criador_id);
CREATE INDEX idx_blocos_assinatura_status ON blocos_assinatura(status);

COMMENT ON TABLE blocos_assinatura IS 'Blocos de Assinatura para aprovação final de documentos';
COMMENT ON COLUMN blocos_assinatura.modo IS 'sequencial (ordem) ou concomitante (paralelo)';
COMMENT ON COLUMN blocos_assinatura.status IS 'Em Andamento | Aprovado | Reprovado';

-- ============================================================================
-- 3. TABELA: itens_bloco_assinatura
-- Descrição: Cada aprovador no bloco de assinatura
-- ============================================================================
CREATE TABLE IF NOT EXISTS itens_bloco_assinatura (
    id SERIAL PRIMARY KEY,
    bloco_id INTEGER NOT NULL REFERENCES blocos_assinatura(id) ON DELETE CASCADE,
    aprovador_id INTEGER NOT NULL REFERENCES usuarios(id),
    ordem INTEGER NOT NULL,                                -- 1, 2, 3... (para modo sequencial)
    status VARCHAR(50) DEFAULT 'Pendente',                 -- Pendente, Aprovado, Reprovado
    parecer TEXT,
    data_assinatura TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(bloco_id, ordem)                                -- Não pode ter 2 aprovadores na mesma ordem
);

CREATE INDEX idx_itens_bloco_bloco_id ON itens_bloco_assinatura(bloco_id);
CREATE INDEX idx_itens_bloco_aprovador_id ON itens_bloco_assinatura(aprovador_id);
CREATE INDEX idx_itens_bloco_status ON itens_bloco_assinatura(status);
CREATE INDEX idx_itens_bloco_ordem ON itens_bloco_assinatura(bloco_id, ordem);

COMMENT ON TABLE itens_bloco_assinatura IS 'Itens individuais do bloco - cada aprovador';
COMMENT ON COLUMN itens_bloco_assinatura.ordem IS 'Ordem de assinatura (importante no modo sequencial)';
COMMENT ON COLUMN itens_bloco_assinatura.status IS 'Pendente | Aprovado | Reprovado';

-- ============================================================================
-- 4. TABELA: validacoes_ugq
-- Descrição: Registro de validações técnicas feitas pelo Validador UGQ
-- ============================================================================
CREATE TABLE IF NOT EXISTS validacoes_ugq (
    id SERIAL PRIMARY KEY,
    documento_id INTEGER NOT NULL REFERENCES documentos(id) ON DELETE CASCADE,
    validador_id INTEGER NOT NULL REFERENCES usuarios(id),
    data_validacao TIMESTAMP NOT NULL,
    declaracao_sei VARCHAR(50),                            -- Número da Declaração SEI (ex: 28538223)
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_validacoes_ugq_documento_id ON validacoes_ugq(documento_id);
CREATE INDEX idx_validacoes_ugq_validador_id ON validacoes_ugq(validador_id);

COMMENT ON TABLE validacoes_ugq IS 'Registro de validações técnicas da UGQ';
COMMENT ON COLUMN validacoes_ugq.declaracao_sei IS 'Número do modelo SEI usado (ex: 28538223)';

-- ============================================================================
-- 5. ADICIONAR CAMPOS EM TABELAS EXISTENTES
-- ============================================================================

-- Adiciona campo metadata_json em tarefas (para dados do bloco de assinatura)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='tarefas' AND column_name='metadata_json') THEN
        ALTER TABLE tarefas ADD COLUMN metadata_json TEXT;
        COMMENT ON COLUMN tarefas.metadata_json IS 'JSON com metadados extras (ex: bloco_id, item_id, modo)';
    END IF;
END $$;

-- Adiciona campo arquivo_final em documentos (PDF codificado final)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='documentos' AND column_name='arquivo_final') THEN
        ALTER TABLE documentos ADD COLUMN arquivo_final VARCHAR(255);
        COMMENT ON COLUMN documentos.arquivo_final IS 'Caminho do PDF final codificado para publicação';
    END IF;
END $$;

-- Adiciona campo codigo_definitivo em documentos
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='documentos' AND column_name='codigo_definitivo') THEN
        ALTER TABLE documentos ADD COLUMN codigo_definitivo VARCHAR(50);
        COMMENT ON COLUMN documentos.codigo_definitivo IS 'Código definitivo gerado pela UGQ (ex: POP.OPERACOES-001)';
    END IF;
END $$;

-- Adiciona campo versao em documentos
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='documentos' AND column_name='versao') THEN
        ALTER TABLE documentos ADD COLUMN versao VARCHAR(20);
        COMMENT ON COLUMN documentos.versao IS 'Versão do documento (ex: v1.0, v2.0)';
    END IF;
END $$;

-- Adiciona campo versao_anterior_id em documentos (para controle de revisões)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='documentos' AND column_name='versao_anterior_id') THEN
        ALTER TABLE documentos ADD COLUMN versao_anterior_id INTEGER REFERENCES documentos(id);
        COMMENT ON COLUMN documentos.versao_anterior_id IS 'ID do documento que esta versão substituiu';
    END IF;
END $$;

-- ============================================================================
-- 6. ATUALIZAR PERFIS DE USUÁRIOS
-- ============================================================================

-- Nota: Os perfis 'qualidade_triador' e 'qualidade_validador' serão criados
-- no script init_database.py. Esta migration apenas garante que o banco
-- suporta esses perfis.

COMMENT ON COLUMN usuarios.perfil IS 'comum | responsavel_interno | gerente | administrador | qualidade_triador | qualidade_validador';

-- ============================================================================
-- 7. CRIAR VIEW: Documentos com Lista Mestra
-- ============================================================================

CREATE OR REPLACE VIEW view_documentos_lista_mestra AS
SELECT
    d.*,
    lm.codigo as lista_mestra_codigo,
    lm.versao as lista_mestra_versao,
    lm.status as lista_mestra_status,
    lm.data_publicacao as lista_mestra_data_publicacao
FROM documentos d
LEFT JOIN lista_mestra lm ON d.id = lm.documento_id
ORDER BY d.id DESC;

COMMENT ON VIEW view_documentos_lista_mestra IS 'View combinada de documentos com dados da Lista Mestra';

-- ============================================================================
-- 8. CRIAR VIEW: Status de Blocos de Assinatura
-- ============================================================================

CREATE OR REPLACE VIEW view_blocos_assinatura_status AS
SELECT
    b.id as bloco_id,
    b.documento_id,
    b.modo,
    b.status as bloco_status,
    d.titulo as documento_titulo,
    d.codigo_definitivo,
    COUNT(i.id) as total_aprovadores,
    COUNT(CASE WHEN i.status = 'Aprovado' THEN 1 END) as aprovadores_aprovaram,
    COUNT(CASE WHEN i.status = 'Reprovado' THEN 1 END) as aprovadores_reprovaram,
    COUNT(CASE WHEN i.status = 'Pendente' THEN 1 END) as aprovadores_pendentes,
    b.data_criacao,
    b.data_conclusao
FROM blocos_assinatura b
JOIN documentos d ON b.documento_id = d.id
LEFT JOIN itens_bloco_assinatura i ON b.id = i.bloco_id
GROUP BY b.id, b.documento_id, b.modo, b.status, d.titulo, d.codigo_definitivo, b.data_criacao, b.data_conclusao
ORDER BY b.data_criacao DESC;

COMMENT ON VIEW view_blocos_assinatura_status IS 'View com estatísticas de aprovação dos blocos';

-- ============================================================================
-- 9. CRIAR FUNÇÃO: Próximo Código Disponível
-- ============================================================================

CREATE OR REPLACE FUNCTION gerar_proximo_codigo(p_tipo VARCHAR, p_setor VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    v_ultimo_numero INTEGER;
    v_novo_numero INTEGER;
    v_novo_codigo VARCHAR;
BEGIN
    -- Busca último número usado para o tipo e setor
    SELECT COALESCE(
        MAX(CAST(SUBSTRING(codigo FROM '[0-9]+$') AS INTEGER)),
        0
    ) INTO v_ultimo_numero
    FROM lista_mestra
    WHERE tipo = p_tipo AND setor = p_setor;

    -- Incrementa
    v_novo_numero := v_ultimo_numero + 1;

    -- Gera código no formato: TIPO.SETOR-NNN
    v_novo_codigo := p_tipo || '.' || p_setor || '-' || LPAD(v_novo_numero::TEXT, 3, '0');

    RETURN v_novo_codigo;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION gerar_proximo_codigo IS 'Gera próximo código sequencial para Lista Mestra';

-- Exemplo de uso:
-- SELECT gerar_proximo_codigo('POP', 'OPERACOES'); -- Retorna: POP.OPERACOES-001

-- ============================================================================
-- 10. CRIAR TRIGGERS: Updated_at automático
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para lista_mestra
DROP TRIGGER IF EXISTS trigger_lista_mestra_updated_at ON lista_mestra;
CREATE TRIGGER trigger_lista_mestra_updated_at
    BEFORE UPDATE ON lista_mestra
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger para blocos_assinatura
DROP TRIGGER IF EXISTS trigger_blocos_assinatura_updated_at ON blocos_assinatura;
CREATE TRIGGER trigger_blocos_assinatura_updated_at
    BEFORE UPDATE ON blocos_assinatura
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger para itens_bloco_assinatura
DROP TRIGGER IF EXISTS trigger_itens_bloco_updated_at ON itens_bloco_assinatura;
CREATE TRIGGER trigger_itens_bloco_updated_at
    BEFORE UPDATE ON itens_bloco_assinatura
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger para validacoes_ugq
DROP TRIGGER IF EXISTS trigger_validacoes_ugq_updated_at ON validacoes_ugq;
CREATE TRIGGER trigger_validacoes_ugq_updated_at
    BEFORE UPDATE ON validacoes_ugq
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- FIM DA MIGRATION
-- ============================================================================

COMMIT;

-- Verificação
SELECT 'Migration add_workflow_ugq.sql aplicada com sucesso!' as status;
SELECT 'Tabelas criadas: lista_mestra, blocos_assinatura, itens_bloco_assinatura, validacoes_ugq' as info;
