"""
Rotas de Gerenciamento de Templates de Documentos

Endpoints:
- GET /template/lista - Lista templates disponíveis
- POST /template/criar - Criar novo template (admin)
- GET /template/<id> - Detalhes de um template
- PUT /template/<id> - Atualizar template (admin)
- DELETE /template/<id> - Deletar template (admin)
- POST /template/<id>/usar - Usar template para criar documento
- GET /template/download/<id> - Download do arquivo template
"""

from flask import Blueprint, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from app.models import db, TemplateDocumento
from config import Config

bp = Blueprint('template', __name__, url_prefix='/template')


def allowed_file(filename):
    """Verifica se extensão do arquivo é permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@bp.route('/lista', methods=['GET'])
@login_required
def listar_templates():
    """
    Lista templates disponíveis para o usuário

    Query params:
        - tipo: Filtrar por tipo de documento
        - ativo: Filtrar por templates ativos (default: true)
    """
    query = TemplateDocumento.query

    # Filtro por tipo
    tipo = request.args.get('tipo')
    if tipo:
        query = query.filter_by(tipo_documento=tipo)

    # Filtro por ativo
    ativo = request.args.get('ativo', 'true').lower() == 'true'
    if ativo:
        query = query.filter_by(ativo=True)

    # Filtra templates disponíveis para o usuário
    # Templates sem setor ou do setor do usuário
    templates = []
    for template in query.all():
        if template.pode_usar(current_user):
            templates.append(template)

    return jsonify({
        'total': len(templates),
        'templates': [{
            'id': t.id,
            'nome': t.nome,
            'descricao': t.descricao,
            'tipo_documento': t.tipo_documento,
            'setor': t.setor,
            'ativo': t.ativo,
            'vezes_utilizado': t.vezes_utilizado,
            'criador': t.criador.nome,
            'data_criacao': t.data_criacao.isoformat()
        } for t in templates]
    })


@bp.route('/criar', methods=['POST'])
@login_required
def criar_template():
    """
    Cria novo template de documento
    Apenas administradores e validadores UGQ
    """
    if not (current_user.is_admin() or current_user.is_validador_ugq()):
        return jsonify({'erro': 'Sem permissão para criar templates'}), 403

    # Validação
    nome = request.form.get('nome', '').strip()
    tipo_documento = request.form.get('tipo_documento')

    if not nome:
        return jsonify({'erro': 'Nome é obrigatório'}), 400

    # Valida tipo no banco
    from app.models.models import TipoDocumento
    tipo_valido = TipoDocumento.query.filter_by(codigo=tipo_documento, ativo=True).first()
    if not tipo_valido:
        return jsonify({'erro': 'Tipo de documento inválido'}), 400

    # Upload do arquivo template
    if 'arquivo' not in request.files:
        return jsonify({'erro': 'Arquivo template é obrigatório'}), 400

    arquivo = request.files['arquivo']

    if arquivo.filename == '':
        return jsonify({'erro': 'Nenhum arquivo selecionado'}), 400

    if not allowed_file(arquivo.filename):
        return jsonify({'erro': 'Tipo de arquivo não permitido'}), 400

    # Salva arquivo
    filename = secure_filename(arquivo.filename)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename_final = f"template_{timestamp}_{filename}"

    # Cria pasta de templates se não existir
    templates_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'templates')
    os.makedirs(templates_folder, exist_ok=True)

    filepath = os.path.join(templates_folder, filename_final)
    arquivo.save(filepath)

    # Cria template
    template = TemplateDocumento(
        nome=nome,
        descricao=request.form.get('descricao', ''),
        tipo_documento=tipo_documento,
        setor=request.form.get('setor'),  # Null = disponível para todos
        arquivo_template=filename_final,
        criador_id=current_user.id
    )

    # Campos opcionais (JSON)
    campos = request.form.get('campos')
    if campos:
        try:
            import json
            template.set_campos(json.loads(campos))
        except:
            pass

    db.session.add(template)
    db.session.commit()

    return jsonify({
        'mensagem': 'Template criado com sucesso',
        'template': {
            'id': template.id,
            'nome': template.nome,
            'tipo_documento': template.tipo_documento
        }
    }), 201


@bp.route('/<int:template_id>', methods=['GET'])
@login_required
def obter_template(template_id):
    """Obtém detalhes de um template"""
    template = TemplateDocumento.query.get_or_404(template_id)

    # Verifica se usuário pode ver este template
    if not template.pode_usar(current_user):
        return jsonify({'erro': 'Template não disponível para seu setor'}), 403

    return jsonify({
        'id': template.id,
        'nome': template.nome,
        'descricao': template.descricao,
        'tipo_documento': template.tipo_documento,
        'setor': template.setor,
        'arquivo_template': template.arquivo_template,
        'ativo': template.ativo,
        'vezes_utilizado': template.vezes_utilizado,
        'campos': template.get_campos(),
        'criador': {
            'id': template.criador.id,
            'nome': template.criador.nome
        },
        'data_criacao': template.data_criacao.isoformat(),
        'data_atualizacao': template.data_atualizacao.isoformat()
    })


@bp.route('/<int:template_id>', methods=['PUT'])
@login_required
def atualizar_template(template_id):
    """
    Atualiza template existente
    Apenas admin e validador UGQ
    """
    if not (current_user.is_admin() or current_user.is_validador_ugq()):
        return jsonify({'erro': 'Sem permissão para atualizar templates'}), 403

    template = TemplateDocumento.query.get_or_404(template_id)

    # Atualiza campos
    data = request.get_json()

    if 'nome' in data:
        template.nome = data['nome'].strip()

    if 'descricao' in data:
        template.descricao = data['descricao']

    if 'tipo_documento' in data:
        from app.models.models import TipoDocumento
        tipo_valido = TipoDocumento.query.filter_by(codigo=data['tipo_documento'], ativo=True).first()
        if not tipo_valido:
            return jsonify({'erro': 'Tipo de documento inválido'}), 400
        template.tipo_documento = data['tipo_documento']

    if 'setor' in data:
        template.setor = data['setor']

    if 'ativo' in data:
        template.ativo = bool(data['ativo'])

    if 'campos' in data:
        template.set_campos(data['campos'])

    template.data_atualizacao = datetime.utcnow()

    db.session.commit()

    return jsonify({
        'mensagem': 'Template atualizado com sucesso',
        'template': {
            'id': template.id,
            'nome': template.nome,
            'ativo': template.ativo
        }
    })


@bp.route('/<int:template_id>', methods=['DELETE'])
@login_required
def deletar_template(template_id):
    """
    Deleta template
    Apenas admin
    """
    if not current_user.is_admin():
        return jsonify({'erro': 'Apenas administradores podem deletar templates'}), 403

    template = TemplateDocumento.query.get_or_404(template_id)

    # Remove arquivo físico
    templates_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'templates')
    filepath = os.path.join(templates_folder, template.arquivo_template)

    if os.path.exists(filepath):
        os.remove(filepath)

    db.session.delete(template)
    db.session.commit()

    return jsonify({
        'mensagem': 'Template deletado com sucesso'
    })


@bp.route('/download/<int:template_id>', methods=['GET'])
@login_required
def download_template(template_id):
    """Download do arquivo template"""
    template = TemplateDocumento.query.get_or_404(template_id)

    # Verifica permissão
    if not template.pode_usar(current_user):
        return jsonify({'erro': 'Template não disponível para seu setor'}), 403

    templates_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'templates')
    filepath = os.path.join(templates_folder, template.arquivo_template)

    if not os.path.exists(filepath):
        return jsonify({'erro': 'Arquivo template não encontrado'}), 404

    # Extrai apenas a extensão original do arquivo
    _, extensao = os.path.splitext(template.arquivo_template)
    nome_download = f"{template.nome}{extensao}"

    return send_file(
        filepath,
        as_attachment=True,
        download_name=nome_download
    )


@bp.route('/<int:template_id>/usar', methods=['POST'])
@login_required
def usar_template(template_id):
    """
    Marca que o template foi utilizado
    Incrementa contador de uso
    """
    template = TemplateDocumento.query.get_or_404(template_id)

    # Verifica permissão
    if not template.pode_usar(current_user):
        return jsonify({'erro': 'Template não disponível para seu setor'}), 403

    # Incrementa contador
    template.incrementar_uso()
    db.session.commit()

    return jsonify({
        'mensagem': 'Template marcado como utilizado',
        'vezes_utilizado': template.vezes_utilizado
    })
