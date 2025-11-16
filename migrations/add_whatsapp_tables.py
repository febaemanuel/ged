#!/usr/bin/env python3
"""
Migration: Adiciona tabelas do WhatsApp

Cria as seguintes tabelas:
- configuracao_whatsapp: Configurações globais do WhatsApp
- conversacoes_whatsapp: Estado de conversas ativas
- logs_whatsapp: Logs de mensagens enviadas/recebidas

Execução:
    python migrations/add_whatsapp_tables.py
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.models import db, ConfiguracaoWhatsApp

print("=" * 60)
print("MIGRATION: Criar Tabelas WhatsApp")
print("=" * 60)

app = create_app()

with app.app_context():
    print("\n1. Criando tabelas WhatsApp...")

    # Cria as tabelas
    try:
        # Importa os modelos para garantir que estão registrados
        from app.models import ConfiguracaoWhatsApp, ConversacaoWhatsApp, LogWhatsApp

        # Cria apenas as tabelas WhatsApp
        db.create_all()

        print("   ✅ Tabelas criadas com sucesso!")

    except Exception as e:
        print(f"   ❌ Erro ao criar tabelas: {e}")
        sys.exit(1)

    print("\n2. Verificando se configuração existe...")

    # Cria configuração padrão se não existir
    config = ConfiguracaoWhatsApp.query.first()

    if not config:
        print("   📝 Criando configuração padrão...")

        config = ConfiguracaoWhatsApp(
            ativo=False,
            usar_para_notificacoes=True,
            usar_para_assinaturas=True,
            usar_para_lembretes=True,
            metodo_confirmacao='ambos',
            exigir_2fa=False,
            timeout_sessao_minutos=15,
            deletar_mensagens_sensiveis=True,
            horario_inicio='08:00',
            horario_fim='18:00',
            dias_semana='1,2,3,4,5'  # Segunda a Sexta
        )

        db.session.add(config)
        db.session.commit()

        print(f"   ✅ Configuração criada com ID: {config.id}")
    else:
        print(f"   ℹ️  Configuração já existe (ID: {config.id})")

    print("\n3. Verificando tabelas criadas...")

    from sqlalchemy import inspect
    inspector = inspect(db.engine)

    tabelas_esperadas = [
        'configuracao_whatsapp',
        'conversacoes_whatsapp',
        'logs_whatsapp'
    ]

    tabelas_existentes = inspector.get_table_names()

    for tabela in tabelas_esperadas:
        if tabela in tabelas_existentes:
            colunas = [col['name'] for col in inspector.get_columns(tabela)]
            print(f"   ✅ {tabela} ({len(colunas)} colunas)")
        else:
            print(f"   ❌ {tabela} NÃO EXISTE!")

    print("\n" + "=" * 60)
    print("MIGRATION CONCLUÍDA!")
    print("=" * 60)
    print("\nPróximos passos:")
    print("1. Acesse: http://localhost:5000/admin/whatsapp")
    print("2. Configure as credenciais do Twilio")
    print("3. Marque 'WhatsApp ATIVADO'")
    print("4. Salve as configurações")
    print("\n" + "=" * 60)
