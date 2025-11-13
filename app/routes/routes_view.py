"""
Routes VIEW - Rotas para renderizar templates HTML
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os

from app import db
from app.models.models import Usuario, Documento, Tarefa, LogAI
from config import Config

view_bp = Blueprint('view', __name__)

# ============================================================================
# AUTENTICAÇÃO
# ============================================================================

@view_bp.route('/')
def index():
    """Página inicial - redireciona para login ou dashboard"""
    if current_user.is_authenticated:
        return redirect(url_for('view.dashboard'))
    return redirect(url_for('view.login'))


@view_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('view.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        lembrar = request.form.get('lembrar') == 'on'

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha_hash, senha):
            login_user(usuario, remember=lembrar)
            usuario.ultimo_acesso = datetime.utcnow()
            db.session.commit()

            flash('Login realizado com sucesso!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('view.dashboard'))
        else:
            flash('Email ou senha inválidos', 'danger')

    return render_template('login.html')


@view_bp.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    flash('Logout realizado com sucesso', 'info')
    return redirect(url_for('view.login'))


# ============================================================================
# DASHBOARD
# ============================================================================

@view_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal"""
    # Estatísticas
    stats = {
        'minhas_pendentes': Tarefa.query.filter_by(
            responsavel_id=current_user.id,
            concluida=False
        ).count(),
        'minhas_atrasadas': Tarefa.query.filter(
            Tarefa.responsavel_id == current_user.id,
            Tarefa.concluida == False,
            Tarefa.prazo < datetime.utcnow()
        ).count(),
        'minhas_concluidas_mes': Tarefa.query.filter(
            Tarefa.responsavel_id == current_user.id,
            Tarefa.concluida == True,
            Tarefa.data_conclusao >= datetime.utcnow() - timedelta(days=30)
        ).count(),
        'total_documentos': Documento.query.count()
    }

    # Minhas tarefas pendentes (últimas 10)
    tarefas = Tarefa.query.filter_by(
        responsavel_id=current_user.id,
        concluida=False
    ).order_by(Tarefa.prazo.asc()).limit(10).all()

    # Adicionar propriedade esta_atrasada para cada tarefa
    for tarefa in tarefas:
        tarefa.esta_atrasada = tarefa.prazo and tarefa.prazo < datetime.utcnow()

    return render_template('dashboard.html', stats=stats, tarefas=tarefas)


# ============================================================================
# DOCUMENTOS
# ============================================================================

