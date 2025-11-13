"""
Rotas de Tarefas do Sistema GED

Endpoints:
- GET /tarefa/lista - Lista tarefas do usuário
- GET /tarefa/<id> - Visualiza tarefa
- POST /tarefa/criar - Cria nova tarefa
- POST /tarefa/<id>/concluir - Conclui tarefa
- GET /tarefa/minhas - Minhas tarefas pendentes
- GET /tarefa/atrasadas - Tarefas atrasadas (gerentes)
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os

from app.models import db, Tarefa, Documento, Usuario

bp = Blueprint('tarefa', __name__, url_prefix='/api/tarefa')


@bp.route('/lista', methods=['GET'])
@login_required
def listar_tarefas():
    """
    Lista tarefas com filtros

    Query params:
        - documento_id: Filtrar por documento
        - concluida: true/false
        - responsavel_id: Filtrar por responsável
        - tipo: Tipo de tarefa
    """
    query = Tarefa.query

    # Filtro de permissão
    if not current_user.is_gerente_ou_superior():
        # Usuários comuns veem apenas suas tarefas
        query = query.filter_by(responsavel_id=current_user.id)

    # Filtros
    documento_id = request.args.get('documento_id', type=int)
    if documento_id:
        query = query.filter_by(documento_id=documento_id)

    concluida = request.args.get('concluida')
    if concluida is not None:
        concluida_bool = concluida.lower() == 'true'
        query = query.filter_by(concluida=concluida_bool)

    responsavel_id = request.args.get('responsavel_id', type=int)
    if responsavel_id:
        query = query.filter_by(responsavel_id=responsavel_id)

    tipo = request.args.get('tipo')
    if tipo:
        query = query.filter_by(tipo_tarefa=tipo)

    # Ordenação
    query = query.order_by(Tarefa.prazo.asc())

    tarefas = query.all()

    return jsonify({
        'tarefas': [{
            'id': t.id,
            'tipo_tarefa': t.tipo_tarefa,
            'documento_id': t.documento_id,
            'documento_titulo': t.documento.titulo,
            'documento_codigo': t.documento.codigo_provisorio or t.documento.codigo_definitivo,
            'criador': t.criador.nome,
            'responsavel': t.responsavel.nome,
            'descricao': t.descricao,
            'prioridade': t.prioridade,
            'prazo': t.prazo.isoformat() if t.prazo else None,
            'data_criacao': t.data_criacao.isoformat(),
            'data_conclusao': t.data_conclusao.isoformat() if t.data_conclusao else None,
            'concluida': t.concluida,
            'parecer': t.parecer,
            'aprovado': t.aprovado,
            'esta_atrasada': t.esta_atrasada(),
            'dias_ate_prazo': t.dias_ate_prazo()
        } for t in tarefas]
    })


@bp.route('/<int:id>', methods=['GET'])
@login_required
def visualizar_tarefa(id):
    """Visualiza detalhes da tarefa"""
    tarefa = Tarefa.query.get_or_404(id)

    # Verifica permissão
    if not current_user.is_gerente_ou_superior():
        if tarefa.responsavel_id != current_user.id and tarefa.criador_id != current_user.id:
            return jsonify({'erro': 'Sem permissão para visualizar esta tarefa'}), 403

    return jsonify({
        'tarefa': {
            'id': tarefa.id,
            'tipo_tarefa': tarefa.tipo_tarefa,
            'descricao': tarefa.descricao,
            'prioridade': tarefa.prioridade,
            'documento': {
                'id': tarefa.documento.id,
                'titulo': tarefa.documento.titulo,
                'tipo': tarefa.documento.tipo_documento,
                'codigo': tarefa.documento.codigo_provisorio or tarefa.documento.codigo_definitivo,
                'status': tarefa.documento.status
            },
            'criador': {
                'id': tarefa.criador.id,
                'nome': tarefa.criador.nome,
                'email': tarefa.criador.email
            },
            'responsavel': {
                'id': tarefa.responsavel.id,
                'nome': tarefa.responsavel.nome,
                'email': tarefa.responsavel.email
            },
            'data_criacao': tarefa.data_criacao.isoformat(),
            'prazo': tarefa.prazo.isoformat() if tarefa.prazo else None,
            'data_conclusao': tarefa.data_conclusao.isoformat() if tarefa.data_conclusao else None,
            'concluida': tarefa.concluida,
            'parecer': tarefa.parecer,
            'aprovado': tarefa.aprovado,
            'arquivo_anexo': tarefa.arquivo_anexo,
            'esta_atrasada': tarefa.esta_atrasada(),
            'dias_ate_prazo': tarefa.dias_ate_prazo()
        }
    })


@bp.route('/criar', methods=['POST'])
@login_required
def criar_tarefa():
    """
    Cria nova tarefa

    JSON body:
        - documento_id: ID do documento
        - responsavel_id: ID do responsável
        - tipo_tarefa: Tipo da tarefa
        - descricao: Descrição (opcional)
        - prioridade: baixa, normal, alta, urgente
        - prazo: Data limite (ISO format)
    """
    # Apenas gerentes podem criar tarefas
    if not current_user.is_gerente_ou_superior():
        return jsonify({'erro': 'Apenas gerentes podem criar tarefas'}), 403

    data = request.get_json()

    documento_id = data.get('documento_id')
    responsavel_id = data.get('responsavel_id')
    tipo_tarefa = data.get('tipo_tarefa')
    descricao = data.get('descricao', '')
    prioridade = data.get('prioridade', 'normal')
    prazo_str = data.get('prazo')

    # Validações
    if not documento_id or not responsavel_id or not tipo_tarefa:
        return jsonify({'erro': 'documento_id, responsavel_id e tipo_tarefa são obrigatórios'}), 400

    documento = Documento.query.get(documento_id)
    if not documento:
        return jsonify({'erro': 'Documento não encontrado'}), 404

    responsavel = Usuario.query.get(responsavel_id)
    if not responsavel:
        return jsonify({'erro': 'Responsável não encontrado'}), 404

    if tipo_tarefa not in current_app.config['TIPOS_TAREFA']:
        return jsonify({'erro': 'Tipo de tarefa inválido'}), 400

    # Parse prazo
    prazo = None
    if prazo_str:
        try:
            prazo = datetime.fromisoformat(prazo_str.replace('Z', '+00:00'))
        except:
            return jsonify({'erro': 'Formato de prazo inválido'}), 400

    # Cria tarefa
    tarefa = Tarefa(
        documento_id=documento_id,
        criador_id=current_user.id,
        responsavel_id=responsavel_id,
        tipo_tarefa=tipo_tarefa,
        descricao=descricao,
        prioridade=prioridade,
        prazo=prazo
    )

    db.session.add(tarefa)

    # Atualiza status do documento para "Em Análise" se for a primeira tarefa
    if documento.status == 'Novo':
        documento.status = 'Em Análise'

    db.session.commit()

    return jsonify({
        'mensagem': 'Tarefa criada com sucesso',
        'tarefa': {
            'id': tarefa.id,
            'tipo_tarefa': tarefa.tipo_tarefa,
            'responsavel': tarefa.responsavel.nome,
            'prazo': tarefa.prazo.isoformat() if tarefa.prazo else None
        }
    }), 201


@bp.route('/<int:id>/concluir', methods=['POST'])
@login_required
def concluir_tarefa(id):
    """
    Conclui uma tarefa

    Form data ou JSON:
        - parecer: Parecer do responsável
        - aprovado: true/false (para tarefas de aprovação)
        - arquivo: PDF final (para tarefa de publicação)
    """
    tarefa = Tarefa.query.get_or_404(id)

    # Verifica permissão
    if not tarefa.pode_concluir(current_user):
        return jsonify({'erro': 'Sem permissão para concluir esta tarefa'}), 403

    if tarefa.concluida:
        return jsonify({'erro': 'Tarefa já foi concluída'}), 400

    # Obtém dados
    if request.is_json:
        data = request.get_json()
        parecer = data.get('parecer', '')
        aprovado = data.get('aprovado')
        arquivo = None
    else:
        parecer = request.form.get('parecer', '')
        aprovado = request.form.get('aprovado')
        arquivo = request.files.get('arquivo')

    # Converte aprovado para boolean
    if aprovado is not None:
        if isinstance(aprovado, str):
            aprovado = aprovado.lower() == 'true'

    # Para tarefa de publicação, exige PDF
    arquivo_nome = None
    if tarefa.tipo_tarefa == 'Publicar':
        if not arquivo:
            return jsonify({'erro': 'Tarefa de publicação requer anexo de PDF final'}), 400

        filename = secure_filename(arquivo.filename)
        if not filename.endswith('.pdf'):
            return jsonify({'erro': 'Arquivo deve ser PDF'}), 400

        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        arquivo_nome = f"{timestamp}_{filename}"
        caminho = os.path.join(current_app.config['PUBLISHED_FOLDER'], arquivo_nome)
        arquivo.save(caminho)

        # Atualiza documento
        documento = tarefa.documento
        documento.arquivo_publicado_pdf = arquivo_nome
        documento.data_publicacao = datetime.utcnow()
        documento.calcular_data_vencimento()
        documento.gerar_codigo_definitivo()
        documento.status = 'Aprovado e Publicado'

    # Conclui tarefa
    tarefa.concluir(parecer=parecer, aprovado=aprovado, arquivo=arquivo_nome)

    # Lógica de mudança de status do documento
    documento = tarefa.documento

    if tarefa.tipo_tarefa == 'Aprovar' and aprovado:
        documento.status = 'Aprovado'
    elif tarefa.tipo_tarefa == 'Aprovar' and not aprovado:
        documento.status = 'Em Análise'  # Volta para análise
    elif tarefa.tipo_tarefa == 'Realizar Correção':
        documento.status = 'Em Análise'

    db.session.commit()

    return jsonify({
        'mensagem': 'Tarefa concluída com sucesso',
        'tarefa': {
            'id': tarefa.id,
            'concluida': tarefa.concluida,
            'data_conclusao': tarefa.data_conclusao.isoformat(),
            'aprovado': tarefa.aprovado
        },
        'documento': {
            'id': documento.id,
            'status': documento.status,
            'codigo_definitivo': documento.codigo_definitivo
        }
    })


@bp.route('/minhas', methods=['GET'])
@login_required
def minhas_tarefas():
    """
    Retorna tarefas pendentes do usuário atual
    """
    tarefas = Tarefa.query.filter_by(
        responsavel_id=current_user.id,
        concluida=False
    ).order_by(Tarefa.prazo.asc()).all()

    return jsonify({
        'tarefas': [{
            'id': t.id,
            'tipo_tarefa': t.tipo_tarefa,
            'documento_titulo': t.documento.titulo,
            'documento_codigo': t.documento.codigo_provisorio or t.documento.codigo_definitivo,
            'descricao': t.descricao,
            'prioridade': t.prioridade,
            'prazo': t.prazo.isoformat() if t.prazo else None,
            'data_criacao': t.data_criacao.isoformat(),
            'esta_atrasada': t.esta_atrasada(),
            'dias_ate_prazo': t.dias_ate_prazo()
        } for t in tarefas],
        'total': len(tarefas),
        'atrasadas': sum(1 for t in tarefas if t.esta_atrasada())
    })


@bp.route('/atrasadas', methods=['GET'])
@login_required
def tarefas_atrasadas():
    """
    Retorna todas as tarefas atrasadas
    Apenas para gerentes e superior
    """
    if not current_user.is_gerente_ou_superior():
        return jsonify({'erro': 'Sem permissão para visualizar tarefas atrasadas'}), 403

    agora = datetime.utcnow()
    tarefas = Tarefa.query.filter(
        Tarefa.concluida == False,
        Tarefa.prazo < agora
    ).order_by(Tarefa.prazo.asc()).all()

    return jsonify({
        'tarefas': [{
            'id': t.id,
            'tipo_tarefa': t.tipo_tarefa,
            'documento_titulo': t.documento.titulo,
            'documento_codigo': t.documento.codigo_provisorio or t.documento.codigo_definitivo,
            'responsavel': t.responsavel.nome,
            'responsavel_email': t.responsavel.email,
            'prioridade': t.prioridade,
            'prazo': t.prazo.isoformat(),
            'dias_atraso': abs(t.dias_ate_prazo()) if t.dias_ate_prazo() else 0
        } for t in tarefas],
        'total': len(tarefas)
    })


@bp.route('/<int:id>', methods=['DELETE'])
@login_required
def deletar_tarefa(id):
    """
    Remove tarefa (apenas se não concluída)
    Apenas criador ou admin
    """
    tarefa = Tarefa.query.get_or_404(id)

    # Verifica permissão
    if not current_user.is_admin() and tarefa.criador_id != current_user.id:
        return jsonify({'erro': 'Sem permissão para deletar esta tarefa'}), 403

    if tarefa.concluida:
        return jsonify({'erro': 'Não é possível deletar tarefa já concluída'}), 400

    db.session.delete(tarefa)
    db.session.commit()

    return jsonify({'mensagem': 'Tarefa deletada com sucesso'})


@bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard_tarefas():
    """
    Dashboard com estatísticas de tarefas
    """
    # Tarefas do usuário
    minhas_pendentes = Tarefa.query.filter_by(
        responsavel_id=current_user.id,
        concluida=False
    ).count()

    minhas_atrasadas = Tarefa.query.filter(
        Tarefa.responsavel_id == current_user.id,
        Tarefa.concluida == False,
        Tarefa.prazo < datetime.utcnow()
    ).count()

    minhas_concluidas_mes = Tarefa.query.filter(
        Tarefa.responsavel_id == current_user.id,
        Tarefa.concluida == True,
        Tarefa.data_conclusao >= datetime.utcnow() - timedelta(days=30)
    ).count()

    stats = {
        'minhas_pendentes': minhas_pendentes,
        'minhas_atrasadas': minhas_atrasadas,
        'minhas_concluidas_mes': minhas_concluidas_mes
    }

    # Estatísticas gerenciais
    if current_user.is_gerente_ou_superior():
        total_pendentes = Tarefa.query.filter_by(concluida=False).count()
        total_atrasadas = Tarefa.query.filter(
            Tarefa.concluida == False,
            Tarefa.prazo < datetime.utcnow()
        ).count()

        stats['total_pendentes'] = total_pendentes
        stats['total_atrasadas'] = total_atrasadas

    return jsonify(stats)
