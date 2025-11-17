#!/usr/bin/env python3
"""
Script para corrigir configuração do WhatsApp Sender ID
========================================================

Este script corrige o campo twilio_whatsapp_number que está com valor inválido "wh"
e permite configurar o número correto do WhatsApp.

Uso:
    python3 fix_whatsapp_sender.py [numero_whatsapp]

Exemplos:
    python3 fix_whatsapp_sender.py +14155238886  (Twilio Sandbox)
    python3 fix_whatsapp_sender.py +5585999999999  (Número real)
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_whatsapp_sender(numero=None):
    """Corrige o número do WhatsApp na configuração"""
    print("=" * 80)
    print("CORREÇÃO DO WHATSAPP SENDER ID")
    print("=" * 80)
    print()

    try:
        # Importa módulos necessários
        print("[1/4] Importando módulos...")
        from dotenv import load_dotenv
        load_dotenv()

        from app import create_app, db
        from app.models import ConfiguracaoWhatsApp
        from sqlalchemy import text
        print("✓ Módulos importados com sucesso")
        print()

        # Cria contexto da aplicação
        print("[2/4] Criando contexto da aplicação...")
        app = create_app()
        app.app_context().push()
        print("✓ Aplicação criada")
        print()

        # Verifica configuração atual
        print("[3/4] Verificando configuração atual...")
        config = ConfiguracaoWhatsApp.get_config()

        print(f"  ID: {config.id}")
        print(f"  Status: {'🟢 ATIVADO' if config.ativo else '🔴 DESATIVADO'}")
        print(f"  Account SID: {config.twilio_account_sid or 'Não configurado'}")
        print(f"  Auth Token: {'Configurado' if config.twilio_auth_token else 'Não configurado'}")
        print(f"  Número WhatsApp ATUAL: '{config.twilio_whatsapp_number}' ❌")
        print()

        # Valida número fornecido
        if numero:
            # Remove espaços
            numero = numero.strip()

            # Valida formato
            if not numero.startswith('+'):
                print(f"❌ ERRO: Número deve começar com '+' (código do país)")
                print(f"   Exemplo: +14155238886 ou +5585999999999")
                return False

            if len(numero) < 10:
                print(f"❌ ERRO: Número muito curto: {numero}")
                print(f"   Exemplo: +14155238886 ou +5585999999999")
                return False

            novo_numero = numero
        else:
            # Solicita número ao usuário
            print("Digite o número do WhatsApp (com código do país):")
            print("  Exemplos:")
            print("    +14155238886     (Twilio Sandbox)")
            print("    +5585999999999   (Número real do Brasil)")
            print()
            novo_numero = input("Número: ").strip()

            if not novo_numero:
                print("❌ Nenhum número fornecido. Operação cancelada.")
                return False

            if not novo_numero.startswith('+'):
                print(f"❌ ERRO: Número deve começar com '+' (código do país)")
                return False

        # Confirma mudança
        print()
        print(f"Você está prestes a alterar:")
        print(f"  DE: '{config.twilio_whatsapp_number}'")
        print(f"  PARA: '{novo_numero}'")
        print()

        if not numero:  # Se não foi passado como argumento, pede confirmação
            confirmacao = input("Confirma a alteração? (s/N): ").strip().lower()
            if confirmacao not in ['s', 'sim', 'y', 'yes']:
                print("❌ Operação cancelada pelo usuário.")
                return False

        # Aplica correção
        print()
        print("[4/4] Aplicando correção...")
        config.twilio_whatsapp_number = novo_numero
        db.session.commit()

        print(f"✓ Número do WhatsApp atualizado com sucesso!")
        print()

        # Verifica configuração final
        print("=" * 80)
        print("CONFIGURAÇÃO ATUALIZADA")
        print("=" * 80)
        config_updated = ConfiguracaoWhatsApp.get_config()
        print(f"  Account SID: {config_updated.twilio_account_sid or 'Não configurado'}")
        print(f"  Número WhatsApp: {config_updated.twilio_whatsapp_number} ✓")
        print(f"  Status: {'🟢 ATIVADO' if config_updated.ativo else '🔴 DESATIVADO'}")
        print()

        if not config_updated.twilio_account_sid or not config_updated.twilio_auth_token:
            print("⚠ ATENÇÃO: Ainda faltam credenciais Twilio!")
            print()
            print("Próximos passos:")
            print("  1. Acesse /admin/whatsapp no navegador")
            print("  2. Configure Account SID e Auth Token")
            print("  3. Ative o WhatsApp usando o toggle")
            print()
        else:
            print("✓ WhatsApp está configurado!")
            print()
            print("Próximos passos:")
            print("  1. Teste o envio em /admin/whatsapp")
            print("  2. Configure o webhook no Twilio Console")
            print("     URL: https://seu-dominio.com/whatsapp/webhook")
            print()

        print("=" * 80)
        return True

    except ImportError as e:
        print(f"✗ Erro ao importar módulos: {str(e)}")
        print()
        print("DICA: Instale as dependências:")
        print("  pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"✗ Erro durante correção: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Verifica se número foi passado como argumento
    numero = sys.argv[1] if len(sys.argv) > 1 else None

    sucesso = fix_whatsapp_sender(numero)
    sys.exit(0 if sucesso else 1)
