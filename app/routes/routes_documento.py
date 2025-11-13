"""
Rotas de Documentos do Sistema GED

Endpoints:
- GET /documentos - Lista documentos
- GET /documento/<id> - Visualiza documento e timeline
- POST /documento/criar - Cria novo documento
- PUT /documento/<id> - Atualiza documento
- DELETE /documento/<id> - Remove documento
- GET /documento/<id>/download - Download do arquivo
- GET /publico - Repositório público de documentos publicados
"""

from flask import Blueprint, request, jsonify, send_file, current_app, render_template
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os

from app.models import db, Documento, Tarefa, Usuario
from app.services import extract_text

bp = Blueprint('documento', __name__, url_prefix='/documento')


def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@bp.route('/lista', methods=['GET'])
@login_required
def listar_documentos():
    """
    Lista documentos com filtros opcionais

    Query params:
        - status: Filtrar por status
        - tipo: Filtrar por tipo de documento
        - setor: Filtrar por setor
        - page: Página (paginação)
        - per_page: Itens por página
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Documento.query

    # Filtros
    if not current_user.is_admin():
        # Usuários comuns veem apenas seus documentos
        if current_user.perfil == 'comum':
            query = query.filter_by(criador_id=current_user.id)
        # Gerentes veem documentos do seu setor
        elif current_user.setor:
            query = query.filter_by(setor=current_user.setor)

    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)

    tipo = request.args.get('tipo')
    if tipo:
        query = query.filter_by(tipo_documento=tipo)

    setor = request.args.get('setor')
    if setor:
        query = query.filter_by(setor=setor)

    # Ordenação
    query = query.order_by(Documento.data_criacao.desc())

    # Paginação
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    documentos = pagination.items

    return jsonify({
        'documentos': [{
            'id': doc.id,
            'titulo': doc.titulo,
            'tipo_documento': doc.tipo_documento,
            'codigo_provisorio': doc.codigo_provisorio,
            'codigo_definitivo': doc.codigo_definitivo,
            'status': doc.status,
            'data_criacao': doc.data_criacao.isoformat() if doc.data_criacao else None,
            'data_publicacao': doc.data_publicacao.isoformat() if doc.data_publicacao else None,
            'criador': doc.criador.nome if doc.criador else None,
            'esta_vencido': doc.esta_vencido(),
            'dias_ate_vencimento': doc.dias_ate_vencimento()
        } for doc in documentos],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@bp.route('/<int:id>', methods=['GET'])
@login_required
def visualizar_documento(id):
    """
    Visualiza detalhes do documento e timeline de tarefas

    Returns:
        JSON com informações completas do documento e histórico
    """
    documento = Documento.query.get_or_404(id)

    # Verifica permissão de visualização
    if not current_user.is_admin() and not current_user.is_gerente_ou_superior():
        if documento.criador_id != current_user.id:
            return jsonify({'erro': 'Sem permissão para visualizar este documento'}), 403

    # Timeline de tarefas
    tarefas = Tarefa.query.filter_by(documento_id=id).order_by(Tarefa.data_criacao.desc()).all()

    timeline = []
    for tarefa in tarefas:
        timeline.append({
            'id': tarefa.id,
            'tipo': tarefa.tipo_tarefa,
            'criador': tarefa.criador.nome,
            'responsavel': tarefa.responsavel.nome,
            'data_criacao': tarefa.data_criacao.isoformat(),
            'data_conclusao': tarefa.data_conclusao.isoformat() if tarefa.data_conclusao else None,
            'concluida': tarefa.concluida,
            'parecer': tarefa.parecer,
            'aprovado': tarefa.aprovado,
            'esta_atrasada': tarefa.esta_atrasada()
        })

    return jsonify({
        'documento': {
            'id': documento.id,
            'titulo': documento.titulo,
            'tipo_documento': documento.tipo_documento,
            'descricao': documento.descricao,
            'setor': documento.setor,
            'codigo_provisorio': documento.codigo_provisorio,
            'codigo_definitivo': documento.codigo_definitivo,
            'status': documento.status,
            'versao': documento.versao,
            'data_criacao': documento.data_criacao.isoformat(),
            'data_publicacao': documento.data_publicacao.isoformat() if documento.data_publicacao else None,
            'data_vencimento': documento.data_vencimento.isoformat() if documento.data_vencimento else None,
            'validade_anos': documento.validade_anos,
            'criador': documento.criador.nome,
            'arquivo_original': documento.arquivo_original,
            'arquivo_publicado': documento.arquivo_publicado_pdf,
            'metadados': documento.get_metadados(),
            'esta_vencido': documento.esta_vencido(),
            'dias_ate_vencimento': documento.dias_ate_vencimento()
        },
        'timeline': timeline
    })


@bp.route('/criar', methods=['POST'])
@login_required
def criar_documento():
    """
    Cria novo documento

    Form data:
        - titulo: Título do documento
        - tipo_documento: POP, Manual ou Protocolo
        - descricao: Descrição (opcional)
        - setor: Setor responsável
        - arquivo: Arquivo do documento (.doc, .odt)
        - validade_anos: Anos de validade (padrão: 5)
    """
    # Validação
    if 'arquivo' not in request.files:
        return jsonify({'erro': 'Arquivo não enviado'}), 400

    arquivo = request.files['arquivo']
    if arquivo.filename == '':
        return jsonify({'erro': 'Nenhum arquivo selecionado'}), 400

    if not allowed_file(arquivo.filename):
        return jsonify({'erro': 'Tipo de arquivo não permitido'}), 400

    titulo = request.form.get('titulo')
    tipo_documento = request.form.get('tipo_documento')
    descricao = request.form.get('descricao', '')
    setor = request.form.get('setor') or current_user.setor
    validade_anos = request.form.get('validade_anos', 5, type=int)

    if not titulo or not tipo_documento:
        return jsonify({'erro': 'Título e tipo de documento são obrigatórios'}), 400

    if tipo_documento not in current_app.config['TIPOS_DOCUMENTO']:
        return jsonify({'erro': 'Tipo de documento inválido'}), 400

    # Salva arquivo
    filename = secure_filename(arquivo.filename)
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    nome_arquivo = f"{timestamp}_{filename}"
    caminho_arquivo = os.path.join(current_app.config['UPLOAD_FOLDER'], nome_arquivo)
    arquivo.save(caminho_arquivo)

    # Cria documento
    documento = Documento(
        titulo=titulo,
        tipo_documento=tipo_documento,
        descricao=descricao,
        setor=setor,
        arquivo_original=nome_arquivo,
        criador_id=current_user.id,
        validade_anos=validade_anos,
        status='Novo'
    )

    db.session.add(documento)
    db.session.commit()

    return jsonify({
        'mensagem': 'Documento criado com sucesso',
        'documento': {
            'id': documento.id,
            'codigo_provisorio': documento.codigo_provisorio,
            'titulo': documento.titulo,
            'status': documento.status
        }
    }), 201


@bp.route('/<int:id>', methods=['PUT'])
@login_required
def atualizar_documento(id):
    """
    Atualiza informações do documento

    JSON body:
        - titulo
        - descricao
        - setor
        - tipo_documento
    """
    documento = Documento.query.get_or_404(id)

    # Verifica permissão
    if not documento.pode_editar(current_user):
        return jsonify({'erro': 'Sem permissão para editar este documento'}), 403

    data = request.get_json()

    if 'titulo' in data:
        documento.titulo = data['titulo']
    if 'descricao' in data:
        documento.descricao = data['descricao']
    if 'setor' in data:
        documento.setor = data['setor']
    if 'tipo_documento' in data and data['tipo_documento'] in current_app.config['TIPOS_DOCUMENTO']:
        documento.tipo_documento = data['tipo_documento']

    db.session.commit()

    return jsonify({'mensagem': 'Documento atualizado com sucesso'})


@bp.route('/<int:id>', methods=['DELETE'])
@login_required
def deletar_documento(id):
    """
    Remove documento (apenas se status = Novo ou Cancelado)
    """
    documento = Documento.query.get_or_404(id)

    # Apenas admin ou criador podem deletar
    if not current_user.is_admin() and documento.criador_id != current_user.id:
        return jsonify({'erro': 'Sem permissão para deletar este documento'}), 403

    # Apenas documentos Novo ou Cancelado podem ser deletados
    if documento.status not in ['Novo', 'Cancelado']:
        return jsonify({'erro': 'Apenas documentos "Novo" ou "Cancelado" podem ser deletados'}), 400

    # Remove arquivo físico
    if documento.arquivo_original:
        caminho = os.path.join(current_app.config['UPLOAD_FOLDER'], documento.arquivo_original)
        if os.path.exists(caminho):
            os.remove(caminho)

    if documento.arquivo_publicado_pdf:
        caminho = os.path.join(current_app.config['PUBLISHED_FOLDER'], documento.arquivo_publicado_pdf)
        if os.path.exists(caminho):
            os.remove(caminho)

    db.session.delete(documento)
    db.session.commit()

    return jsonify({'mensagem': 'Documento deletado com sucesso'})


@bp.route('/<int:id>/download/<tipo>', methods=['GET'])
@login_required
def download_arquivo(id, tipo):
    """
    Download do arquivo do documento

    Args:
        tipo: 'original' ou 'publicado'
    """
    documento = Documento.query.get_or_404(id)

    if tipo == 'original':
        if not documento.arquivo_original:
            return jsonify({'erro': 'Arquivo original não encontrado'}), 404
        caminho = os.path.join(current_app.config['UPLOAD_FOLDER'], documento.arquivo_original)
        nome_download = documento.arquivo_original
    elif tipo == 'publicado':
        if not documento.arquivo_publicado_pdf:
            return jsonify({'erro': 'Arquivo publicado não encontrado'}), 404
        caminho = os.path.join(current_app.config['PUBLISHED_FOLDER'], documento.arquivo_publicado_pdf)
        nome_download = documento.arquivo_publicado_pdf
    else:
        return jsonify({'erro': 'Tipo de arquivo inválido'}), 400

    if not os.path.exists(caminho):
        return jsonify({'erro': 'Arquivo não encontrado no servidor'}), 404

    return send_file(caminho, as_attachment=True, download_name=nome_download)


@bp.route('/publico', methods=['GET'])
def repositorio_publico():
    """
    Repositório público de documentos publicados e válidos
    Acesso livre (sem autenticação)

    Query params:
        - q: Busca por título
        - tipo: Filtro por tipo de documento
        - setor: Filtro por setor
        - page: Página
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Documento.query.filter_by(status='Aprovado e Publicado')

    # Apenas documentos válidos (não vencidos)
    query = query.filter(
        (Documento.data_vencimento == None) | (Documento.data_vencimento > datetime.utcnow())
    )

    # Filtros
    q = request.args.get('q')
    if q:
        query = query.filter(Documento.titulo.ilike(f'%{q}%'))

    tipo = request.args.get('tipo')
    if tipo:
        query = query.filter_by(tipo_documento=tipo)

    setor = request.args.get('setor')
    if setor:
        query = query.filter_by(setor=setor)

    # Ordenação
    query = query.order_by(Documento.data_publicacao.desc())

    # Paginação
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    documentos = pagination.items

    return jsonify({
        'documentos': [{
            'id': doc.id,
            'titulo': doc.titulo,
            'tipo_documento': doc.tipo_documento,
            'codigo_definitivo': doc.codigo_definitivo,
            'setor': doc.setor,
            'data_publicacao': doc.data_publicacao.isoformat(),
            'data_vencimento': doc.data_vencimento.isoformat() if doc.data_vencimento else None,
            'versao': doc.versao
        } for doc in documentos],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@bp.route('/<int:id>/mudar_status', methods=['POST'])
@login_required
def mudar_status(id):
    """
    Muda status do documento

    JSON body:
        - novo_status: Novo status do documento
        - motivo: Justificativa da mudança
    """
    documento = Documento.query.get_or_404(id)

    # Apenas gerentes ou superior podem mudar status
    if not current_user.is_gerente_ou_superior():
        return jsonify({'erro': 'Sem permissão para alterar status'}), 403

    data = request.get_json()
    novo_status = data.get('novo_status')
    motivo = data.get('motivo', '')

    if not novo_status:
        return jsonify({'erro': 'Novo status não informado'}), 400

    documento.status = novo_status
    db.session.commit()

    return jsonify({
        'mensagem': 'Status alterado com sucesso',
        'novo_status': novo_status
    })
