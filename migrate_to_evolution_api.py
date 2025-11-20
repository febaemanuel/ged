#!/usr/bin/env python3
"""
Script de migração para Evolution API

Adiciona campos necessários para Evolution API na tabela configuracao_whatsapp
Mantém compatibilidade com Twilio
"""

import os
import sys
from sqlalchemy import create_engine, text

# Adiciona o diretório ao path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config import Config

def migrate():
    """Executa migração"""
    print("=" * 60)
    print("MIGRAÇÃO: Twilio → Evolution API")
    print("=" * 60)
    print()

    # Cria engine
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

    print("Conectando ao banco de dados...")
    print(f"Database: {Config.SQLALCHEMY_DATABASE_URI.split('@')[1] if '@' in Config.SQLALCHEMY_DATABASE_URI else 'N/A'}")
    print()

    with engine.connect() as conn:
        # Verifica se as colunas já existem
        check_sql = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'configuracao_whatsapp'
        AND column_name IN ('evolution_api_url', 'evolution_instance_name', 'evolution_api_key');
        """

        result = conn.execute(text(check_sql))
        existing_columns = [row[0] for row in result]

        if len(existing_columns) == 3:
            print("✓ Colunas da Evolution API já existem!")
            print("  - evolution_api_url")
            print("  - evolution_instance_name")
            print("  - evolution_api_key")
            print()
            print("Nenhuma ação necessária.")
            return

        print("Adicionando colunas da Evolution API...")

        # Adiciona colunas
        migration_sql = """
        ALTER TABLE configuracao_whatsapp
        ADD COLUMN IF NOT EXISTS evolution_api_url VARCHAR(200),
        ADD COLUMN IF NOT EXISTS evolution_instance_name VARCHAR(100),
        ADD COLUMN IF NOT EXISTS evolution_api_key VARCHAR(200);
        """

        conn.execute(text(migration_sql))
        conn.commit()

        print("✓ Colunas adicionadas com sucesso!")
        print("  - evolution_api_url VARCHAR(200)")
        print("  - evolution_instance_name VARCHAR(100)")
        print("  - evolution_api_key VARCHAR(200)")
        print()

        # Verifica se registro de configuração existe
        check_config = "SELECT COUNT(*) FROM configuracao_whatsapp;"
        result = conn.execute(text(check_config))
        count = result.fetchone()[0]

        if count == 0:
            print("⚠ Nenhuma configuração encontrada.")
            print("  Execute o sistema para criar a configuração padrão.")
        else:
            print(f"✓ Configuração existente encontrada ({count} registro)")

        print()
        print("=" * 60)
        print("MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print()
        print("Próximos passos:")
        print("1. Configure a Evolution API em /admin/whatsapp")
        print("2. Insira URL da API, nome da instância e API Key")
        print("3. Conecte o WhatsApp usando QR Code")
        print("4. Teste o envio de mensagens")
        print()


if __name__ == '__main__':
    try:
        migrate()
    except Exception as e:
        print()
        print("❌ ERRO NA MIGRAÇÃO:")
        print(f"   {str(e)}")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)
