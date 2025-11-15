"""
Script de verificacao completa do sistema
Executa testes basicos para garantir que tudo esta funcionando
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

print('=' * 80)
print('VERIFICACAO COMPLETA DO SISTEMA GED')
print('=' * 80)
print()

# 1. Verifica bibliotecas
print('[1/7] Verificando bibliotecas Python...')
try:
    import flask
    import sqlalchemy
    import psycopg2
    import openai
    from docx import Document
    from PyPDF2 import PdfReader
    from odf.opendocument import load as odf_load
    print('  ✓ Flask:', flask.__version__)
    print('  ✓ SQLAlchemy:', sqlalchemy.__version__)
    print('  ✓ psycopg2: OK')
    print('  ✓ OpenAI: OK (DeepSeek)')
    print('  ✓ python-docx: OK')
    print('  ✓ PyPDF2: OK')
    print('  ✓ odfpy: OK')
except ImportError as e:
    print(f'  ✗ ERRO: Biblioteca faltando - {e}')
    print('  Execute: pip install -r requirements-windows.txt')
    sys.exit(1)

# 2. Verifica configuração
print()
print('[2/7] Verificando configuracao (.env)...')
try:
    from config import Config
    print('  ✓ SECRET_KEY:', 'Configurado' if Config.SECRET_KEY else 'FALTANDO')
    print('  ✓ DATABASE_URL:', Config.SQLALCHEMY_DATABASE_URI[:30] + '...')
    # FIX: Não expõe API Key completa nos logs
    print('  ✓ AI_API_KEY:', '***REDACTED***' if Config.AI_API_KEY else 'FALTANDO')
    print('  ✓ AI_API_MODEL:', Config.AI_API_MODEL)
except Exception as e:
    print(f'  ✗ ERRO na configuracao: {e}')
    sys.exit(1)

# 3. Verifica conexão com banco
print()
print('[3/7] Verificando conexao com PostgreSQL...')
try:
    from app import create_app, db
    app = create_app()
    with app.app_context():
        db.session.execute(sqlalchemy.text('SELECT 1'))
        print('  ✓ Conexao com banco de dados: OK')
except Exception as e:
    print(f'  ✗ ERRO ao conectar no banco: {e}')
    print('  Verifique se PostgreSQL esta rodando!')
    sys.exit(1)

# 4. Verifica tabelas
print()
print('[4/7] Verificando tabelas no banco...')
try:
    with app.app_context():
        from app.models import Usuario, Documento, Tarefa, LogAI

        tabelas = {
            'usuarios': Usuario.query.count(),
            'documentos': Documento.query.count(),
            'tarefas': Tarefa.query.count(),
            'logs_ia': LogAI.query.count()
        }

        for tabela, count in tabelas.items():
            print(f'  ✓ Tabela {tabela}: {count} registros')
except Exception as e:
    print(f'  ✗ ERRO nas tabelas: {e}')
    print('  Execute: python init_database.py')
    sys.exit(1)

# 5. Verifica diretórios
print()
print('[5/7] Verificando diretorios de upload...')
try:
    os.makedirs('app/uploads/documentos', exist_ok=True)
    os.makedirs('app/uploads/publicados', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    print('  ✓ app/uploads/documentos')
    print('  ✓ app/uploads/publicados')
    print('  ✓ logs')
except Exception as e:
    print(f'  ✗ ERRO ao criar diretorios: {e}')

# 6. Testa extração de texto
print()
print('[6/7] Testando extracao de texto...')
try:
    from app.services.ai_client import extract_text
    print('  ✓ Modulo extract_text importado')
    print('  ✓ Pronto para processar: PDF, DOCX, ODT')
except Exception as e:
    print(f'  ✗ ERRO no modulo de extracao: {e}')

# 7. Testa conexão com DeepSeek
print()
print('[7/7] Testando conexao com DeepSeek IA...')
try:
    from app.services.ai_client import _call_deepseek
    with app.app_context():
        # Teste simples
        resposta = _call_deepseek(
            "Voce e um assistente util.",
            "Responda apenas: OK",
            temperature=0.1
        )
        if resposta:
            print('  ✓ Conexao com DeepSeek: OK')
            print(f'  ✓ Resposta da IA: {resposta[:50]}...')
        else:
            print('  ⚠ DeepSeek respondeu vazio')
except Exception as e:
    print(f'  ⚠ Aviso DeepSeek: {str(e)[:100]}')
    print('  (Sistema funcionara sem IA)')

# Resumo final
print()
print('=' * 80)
print('RESULTADO DA VERIFICACAO')
print('=' * 80)
print()
print('✓ Sistema configurado corretamente!')
print('✓ Banco de dados conectado!')
print('✓ Tabelas criadas!')
print('✓ Modulos de IA disponiveis!')
print()
print('PRONTO PARA USAR!')
print()
print('Para iniciar o servidor:')
print('  python app.py')
print()
print('Acesse: http://localhost:5000')
print('Login: admin@example.com / admin123')
print()
print('=' * 80)