@view_bp.route('/documentos')
@login_required
def documentos():
    """Lista de documentos"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Filtros
    query = Documento.query
    busca = request.args.get('q')
    status = request.args.get('status')
    tipo = request.args.get('tipo')
    setor = request.args.get('setor')

    if busca:
        query = query.filter(
            (Documento.titulo.ilike(f'%{busca}%')) |
            (Documento.codigo.ilike(f'%{busca}%'))
        )
    if status:
        query = query.filter_by(status=status)
    if tipo:
        query = query.filter_by(tipo_documento=tipo)
    if setor:
        query = query.filter_by(setor=setor)

    documentos = query.order_by(Documento.data_criacao.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('documentos.html', documentos=documentos)


@view_bp.route('/documento/<int:id>')
@login_required
def documento_detalhe(id):
    """Detalhes do documento"""
    documento = Documento.query.get_or_404(id)

    # Timeline de tarefas
    tarefas = Tarefa.query.filter_by(documento_id=id).order_by(
        Tarefa.data_criacao.desc()
    ).all()

    # Logs de IA
    logs_ia = LogAI.query.filter_by(documento_id=id).order_by(
        LogAI.data_hora.desc()
    ).limit(10).all()

    return render_template(
        'documento_detalhe.html',
        documento=documento,
        tarefas=tarefas,
        logs_ia=logs_ia
    )


@view_bp.route('/documento/criar', methods=['GET', 'POST'])
@login_required
def documento_criar():
    """Criar novo documento"""
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        tipo_documento = request.form.get('tipo_documento')
        setor = request.form.get('setor')
        descricao = request.form.get('descricao')
        validade_anos = request.form.get('validade_anos', type=int)

        # Upload do arquivo
        arquivo = request.files.get('arquivo')
        if not arquivo or arquivo.filename == '':
            flash('Arquivo é obrigatório', 'danger')
            return redirect(request.url)

        # Validar extensão
        extensao = arquivo.filename.rsplit('.', 1)[1].lower()
        if extensao not in Config.ALLOWED_EXTENSIONS_DOCUMENTO:
            flash(f'Extensão .{extensao} não permitida', 'danger')
            return redirect(request.url)

        # Salvar arquivo
        filename = secure_filename(arquivo.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_final = f"{timestamp}_{filename}"
        caminho_completo = os.path.join(Config.UPLOAD_FOLDER_DOCUMENTOS, filename_final)

        os.makedirs(Config.UPLOAD_FOLDER_DOCUMENTOS, exist_ok=True)
        arquivo.save(caminho_completo)

        # Criar documento
        documento = Documento(
            titulo=titulo,
            tipo_documento=tipo_documento,
            setor=setor,
            descricao=descricao,
            caminho_arquivo=caminho_completo,
            criador_id=current_user.id,
            responsavel_atual_id=current_user.id
        )

        # Calcular data de vencimento
        if validade_anos:
            documento.data_vencimento = datetime.utcnow() + timedelta(days=validade_anos * 365)

        db.session.add(documento)
        db.session.commit()

        flash(f'Documento {documento.codigo} criado com sucesso!', 'success')
        return redirect(url_for('view.documento_detalhe', id=documento.id))

    return render_template('documento_criar.html')


@view_bp.route('/documento/<int:id>/download')
@login_required
def documento_download(id):
    """Download do arquivo do documento"""
    documento = Documento.query.get_or_404(id)

    if not os.path.exists(documento.caminho_arquivo):
        flash('Arquivo não encontrado', 'danger')
        return redirect(url_for('view.documento_detalhe', id=id))

    return send_file(
        documento.caminho_arquivo,
        as_attachment=True,
        download_name=f"{documento.codigo}_{os.path.basename(documento.caminho_arquivo)}"
    )


# ============================================================================
# TAREFAS
# ============================================================================

@view_bp.route('/tarefas')
@login_required
def tarefas():
    """Lista de tarefas"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Filtros
    query = Tarefa.query
    tipo = request.args.get('tipo')
    status = request.args.get('status')
    prioridade = request.args.get('prioridade')
    atrasadas = request.args.get('atrasadas')

    # Se não for admin, mostrar apenas tarefas do usuário
    if not current_user.is_admin():
        query = query.filter(
            (Tarefa.responsavel_id == current_user.id) |
            (Tarefa.documento.has(criador_id=current_user.id))
        )

    if tipo:
        query = query.filter_by(tipo_tarefa=tipo)
    if status:
        # Converte status string para boolean concluida
        if status == 'pendente':
            query = query.filter_by(concluida=False)
        elif status == 'concluida':
            query = query.filter_by(concluida=True)
    if prioridade:
        query = query.filter_by(prioridade=prioridade)
    if atrasadas:
        query = query.filter(
            Tarefa.concluida == False,
            Tarefa.prazo < datetime.utcnow()
        )

    tarefas = query.order_by(Tarefa.prazo.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Adicionar propriedade esta_atrasada
    for tarefa in tarefas.items:
        tarefa.esta_atrasada = tarefa.prazo and tarefa.prazo < datetime.utcnow()

    # Estatísticas
    stats = {
        'pendentes': Tarefa.query.filter_by(
            responsavel_id=current_user.id,
            concluida=False
        ).count(),
        'atrasadas': Tarefa.query.filter(
            Tarefa.responsavel_id == current_user.id,
            Tarefa.concluida == False,
            Tarefa.prazo < datetime.utcnow()
        ).count(),
        'concluidas_mes': Tarefa.query.filter(
            Tarefa.responsavel_id == current_user.id,
            Tarefa.concluida == True,
            Tarefa.data_conclusao >= datetime.utcnow() - timedelta(days=30)
        ).count(),
        'total': Tarefa.query.filter_by(responsavel_id=current_user.id).count()
    }

    return render_template('tarefas.html', tarefas=tarefas, stats=stats)


@view_bp.route('/tarefa/<int:id>')
@login_required
def tarefa_detalhe(id):
    """Detalhes da tarefa"""
    tarefa = Tarefa.query.get_or_404(id)

    # Verificar permissão
    if not current_user.is_admin() and tarefa.responsavel_id != current_user.id:
        flash('Acesso negado', 'danger')
        return redirect(url_for('view.tarefas'))

    tarefa.esta_atrasada = tarefa.prazo and tarefa.prazo < datetime.utcnow()

    return render_template('tarefa_detalhe.html', tarefa=tarefa)


@view_bp.route('/tarefa/criar', methods=['GET', 'POST'])
@login_required
def tarefa_criar():
    """Criar nova tarefa"""
    if not current_user.is_gerente_ou_superior():
        flash('Apenas gerentes e administradores podem criar tarefas', 'danger')
        return redirect(url_for('view.tarefas'))

    if request.method == 'POST':
        documento_id = request.form.get('documento_id', type=int)
        tipo_tarefa = request.form.get('tipo_tarefa')
        responsavel_id = request.form.get('responsavel_id', type=int)
        descricao = request.form.get('descricao')
        prazo = request.form.get('prazo')
        prioridade = request.form.get('prioridade', 'normal')

        # Validações
        if not documento_id or not tipo_tarefa or not responsavel_id:
            flash('Preencha todos os campos obrigatórios', 'danger')
            return redirect(request.url)

        # Converter prazo
        prazo_dt = None
        if prazo:
            prazo_dt = datetime.strptime(prazo, '%Y-%m-%d')

        # Criar tarefa
        tarefa = Tarefa(
            documento_id=documento_id,
            tipo_tarefa=tipo_tarefa,
            responsavel_id=responsavel_id,
            descricao=descricao,
            prazo=prazo_dt,
            prioridade=prioridade,
            criador_id=current_user.id
        )

        db.session.add(tarefa)
        db.session.commit()

        flash('Tarefa criada com sucesso!', 'success')
        return redirect(url_for('view.tarefa_detalhe', id=tarefa.id))

    # Listar documentos e usuários para o formulário
    documentos = Documento.query.filter(
        Documento.status.in_(['rascunho', 'revisao', 'aprovado'])
    ).order_by(Documento.data_criacao.desc()).all()

    usuarios = Usuario.query.order_by(Usuario.nome).all()

    return render_template(
        'tarefa_criar.html',
        documentos=documentos,
        usuarios=usuarios
    )


@view_bp.route('/tarefa/<int:id>/concluir', methods=['POST'])
@login_required
def tarefa_concluir(id):
    """Concluir tarefa"""
    tarefa = Tarefa.query.get_or_404(id)

    # Verificar permissão
    if tarefa.responsavel_id != current_user.id and not current_user.is_admin():
        flash('Acesso negado', 'danger')
        return redirect(url_for('view.tarefa_detalhe', id=id))

    if tarefa.concluida:
        flash('Tarefa já foi concluída', 'warning')
        return redirect(url_for('view.tarefa_detalhe', id=id))

    # Obter parecer
    parecer = request.form.get('parecer', '').strip()
    acao = request.form.get('acao')  # 'aprovar' ou 'rejeitar'

    # Para tarefas de publicação, pode ter upload de arquivo PDF
    if tarefa.tipo_tarefa == 'Publicar':
        arquivo = request.files.get('arquivo_pdf')
        if arquivo and arquivo.filename:
            extensao = arquivo.filename.rsplit('.', 1)[1].lower()
            if extensao == 'pdf':
                filename = secure_filename(arquivo.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename_final = f"publicado_{timestamp}_{filename}"
                caminho_completo = os.path.join(Config.UPLOAD_FOLDER_DOCUMENTOS, filename_final)

                os.makedirs(Config.UPLOAD_FOLDER_DOCUMENTOS, exist_ok=True)
                arquivo.save(caminho_completo)

                # Atualizar caminho do documento
                tarefa.documento.caminho_arquivo = caminho_completo

    # Concluir tarefa
    tarefa.status = 'concluida'
    tarefa.data_conclusao = datetime.utcnow()
    tarefa.parecer = parecer or 'Tarefa concluída'

    # Atualizar status do documento baseado no tipo de tarefa e ação
    if acao == 'aprovar':
        if tarefa.tipo_tarefa == 'Revisar':
            tarefa.documento.status = 'revisao'
        elif tarefa.tipo_tarefa == 'Validar':
            tarefa.documento.status = 'aprovado'
        elif tarefa.tipo_tarefa == 'Publicar':
            tarefa.documento.status = 'publicado'
            tarefa.documento.data_publicacao = datetime.utcnow()
    elif acao == 'rejeitar':
        tarefa.documento.status = 'rascunho'

    db.session.commit()

    flash('Tarefa concluída com sucesso!', 'success')
    return redirect(url_for('view.tarefa_detalhe', id=id))


# ============================================================================
# USUÁRIOS
# ============================================================================

@view_bp.route('/usuarios')
@login_required
def usuarios():
    """Lista de usuários (apenas admin)"""
    if not current_user.is_admin():
        flash('Acesso negado', 'danger')
        return redirect(url_for('view.dashboard'))

    usuarios = Usuario.query.order_by(Usuario.nome).all()
    return render_template('usuarios.html', usuarios=usuarios)


@view_bp.route('/usuario/criar', methods=['POST'])
@login_required
def usuario_criar():
    """Criar novo usuário (apenas admin)"""
    if not current_user.is_admin():
        flash('Acesso negado', 'danger')
        return redirect(url_for('view.usuarios'))

    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')
    perfil = request.form.get('perfil')
    setor = request.form.get('setor')

    # Validações
    if Usuario.query.filter_by(email=email).first():
        flash('Email já cadastrado', 'danger')
        return redirect(url_for('view.usuarios'))

    # Criar usuário
    usuario = Usuario(
        nome=nome,
        email=email,
        senha_hash=generate_password_hash(senha),
        perfil=perfil,
        setor=setor
    )

    db.session.add(usuario)
    db.session.commit()

    flash(f'Usuário {nome} criado com sucesso!', 'success')
    return redirect(url_for('view.usuarios'))


@view_bp.route('/usuario/<int:id>/editar', methods=['POST'])
@login_required
def usuario_editar(id):
    """Editar usuário (apenas admin)"""
    if not current_user.is_admin():
        flash('Acesso negado', 'danger')
        return redirect(url_for('view.usuarios'))

    usuario = Usuario.query.get_or_404(id)

    usuario.nome = request.form.get('nome')
    usuario.email = request.form.get('email')
    usuario.perfil = request.form.get('perfil')
    usuario.setor = request.form.get('setor')

    # Atualizar senha apenas se fornecida
    nova_senha = request.form.get('senha')
    if nova_senha:
        usuario.senha_hash = generate_password_hash(nova_senha)

    db.session.commit()

    flash(f'Usuário {usuario.nome} atualizado com sucesso!', 'success')
    return redirect(url_for('view.usuarios'))


@view_bp.route('/usuario/<int:id>/excluir', methods=['POST'])
@login_required
def usuario_excluir(id):
    """Excluir usuário (apenas admin)"""
    if not current_user.is_admin():
        flash('Acesso negado', 'danger')
        return redirect(url_for('view.usuarios'))

    if id == current_user.id:
        flash('Você não pode excluir sua própria conta', 'danger')
        return redirect(url_for('view.usuarios'))

    usuario = Usuario.query.get_or_404(id)
    nome = usuario.nome

    db.session.delete(usuario)
    db.session.commit()

    flash(f'Usuário {nome} excluído com sucesso!', 'success')
    return redirect(url_for('view.usuarios'))


# ============================================================================
# PERFIL
# ============================================================================

@view_bp.route('/perfil')
@login_required
def perfil():
    """Perfil do usuário"""
    # Estatísticas do usuário
    stats = {
        'tarefas_pendentes': Tarefa.query.filter_by(
            responsavel_id=current_user.id,
            concluida=False
        ).count(),
        'tarefas_concluidas_mes': Tarefa.query.filter(
            Tarefa.responsavel_id == current_user.id,
            Tarefa.concluida == True,
            Tarefa.data_conclusao >= datetime.utcnow() - timedelta(days=30)
        ).count(),
        'documentos_criados': Documento.query.filter_by(
            criador_id=current_user.id
        ).count()
    }

    return render_template('perfil.html', stats=stats)


@view_bp.route('/alterar-senha', methods=['POST'])
@login_required
def alterar_senha():
    """Alterar senha do usuário"""
    senha_atual = request.form.get('senha_atual')
    senha_nova = request.form.get('senha_nova')
    senha_confirma = request.form.get('senha_confirma')

    # Validações
    if not check_password_hash(current_user.senha_hash, senha_atual):
        flash('Senha atual incorreta', 'danger')
        return redirect(url_for('view.perfil'))

    if senha_nova != senha_confirma:
        flash('As senhas não coincidem', 'danger')
        return redirect(url_for('view.perfil'))

    if len(senha_nova) < 6:
        flash('A nova senha deve ter pelo menos 6 caracteres', 'danger')
        return redirect(url_for('view.perfil'))

    # Atualizar senha
    current_user.senha_hash = generate_password_hash(senha_nova)
    db.session.commit()

    flash('Senha alterada com sucesso!', 'success')
    return redirect(url_for('view.perfil'))


# ============================================================================
# REPOSITÓRIO PÚBLICO
# ============================================================================

@view_bp.route('/repositorio-publico')
@login_required
def repositorio_publico():
    """Repositório de documentos públicos"""
    page = request.args.get('page', 1, type=int)
    per_page = 12

    # Filtros
    query = Documento.query.filter_by(status='publicado')
    busca = request.args.get('q')
    tipo = request.args.get('tipo')
    setor = request.args.get('setor')

    if busca:
        query = query.filter(
            (Documento.titulo.ilike(f'%{busca}%')) |
            (Documento.codigo.ilike(f'%{busca}%'))
        )
    if tipo:
        query = query.filter_by(tipo_documento=tipo)
    if setor:
        query = query.filter_by(setor=setor)

    documentos = query.order_by(Documento.data_publicacao.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Adicionar propriedades de vencimento
    for doc in documentos.items:
        doc.esta_vencido_flag = doc.data_vencimento and doc.data_vencimento < datetime.utcnow()
        doc.proxima_vencimento_flag = doc.data_vencimento and doc.data_vencimento < datetime.utcnow() + timedelta(days=30) and not doc.esta_vencido_flag

    return render_template('repositorio_publico.html', documentos=documentos)
