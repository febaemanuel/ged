-- Migração: Adiciona campos da Evolution API
-- Data: 2025-11-20
-- Descrição: Adiciona campos evolution_api_url, evolution_instance_name, evolution_api_key
--            mantendo campos antigos do Twilio para compatibilidade

-- Adiciona colunas da Evolution API
ALTER TABLE configuracao_whatsapp
ADD COLUMN IF NOT EXISTS evolution_api_url VARCHAR(200),
ADD COLUMN IF NOT EXISTS evolution_instance_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS evolution_api_key VARCHAR(200);

-- Comentários para documentação
COMMENT ON COLUMN configuracao_whatsapp.evolution_api_url IS 'URL base da Evolution API (ex: https://api.evolution.com)';
COMMENT ON COLUMN configuracao_whatsapp.evolution_instance_name IS 'Nome da instância no Evolution API (ex: minha_instancia)';
COMMENT ON COLUMN configuracao_whatsapp.evolution_api_key IS 'API Key para autenticação na Evolution API';

-- Marca campos Twilio como deprecated (apenas documentação)
COMMENT ON COLUMN configuracao_whatsapp.twilio_account_sid IS 'DEPRECATED - Usar Evolution API. Account SID do Twilio';
COMMENT ON COLUMN configuracao_whatsapp.twilio_auth_token IS 'DEPRECATED - Usar Evolution API. Auth Token do Twilio';
COMMENT ON COLUMN configuracao_whatsapp.twilio_whatsapp_number IS 'DEPRECATED - Usar Evolution API. Número WhatsApp do Twilio';
