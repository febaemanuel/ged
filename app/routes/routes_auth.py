"""
Rotas de Autenticação do Sistema GED

Endpoints:
- POST /auth/login - Login do usuário
- POST /auth/logout - Logout do usuário
- POST /auth/register - Registro de novo usuário (admin apenas)
- GET /auth/me - Informações do usuário atual
- PUT /auth/change_password - Alterar senha
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime

from app.models import db, Usuario
from app.utils.validators import validar_senha_forte, validar_email

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['POST'])
def login():
    """
    Login do usuário

    JSON body:
        - email: Email do usuário
        - senha: Senha do usuário

    Returns:
        JSON com informações do usuário logado
    """
    data = request.get_json()

    email = data.get('email')
    senha = data.get('senha')

    if not email or not senha:
        return jsonify({'erro': 'Email e senha são obrigatórios'}), 400

    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario or not usuario.check_password(senha):
        return jsonify({'erro': 'Email ou senha inválidos'}), 401

    if not usuario.ativo:
        return jsonify({'erro': 'Usuário inativo'}), 401

    # Atualiza último acesso
    usuario.ultimo_acesso = datetime.utcnow()
    db.session.commit()

    # Login
    login_user(usuario)

    return jsonify({
        'mensagem': 'Login realizado com sucesso',
        'usuario': {
            'id': usuario.id,
            'nome': usuario.nome,
            'email': usuario.email,
            'perfil': usuario.perfil,
            'setor': usuario.setor
        }
    })


@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout do usuário"""
    logout_user()
    return jsonify({'mensagem': 'Logout realizado com sucesso'})


@bp.route('/register', methods=['POST'])
@login_required
def register():
    """
    Registra novo usuário
    Apenas administradores podem criar usuários

    JSON body:
        - nome: Nome completo
        - email: Email (único)
        - senha: Senha
        - perfil: comum, gerente, responsavel_interno, administrador
        - setor: Setor do usuário (opcional)
    """
    if not current_user.is_admin():
        return jsonify({'erro': 'Apenas administradores podem criar usuários'}), 403

    data = request.get_json()

    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')
    perfil = data.get('perfil', 'comum')
    setor = data.get('setor')

    # Validações
    if not nome or not email or not senha:
        return jsonify({'erro': 'Nome, email e senha são obrigatórios'}), 400

    # Valida email
    email_valido, erro_email = validar_email(email)
    if not email_valido:
        return jsonify({'erro': erro_email}), 400

    # Valida senha
    senha_valida, erro_senha = validar_senha_forte(senha)
    if not senha_valida:
        return jsonify({'erro': erro_senha}), 400

    if perfil not in current_app.config['PERFIS_PERMITIDOS']:
        return jsonify({'erro': 'Perfil inválido'}), 400

    # Verifica se email já existe
    if Usuario.query.filter_by(email=email).first():
        return jsonify({'erro': 'Email já cadastrado'}), 400

    # Cria usuário
    usuario = Usuario(
        nome=nome,
        email=email,
        perfil=perfil,
        setor=setor,
        ativo=True
    )
    usuario.set_password(senha)

    db.session.add(usuario)
    db.session.commit()

    return jsonify({
        'mensagem': 'Usuário criado com sucesso',
        'usuario': {
            'id': usuario.id,
            'nome': usuario.nome,
            'email': usuario.email,
            'perfil': usuario.perfil
        }
    }), 201


@bp.route('/me', methods=['GET'])
@login_required
def me():
    """Retorna informações do usuário atual"""
    return jsonify({
        'usuario': {
            'id': current_user.id,
            'nome': current_user.nome,
            'email': current_user.email,
            'perfil': current_user.perfil,
            'setor': current_user.setor,
            'ativo': current_user.ativo,
            'data_criacao': current_user.data_criacao.isoformat(),
            'ultimo_acesso': current_user.ultimo_acesso.isoformat() if current_user.ultimo_acesso else None
        }
    })


@bp.route('/change_password', methods=['PUT'])
@login_required
def change_password():
    """
    Alterar senha do usuário

    JSON body:
        - senha_atual: Senha atual
        - senha_nova: Nova senha
    """
    data = request.get_json()

    senha_atual = data.get('senha_atual')
    senha_nova = data.get('senha_nova')

    if not senha_atual or not senha_nova:
        return jsonify({'erro': 'Senha atual e nova senha são obrigatórias'}), 400

    if not current_user.check_password(senha_atual):
        return jsonify({'erro': 'Senha atual incorreta'}), 401

    # Valida senha forte
    senha_valida, erro_senha = validar_senha_forte(senha_nova)
    if not senha_valida:
        return jsonify({'erro': erro_senha}), 400

    current_user.set_password(senha_nova)
    db.session.commit()

    return jsonify({'mensagem': 'Senha alterada com sucesso'})


@bp.route('/usuarios', methods=['GET'])
@login_required
def listar_usuarios():
    """
    Lista todos os usuários
    Apenas para gerentes e administradores
    """
    if not current_user.is_gerente_ou_superior():
        return jsonify({'erro': 'Sem permissão para listar usuários'}), 403

    usuarios = Usuario.query.order_by(Usuario.nome).all()

    return jsonify({
        'usuarios': [{
            'id': u.id,
            'nome': u.nome,
            'email': u.email,
            'perfil': u.perfil,
            'setor': u.setor,
            'ativo': u.ativo,
            'data_criacao': u.data_criacao.isoformat(),
            'ultimo_acesso': u.ultimo_acesso.isoformat() if u.ultimo_acesso else None
        } for u in usuarios]
    })


@bp.route('/usuarios/<int:id>', methods=['PUT'])
@login_required
def atualizar_usuario(id):
    """
    Atualiza informações do usuário
    Apenas administradores

    JSON body:
        - nome
        - perfil
        - setor
        - ativo
    """
    if not current_user.is_admin():
        return jsonify({'erro': 'Apenas administradores podem atualizar usuários'}), 403

    usuario = Usuario.query.get_or_404(id)

    data = request.get_json()

    if 'nome' in data:
        usuario.nome = data['nome']
    if 'perfil' in data and data['perfil'] in current_app.config['PERFIS_PERMITIDOS']:
        usuario.perfil = data['perfil']
    if 'setor' in data:
        usuario.setor = data['setor']
    if 'ativo' in data:
        usuario.ativo = bool(data['ativo'])

    db.session.commit()

    return jsonify({'mensagem': 'Usuário atualizado com sucesso'})


@bp.route('/usuarios/<int:id>', methods=['DELETE'])
@login_required
def deletar_usuario(id):
    """
    Deleta usuário
    Apenas administradores
    Não pode deletar a si mesmo
    """
    if not current_user.is_admin():
        return jsonify({'erro': 'Apenas administradores podem deletar usuários'}), 403

    if id == current_user.id:
        return jsonify({'erro': 'Não é possível deletar seu próprio usuário'}), 400

    usuario = Usuario.query.get_or_404(id)

    # Verifica se usuário tem documentos ou tarefas
    if usuario.documentos_criados.count() > 0:
        return jsonify({'erro': 'Usuário possui documentos criados. Não é possível deletar'}), 400

    if usuario.tarefas_atribuidas.count() > 0:
        return jsonify({'erro': 'Usuário possui tarefas atribuídas. Não é possível deletar'}), 400

    db.session.delete(usuario)
    db.session.commit()

    return jsonify({'mensagem': 'Usuário deletado com sucesso'})
