"""
Script para verificar usuarios no banco de dados
"""

import sys
import os

# Força UTF-8 no Windows
if sys.platform == 'win32':
    import codecs
    # Verifica se tem o atributo buffer antes de tentar modificar
    if hasattr(sys.stdout, 'buffer') and not hasattr(sys.stdout, 'write_through'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if hasattr(sys.stderr, 'buffer') and not hasattr(sys.stderr, 'write_through'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Carrega .env com encoding UTF-8
from dotenv import load_dotenv
load_dotenv(encoding='utf-8')

from app import create_app, db
from app.models import Usuario

print('========================================')
print('Verificacao de Usuarios no Banco')
print('========================================')
print()

app = create_app()

with app.app_context():
    # Busca todos os usuarios
    usuarios = Usuario.query.all()

    print(f'Total de usuarios no banco: {len(usuarios)}')
    print()

    if len(usuarios) == 0:
        print('[ERRO] Nenhum usuario encontrado no banco!')
        print('Execute: python init_database.py')
    else:
        print('Usuarios encontrados:')
        print('-' * 80)

        for u in usuarios:
            print(f'ID: {u.id}')
            print(f'Nome: {u.nome}')
            print(f'Email: {u.email}')
            print(f'Perfil: {u.perfil}')
            print(f'Ativo: {u.ativo}')
            print(f'Senha Hash: {u.senha_hash[:50]}...' if u.senha_hash else 'SEM SENHA!')
            print('-' * 80)

        print()
        print('Testando validacao de senhas:')
        print('-' * 80)

        # Testa senha do admin
        admin = Usuario.query.filter_by(email='admin@example.com').first()
        if admin:
            senha_correta = admin.check_password('admin123')
            senha_errada = admin.check_password('senha_errada')
            print(f'Admin - Senha "admin123": {"OK" if senha_correta else "FALHOU"}')
            print(f'Admin - Senha errada: {"ERRO - NAO DEVERIA PASSAR" if senha_errada else "OK"}')

        # Testa senha do gerente
        gerente = Usuario.query.filter_by(email='gerente@example.com').first()
        if gerente:
            senha_correta = gerente.check_password('gerente123')
            senha_errada = gerente.check_password('senha_errada')
            print(f'Gerente - Senha "gerente123": {"OK" if senha_correta else "FALHOU"}')
            print(f'Gerente - Senha errada: {"ERRO - NAO DEVERIA PASSAR" if senha_errada else "OK"}')

        # Testa senha do usuario
        usuario = Usuario.query.filter_by(email='usuario@example.com').first()
        if usuario:
            senha_correta = usuario.check_password('usuario123')
            senha_errada = usuario.check_password('senha_errada')
            print(f'Usuario - Senha "usuario123": {"OK" if senha_correta else "FALHOU"}')
            print(f'Usuario - Senha errada: {"ERRO - NAO DEVERIA PASSAR" if senha_errada else "OK"}')

        print('-' * 80)

print()
print('========================================')
print('Verificacao concluida!')
print('========================================')
