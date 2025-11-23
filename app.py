"""
Ponto de entrada principal da aplicação Sistema GED

Execute com:
    flask run
ou:
    python app.py
"""

import os
import sys

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

from app import create_app
from app.models import db

# Cria aplicação
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)


@app.shell_context_processor
def make_shell_context():
    """Adiciona objetos ao shell do Flask"""
    from app.models import Usuario, Documento, Tarefa, LogAI

    return {
        'db': db,
        'Usuario': Usuario,
        'Documento': Documento,
        'Tarefa': Tarefa,
        'LogAI': LogAI
    }


@app.cli.command()
def init_db():
    """Inicializa o banco de dados"""
    db.create_all()
    print('Banco de dados inicializado com sucesso!')


@app.cli.command()
def seed_db():
    """Popula o banco com dados iniciais - SENHAS FORTES GERADAS"""
    from app.models import Usuario
    from datetime import datetime
    import secrets

    print('🔐 Gerando senhas fortes aleatórias...')
    print('')

    # Gera senhas fortes aleatórias (16 caracteres URL-safe)
    senha_admin = secrets.token_urlsafe(16)
    senha_gerente = secrets.token_urlsafe(16)
    senha_usuario = secrets.token_urlsafe(16)

    # Cria usuário administrador padrão
    admin = Usuario.query.filter_by(email='admin@example.com').first()
    if not admin:
        admin = Usuario(
            nome='Administrador',
            email='admin@example.com',
            perfil='administrador',
            ativo=True
        )
        admin.set_password(senha_admin)
        db.session.add(admin)
        print('✅ Administrador criado')
    else:
        print('ℹ️  Administrador já existe')

    # Cria usuário gerente de exemplo
    gerente = Usuario.query.filter_by(email='gerente@example.com').first()
    if not gerente:
        gerente = Usuario(
            nome='Gerente Exemplo',
            email='gerente@example.com',
            perfil='gerente',
            setor='Qualidade',
            ativo=True
        )
        gerente.set_password(senha_gerente)
        db.session.add(gerente)
        print('✅ Gerente criado')
    else:
        print('ℹ️  Gerente já existe')

    # Cria usuário comum de exemplo
    usuario = Usuario.query.filter_by(email='usuario@example.com').first()
    if not usuario:
        usuario = Usuario(
            nome='Usuário Exemplo',
            email='usuario@example.com',
            perfil='comum',
            setor='Operações',
            ativo=True
        )
        usuario.set_password(senha_usuario)
        db.session.add(usuario)
        print('✅ Usuário comum criado')
    else:
        print('ℹ️  Usuário comum já existe')

    db.session.commit()

    print('')
    print('=' * 80)
    print('⚠️  SENHAS GERADAS - GUARDE EM LOCAL SEGURO! ⚠️')
    print('=' * 80)
    print(f'  Admin:   admin@example.com    / {senha_admin}')
    print(f'  Gerente: gerente@example.com  / {senha_gerente}')
    print(f'  Usuário: usuario@example.com  / {senha_usuario}')
    print('=' * 80)
    print('⚠️  Estas senhas NÃO serão exibidas novamente!')
    print('💡 IMPORTANTE: Altere todas as senhas no primeiro login!')
    print('🔒 Em produção, DELETE estes usuários de teste!')
    print('=' * 80)


@app.cli.command()
def verificar_vencimentos():
    """Verifica e atualiza documentos vencidos"""
    from app.models import Documento
    from datetime import datetime

    agora = datetime.utcnow()

    documentos_vencidos = Documento.query.filter(
        Documento.data_vencimento != None,
        Documento.data_vencimento < agora,
        Documento.status == 'Publicado'
    ).all()

    total_atualizados = 0
    for doc in documentos_vencidos:
        doc.status = 'Obsoleto'
        total_atualizados += 1

    db.session.commit()
    print(f'{total_atualizados} documentos marcados como Obsoletos')


if __name__ == '__main__':
    # Cria diretórios necessários
    os.makedirs('app/uploads/documentos', exist_ok=True)
    os.makedirs('app/uploads/publicados', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    # Executa aplicação
    app.run(debug=True, host='0.0.0.0', port=5000)
