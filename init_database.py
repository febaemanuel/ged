"""
Script para inicializar o banco de dados do Sistema GED
Cria todas as tabelas e usuarios padrao
"""

from app import create_app, db
from app.models import Usuario

print('========================================')
print('Inicializando Banco de Dados GED')
print('========================================')
print()

# Cria a aplicacao
app = create_app()

with app.app_context():
    # Cria todas as tabelas
    print('Criando tabelas...')
    db.create_all()
    print('[OK] Tabelas criadas com sucesso!')
    print()

    # Verifica se ja existem usuarios
    if Usuario.query.count() > 0:
        print('[AVISO] Banco ja possui usuarios. Pulando criacao.')
        print()
    else:
        print('Criando usuarios padrao...')

        # Admin
        admin = Usuario(
            nome='Administrador',
            email='admin@example.com',
            perfil='administrador',
            ativo=True
        )
        admin.set_password('admin123')
        db.session.add(admin)

        # Gerente
        gerente = Usuario(
            nome='Gerente Exemplo',
            email='gerente@example.com',
            perfil='gerente',
            setor='Qualidade',
            ativo=True
        )
        gerente.set_password('gerente123')
        db.session.add(gerente)

        # Usuario comum
        usuario = Usuario(
            nome='Usuario Exemplo',
            email='usuario@example.com',
            perfil='comum',
            setor='Operacoes',
            ativo=True
        )
        usuario.set_password('usuario123')
        db.session.add(usuario)

        db.session.commit()
        print('[OK] Usuarios criados com sucesso!')
        print()

    print('========================================')
    print('Banco de dados inicializado!')
    print('========================================')
    print()
    print('Usuarios disponiveis:')
    print('  Admin:   admin@example.com / admin123')
    print('  Gerente: gerente@example.com / gerente123')
    print('  Usuario: usuario@example.com / usuario123')
    print()
    print('Acesse: http://localhost:5000')
    print('========================================')
