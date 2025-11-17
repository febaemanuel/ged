#!/usr/bin/env python3
"""
Script de Verificação do Sistema WhatsApp
==========================================

Este script verifica o estado do sistema WhatsApp, incluindo:
- Conexão com banco de dados
- Tabelas do WhatsApp (configuracao_whatsapp, conversacoes_whatsapp, logs_whatsapp)
- Estado atual da configuração
- Credenciais Twilio
- Estatísticas de uso

Uso:
    python3 verificar_whatsapp.py
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verificar_whatsapp():
    """Verifica o sistema WhatsApp"""
    print("=" * 80)
    print("VERIFICAÇÃO DO SISTEMA WHATSAPP")
    print("=" * 80)
    print()

    try:
        # 1. Importar módulos
        print("[1/6] Importando módulos...")
        from app import create_app, db
        from app.models import ConfiguracaoWhatsApp, ConversacaoWhatsApp, LogWhatsApp, Usuario
        from sqlalchemy import inspect
        print("✓ Módulos importados com sucesso")
        print()

        # 2. Criar contexto da aplicação
        print("[2/6] Criando contexto da aplicação...")
        app = create_app()
        app.app_context().push()
        print(f"✓ Aplicação criada: {app.name}")
        print(f"  Banco de dados: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[1] if '@' in app.config['SQLALCHEMY_DATABASE_URI'] else 'N/A'}")
        print()

        # 3. Verificar conexão com banco de dados
        print("[3/6] Verificando conexão com banco de dados...")
        try:
            db.session.execute(db.text('SELECT 1'))
            print("✓ Conexão com PostgreSQL estabelecida")
        except Exception as e:
            print(f"✗ Erro ao conectar ao banco de dados: {str(e)}")
            print("\nDICA: Certifique-se de que o PostgreSQL está rodando:")
            print("  sudo service postgresql start")
            return False
        print()

        # 4. Verificar existência das tabelas
        print("[4/6] Verificando tabelas do WhatsApp...")
        inspector = inspect(db.engine)
        tabelas_necessarias = ['configuracao_whatsapp', 'conversacoes_whatsapp', 'logs_whatsapp']
        tabelas_existentes = inspector.get_table_names()

        for tabela in tabelas_necessarias:
            if tabela in tabelas_existentes:
                colunas = inspector.get_columns(tabela)
                print(f"✓ Tabela '{tabela}' existe ({len(colunas)} colunas)")
            else:
                print(f"✗ Tabela '{tabela}' NÃO EXISTE!")
                print("\nDICA: Execute a migração do banco de dados:")
                print("  python3 aplicar_migracao.py")
                return False
        print()

        # 5. Verificar configuração do WhatsApp
        print("[5/6] Verificando configuração do WhatsApp...")
        config = ConfiguracaoWhatsApp.get_config()

        print(f"  ID: {config.id}")
        print(f"  Status: {'🟢 ATIVADO' if config.ativo else '🔴 DESATIVADO'}")
        print(f"  Twilio Account SID: {'✓ Configurado' if config.twilio_account_sid else '✗ Não configurado'}")
        print(f"  Twilio Auth Token: {'✓ Configurado' if config.twilio_auth_token else '✗ Não configurado'}")
        print(f"  Número WhatsApp: {config.twilio_whatsapp_number or '✗ Não configurado'}")
        print()
        print("  Funcionalidades:")
        print(f"    - Notificações: {'✓' if config.usar_para_notificacoes else '✗'}")
        print(f"    - Assinaturas: {'✓' if config.usar_para_assinaturas else '✗'}")
        print(f"    - Lembretes: {'✓' if config.usar_para_lembretes else '✗'}")
        print(f"  Método de confirmação: {config.metodo_confirmacao}")
        print()
        print("  Segurança:")
        print(f"    - 2FA: {'✓ Ativo' if config.exigir_2fa else '✗ Desativado'}")
        print(f"    - Timeout sessão: {config.timeout_sessao_minutos} minutos")
        print(f"    - Deletar mensagens sensíveis: {'✓' if config.deletar_mensagens_sensiveis else '✗'}")
        print()
        print("  Horário de funcionamento:")
        print(f"    - Horário: {config.horario_inicio} às {config.horario_fim}")
        print(f"    - Dias: {config.dias_semana}")
        print()

        if config.atualizado_por:
            print(f"  Última atualização: {config.atualizado_em}")
            print(f"  Atualizado por: {config.atualizado_por.nome}")
        print()

        # 6. Estatísticas de uso
        print("[6/6] Estatísticas de uso...")
        total_mensagens = LogWhatsApp.query.count()
        mensagens_enviadas = LogWhatsApp.query.filter_by(direcao='enviada').count()
        mensagens_recebidas = LogWhatsApp.query.filter_by(direcao='recebida').count()
        mensagens_falhas = LogWhatsApp.query.filter_by(status='falhou').count()
        conversacoes_ativas = ConversacaoWhatsApp.query.count()

        usuarios_whatsapp = Usuario.query.filter(
            Usuario.telefone.isnot(None),
            Usuario.whatsapp_ativo == True
        ).count()

        print(f"  Total de mensagens: {total_mensagens}")
        print(f"  Mensagens enviadas: {mensagens_enviadas}")
        print(f"  Mensagens recebidas: {mensagens_recebidas}")
        print(f"  Mensagens com falha: {mensagens_falhas}")
        print(f"  Conversas ativas: {conversacoes_ativas}")
        print(f"  Usuários com WhatsApp: {usuarios_whatsapp}")
        print()

        # Resumo final
        print("=" * 80)
        print("RESUMO DA VERIFICAÇÃO")
        print("=" * 80)

        if config.ativo and config.twilio_account_sid and config.twilio_auth_token and config.twilio_whatsapp_number:
            print("✓ Sistema WhatsApp está CONFIGURADO e ATIVO")
            print("\nPróximos passos:")
            print("  1. Testar envio de mensagem no painel /admin/whatsapp")
            print("  2. Configurar webhook no Twilio Console")
        elif config.ativo:
            print("⚠ Sistema WhatsApp está ATIVO mas FALTAM CREDENCIAIS")
            print("\nPróximos passos:")
            print("  1. Acesse /admin/whatsapp")
            print("  2. Configure as credenciais Twilio")
        else:
            print("⚠ Sistema WhatsApp está DESATIVADO")
            print("\nPróximos passos:")
            print("  1. Acesse /admin/whatsapp")
            print("  2. Configure as credenciais Twilio")
            print("  3. Ative o WhatsApp usando o botão de toggle")

        print("=" * 80)
        return True

    except ImportError as e:
        print(f"✗ Erro ao importar módulos: {str(e)}")
        print("\nDICA: Instale as dependências:")
        print("  pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"✗ Erro durante verificação: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    sucesso = verificar_whatsapp()
    sys.exit(0 if sucesso else 1)
