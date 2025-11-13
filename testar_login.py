"""
Script para testar login via API
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
import json

print('========================================')
print('Teste de Login - Simulacao API')
print('========================================')
print()

app = create_app()

# Simula requisicao de login
with app.test_client() as client:
    with app.app_context():
        print('Testando login com credenciais corretas:')
        print('-' * 80)

        # Teste 1: Admin
        print('1. Login como ADMIN (admin@example.com / admin123)')
        response = client.post('/auth/login',
                              json={'email': 'admin@example.com', 'senha': 'admin123'},
                              content_type='application/json')

        print(f'   Status Code: {response.status_code}')
        print(f'   Response: {response.get_json()}')
        print()

        # Teste 2: Gerente
        print('2. Login como GERENTE (gerente@example.com / gerente123)')
        response = client.post('/auth/login',
                              json={'email': 'gerente@example.com', 'senha': 'gerente123'},
                              content_type='application/json')

        print(f'   Status Code: {response.status_code}')
        print(f'   Response: {response.get_json()}')
        print()

        # Teste 3: Usuario
        print('3. Login como USUARIO (usuario@example.com / usuario123)')
        response = client.post('/auth/login',
                              json={'email': 'usuario@example.com', 'senha': 'usuario123'},
                              content_type='application/json')

        print(f'   Status Code: {response.status_code}')
        print(f'   Response: {response.get_json()}')
        print()

        print('-' * 80)
        print()
        print('Testando login com senha INCORRETA:')
        print('-' * 80)

        # Teste 4: Senha errada
        print('4. Login com senha errada')
        response = client.post('/auth/login',
                              json={'email': 'admin@example.com', 'senha': 'senha_errada'},
                              content_type='application/json')

        print(f'   Status Code: {response.status_code}')
        print(f'   Response: {response.get_json()}')
        print()

        print('-' * 80)

print()
print('========================================')
print('Teste concluido!')
print('========================================')
