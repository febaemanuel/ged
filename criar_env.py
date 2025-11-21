#!/usr/bin/env python3
"""
Script para Criar/Atualizar Arquivo .env
=========================================

Este script gera uma SECRET_KEY segura e cria/atualiza o arquivo .env
com base no .env.example.

Uso:
    python3 criar_env.py
"""

import os
import secrets
import shutil
from pathlib import Path


def gerar_secret_key():
    """Gera uma SECRET_KEY segura de 64 caracteres hexadecimais"""
    return secrets.token_hex(32)


def criar_env():
    """Cria arquivo .env baseado no .env.example"""

    # Diretórios
    base_dir = Path(__file__).parent
    env_example = base_dir / '.env.example'
    env_file = base_dir / '.env'

    print("=" * 80)
    print("CRIANDO ARQUIVO .env")
    print("=" * 80)
    print()

    # Verifica se .env.example existe
    if not env_example.exists():
        print("❌ Erro: Arquivo .env.example não encontrado!")
        return False

    # Verifica se .env já existe
    if env_file.exists():
        resposta = input("⚠️  Arquivo .env já existe. Deseja sobrescrever? (s/N): ").strip().lower()
        if resposta not in ['s', 'sim', 'y', 'yes']:
            print("❌ Operação cancelada")
            return False

        # Faz backup
        backup_file = base_dir / '.env.backup'
        shutil.copy(env_file, backup_file)
        print(f"✓ Backup criado: {backup_file}")

    # Lê .env.example
    print(f"✓ Lendo {env_example}")
    with open(env_example, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Gera SECRET_KEY
    secret_key = gerar_secret_key()
    print(f"✓ SECRET_KEY gerada: {secret_key[:16]}...{secret_key[-8:]}")

    # Substitui SECRET_KEY
    conteudo = conteudo.replace(
        'SECRET_KEY=your-secret-key-change-in-production',
        f'SECRET_KEY={secret_key}'
    )

    # Escreve .env
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(conteudo)

    print(f"✓ Arquivo .env criado: {env_file}")
    print()

    # Instruções
    print("=" * 80)
    print("PRÓXIMOS PASSOS")
    print("=" * 80)
    print()
    print("1. Edite o arquivo .env e configure:")
    print("   - DATABASE_URL (PostgreSQL)")
    print("   - AI_API_KEY (se for usar IA)")
    print("   - MAIL_USERNAME e MAIL_PASSWORD (se for usar e-mail)")
    print("   - EVOLUTION_API_URL, EVOLUTION_INSTANCE_NAME e EVOLUTION_API_KEY (WhatsApp)")
    print()
    print("2. Execute as migrações do banco de dados:")
    print("   python3 aplicar_migracao.py")
    print()
    print("3. Inicie a aplicação:")
    print("   python3 app.py")
    print()
    print("✅ Arquivo .env criado com sucesso!")
    print()

    return True


def criar_env_windows():
    """Cria arquivo .env no Windows (para o usuário que está vendo o erro)"""

    print("=" * 80)
    print("INSTRUÇÕES PARA WINDOWS")
    print("=" * 80)
    print()

    secret_key = gerar_secret_key()

    print("Execute os seguintes comandos no PowerShell ou CMD:")
    print()
    print("1. Copie o arquivo .env.example para .env:")
    print("   copy .env.example .env")
    print()
    print("2. Edite o arquivo .env e substitua a linha:")
    print("   SECRET_KEY=your-secret-key-change-in-production")
    print()
    print("   Por:")
    print(f"   SECRET_KEY={secret_key}")
    print()
    print("Ou use o comando direto (PowerShell):")
    print()
    print(f"   (Get-Content .env.example) -replace 'SECRET_KEY=your-secret-key-change-in-production', 'SECRET_KEY={secret_key}' | Set-Content .env")
    print()
    print("3. Edite o arquivo .env e configure outras variáveis (banco de dados, etc)")
    print()
    print("4. Execute as migrações:")
    print("   python aplicar_migracao.py")
    print()
    print("5. Inicie a aplicação:")
    print("   python app.py")
    print()


if __name__ == '__main__':
    import sys

    # Detecta sistema operacional
    if sys.platform == 'win32':
        print()
        print("🪟 Sistema Windows detectado")
        print()
        criar_env_windows()
    else:
        print()
        print("🐧 Sistema Linux/Mac detectado")
        print()
        sucesso = criar_env()
        sys.exit(0 if sucesso else 1)
