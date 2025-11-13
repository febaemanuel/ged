"""
Ponto de entrada principal da aplicação Sistema GED

Execute com:
    flask run
ou:
    python app.py
"""

import os
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
    """Popula o banco com dados iniciais"""
    from app.models import Usuario
    from datetime import datetime

    # Cria usuário administrador padrão
    admin = Usuario.query.filter_by(email='admin@example.com').first()
    if not admin:
        admin = Usuario(
            nome='Administrador',
            email='admin@example.com',
            perfil='administrador',
            ativo=True
        )
        admin.set_password('admin123')
        db.session.add(admin)

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
        gerente.set_password('gerente123')
        db.session.add(gerente)

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
        usuario.set_password('usuario123')
        db.session.add(usuario)

    db.session.commit()
    print('Dados iniciais criados com sucesso!')
    print('')
    print('Usuários criados:')
    print('  Admin:   admin@example.com    / admin123')
    print('  Gerente: gerente@example.com  / gerente123')
    print('  Usuário: usuario@example.com  / usuario123')


@app.cli.command()
def verificar_vencimentos():
    """Verifica e atualiza documentos vencidos"""
    from app.models import Documento
    from datetime import datetime

    agora = datetime.utcnow()

    documentos_vencidos = Documento.query.filter(
        Documento.data_vencimento != None,
        Documento.data_vencimento < agora,
        Documento.status == 'Aprovado e Publicado'
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
