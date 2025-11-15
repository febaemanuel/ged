"""
Rotas de Busca Avançada do Sistema GED
"""

from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from sqlalchemy import or_, and_
from datetime import datetime, timedelta

from app.models import db, Documento, Tarefa, Usuario
from app.utils.security import sanitize_like_pattern

bp = Blueprint('busca', __name__, url_prefix='/busca')


@bp.route('/', methods=['GET'])
@login_required
def busca_avancada():
    """Página de busca avançada"""
    return render_template('busca_avancada.html')


@bp.route('/api/search', methods=['POST'])
@login_required
def buscar():
    """
    Busca avançada de documentos

    JSON body:
        - query: Termo de busca
        - tipo: Tipo de documento
        - status: Status
        - setor: Setor
        - data_inicio: Data inicial
        - data_fim: Data final
        - autor_id: ID do autor
    """
    data = request.get_json() or {}

    query_text = data.get('query', '').strip()
    tipo = data.get('tipo')
    status = data.get('status')
    setor = data.get('setor')
    data_inicio = data.get('data_inicio')
    data_fim = data.get('data_fim')
    autor_id = data.get('autor_id')

    # Query base
    query = Documento.query

    # Aplica filtros de permissão
    if not current_user.is_admin():
        if current_user.perfil == 'comum':
            query = query.filter_by(criador_id=current_user.id)
        elif current_user.setor:
            query = query.filter(
                or_(
                    Documento.setor == current_user.setor,
                    Documento.criador_id == current_user.id
                )
            )

    # Busca textual
    if query_text:
        # FIX: SQL Injection - sanitiza input antes de usar em ILIKE
        query_text_safe = sanitize_like_pattern(query_text)
        query = query.filter(
            or_(
                Documento.titulo.ilike(f'%{query_text_safe}%'),
                Documento.descricao.ilike(f'%{query_text_safe}%'),
                Documento.codigo_provisorio.ilike(f'%{query_text_safe}%'),
                Documento.codigo_definitivo.ilike(f'%{query_text_safe}%'),
                Documento.texto_extraido.ilike(f'%{query_text_safe}%')
            )
        )

    # Filtros adicionais
    if tipo:
        query = query.filter_by(tipo_documento=tipo)

    if status:
        query = query.filter_by(status=status)

    if setor:
        query = query.filter_by(setor=setor)

    if autor_id:
        query = query.filter_by(criador_id=autor_id)

    # Filtros de data
    if data_inicio:
        try:
            dt_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(Documento.data_criacao >= dt_inicio)
        except ValueError:
            pass

    if data_fim:
        try:
            dt_fim = datetime.strptime(data_fim, '%Y-%m-%d')
            query = query.filter(Documento.data_criacao <= dt_fim)
        except ValueError:
            pass

    # Executa busca
    documentos = query.order_by(Documento.data_criacao.desc()).limit(100).all()

    return jsonify({
        'total': len(documentos),
        'resultados': [{
            'id': d.id,
            'titulo': d.titulo,
            'codigo': d.codigo,
            'tipo_documento': d.tipo_documento,
            'status': d.status,
            'setor': d.setor,
            'criador': d.criador.nome,
            'data_criacao': d.data_criacao.isoformat(),
            'resumo': (d.get_metadados().get('resumo', {}).get('resumo', '')[:200]
                      if d.get_metadados() else '')
        } for d in documentos]
    })


@bp.route('/api/stats', methods=['GET'])
@login_required
def estatisticas_gerais():
    """Estatísticas gerais do sistema"""

    if not current_user.is_gerente_ou_superior():
        return jsonify({'erro': 'Sem permissão'}), 403

    # Documentos por tipo
    docs_por_tipo = db.session.query(
        Documento.tipo_documento,
        db.func.count(Documento.id)
    ).group_by(Documento.tipo_documento).all()

    # Documentos por status
    docs_por_status = db.session.query(
        Documento.status,
        db.func.count(Documento.id)
    ).group_by(Documento.status).all()

    # Tarefas por status
    tarefas_pendentes = Tarefa.query.filter_by(concluida=False).count()
    tarefas_concluidas = Tarefa.query.filter_by(concluida=True).count()

    # Tarefas atrasadas
    tarefas_atrasadas = Tarefa.query.filter(
        Tarefa.concluida == False,
        Tarefa.prazo < datetime.utcnow()
    ).count()

    # Documentos criados nos últimos 30 dias
    data_limite = datetime.utcnow() - timedelta(days=30)
    docs_recentes = Documento.query.filter(
        Documento.data_criacao >= data_limite
    ).count()

    return jsonify({
        'documentos': {
            'total': Documento.query.count(),
            'por_tipo': {tipo: count for tipo, count in docs_por_tipo},
            'por_status': {status: count for status, count in docs_por_status},
            'ultimos_30_dias': docs_recentes
        },
        'tarefas': {
            'total': Tarefa.query.count(),
            'pendentes': tarefas_pendentes,
            'concluidas': tarefas_concluidas,
            'atrasadas': tarefas_atrasadas
        },
        'usuarios': {
            'total': Usuario.query.count(),
            'ativos': Usuario.query.filter_by(ativo=True).count()
        }
    })


@bp.route('/api/sugestoes', methods=['GET'])
@login_required
def sugestoes_busca():
    """Sugestões de busca baseadas em documentos recentes"""

    query_text = request.args.get('q', '').strip()

    if not query_text or len(query_text) < 2:
        return jsonify({'sugestoes': []})

    # FIX: SQL Injection - sanitiza input antes de usar em ILIKE
    query_text_safe = sanitize_like_pattern(query_text)
    query = Documento.query.filter(
        or_(
            Documento.titulo.ilike(f'%{query_text_safe}%'),
            Documento.codigo_provisorio.ilike(f'%{query_text_safe}%'),
            Documento.codigo_definitivo.ilike(f'%{query_text_safe}%')
        )
    )

    # Aplica filtros de permissão
    if not current_user.is_admin():
        if current_user.perfil == 'comum':
            query = query.filter_by(criador_id=current_user.id)
        elif current_user.setor:
            query = query.filter_by(setor=current_user.setor)

    documentos = query.limit(5).all()

    return jsonify({
        'sugestoes': [{
            'id': d.id,
            'texto': f'{d.codigo} - {d.titulo}',
            'tipo': d.tipo_documento
        } for d in documentos]
    })
