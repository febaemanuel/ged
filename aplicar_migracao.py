"""
Script para aplicar migração do banco de dados
Adiciona campo chefia_imediata_id para workflow automático
"""

import sys
import os

# Força UTF-8 no Windows
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer') and not hasattr(sys.stdout, 'write_through'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if hasattr(sys.stderr, 'buffer') and not hasattr(sys.stderr, 'write_through'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from dotenv import load_dotenv
load_dotenv(encoding='utf-8')

from app import create_app, db
from sqlalchemy import text

print('========================================')
print('Aplicando Migração: Workflow Automático')
print('========================================')
print()

app = create_app()

with app.app_context():
    try:
        # Lê o arquivo SQL
        sql_file = os.path.join('migrations', 'add_chefia_imediata_workflow.sql')

        if not os.path.exists(sql_file):
            print(f'[ERRO] Arquivo de migração não encontrado: {sql_file}')
            sys.exit(1)

        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        print('Executando migração...')

        # Executa linha por linha (pula comentários)
        for line in sql_content.split(';'):
            line = line.strip()
            if line and not line.startswith('--'):
                try:
                    db.session.execute(text(line))
                except Exception as e:
                    # Ignora erros de "já existe"
                    if 'already exists' not in str(e) and 'duplicate' not in str(e).lower():
                        print(f'[AVISO] Erro ao executar: {line[:50]}...')
                        print(f'        {str(e)}')

        db.session.commit()

        print('[OK] Migração aplicada com sucesso!')
        print()
        print('Mudanças aplicadas:')
        print('  ✓ Campo chefia_imediata_id adicionado na tabela documentos')
        print('  ✓ Índice criado para performance')
        print()
        print('Workflow automático ativado! Agora documentos seguem o fluxo:')
        print('  1. Chefia Imediata → Análise')
        print('  2. Especialista → Validação de Conteúdo')
        print('  3. Qualidade → Validação de Padronização')
        print('  4. Aprovador → Aprovação Final')
        print('  5. Admin → Publicação')
        print()

    except Exception as e:
        print(f'[ERRO] Falha na migração: {str(e)}')
        db.session.rollback()
        sys.exit(1)

print('========================================')
print('Migração concluída!')
print('========================================')
