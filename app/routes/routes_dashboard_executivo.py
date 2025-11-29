"""
Rotas do Dashboard Executivo
Interface avançada para gestão administrativa

Endpoints:
- GET /dashboard-executivo/estatisticas - Estatísticas gerais do sistema
- GET /dashboard-executivo/documentos-por-tipo - Documentos agrupados por tipo
- GET /dashboard-executivo/documentos-vencidos - Lista de documentos vencidos
- GET /dashboard-executivo/documentos-vencendo - Documentos próximos ao vencimento
- GET /dashboard-executivo/documentos-por-status - Documentos agrupados por status
- GET /dashboard-executivo/tarefas-resumo - Resumo de tarefas do sistema
- GET /dashboard-executivo/timeline-criacao - Timeline de criação de documentos
- GET /dashboard-executivo/usuarios-ativos - Estatísticas de usuários
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, extract

from app.models import db, Documento, Tarefa, Usuario, BlocoAssinatura, ValidacaoUGQ
from config import Config

bp = Blueprint('dashboard_executivo', __name__, url_prefix='/dashboard-executivo')


def verificar_permissao_executivo():
    """Apenas admin e validadores UGQ podem acessar dashboard executivo"""
    if not (current_user.is_admin() or current_user.is_validador_ugq()):
        return False
    return True


@bp.route('/estatisticas', methods=['GET'])
@login_required
def estatisticas_gerais():
    """
    Estatísticas gerais do sistema para dashboard executivo
    """
    if not verificar_permissao_executivo():
        return jsonify({'erro': 'Sem permissão para acessar dashboard executivo'}), 403

    agora = datetime.utcnow()

    # Documentos
    total_documentos = Documento.query.count()
    docs_publicados = Documento.query.filter_by(status=Config.STATUS_PUBLICADO).count()
    docs_em_aprovacao = Documento.query.filter_by(status=Config.STATUS_EM_APROVACAO).count()
    docs_em_triagem = Documento.query.filter_by(status=Config.STATUS_EM_TRIAGEM).count()
    docs_em_validacao = Documento.query.filter_by(status=Config.STATUS_EM_VALIDACAO).count()

    # Documentos vencidos
    docs_vencidos = Documento.query.filter(
        Documento.data_vencimento != None,
        Documento.data_vencimento < agora
    ).count()

    # Documentos vencendo em 30, 60, 90 dias
    data_30 = agora + timedelta(days=30)
    data_60 = agora + timedelta(days=60)
    data_90 = agora + timedelta(days=90)

    docs_vencendo_30 = Documento.query.filter(
        Documento.data_vencimento != None,
        Documento.data_vencimento > agora,
        Documento.data_vencimento <= data_30,
        Documento.status == Config.STATUS_PUBLICADO
    ).count()

    docs_vencendo_60 = Documento.query.filter(
        Documento.data_vencimento != None,
        Documento.data_vencimento > data_30,
        Documento.data_vencimento <= data_60,
        Documento.status == Config.STATUS_PUBLICADO
    ).count()

    docs_vencendo_90 = Documento.query.filter(
        Documento.data_vencimento != None,
        Documento.data_vencimento > data_60,
        Documento.data_vencimento <= data_90,
        Documento.status == Config.STATUS_PUBLICADO
    ).count()

    # Tarefas
    total_tarefas = Tarefa.query.count()
    tarefas_pendentes = Tarefa.query.filter_by(concluida=False).count()
    tarefas_atrasadas = Tarefa.query.filter(
        Tarefa.concluida == False,
        Tarefa.prazo < agora
    ).count()

    # Usuários
    total_usuarios = Usuario.query.count()
    usuarios_ativos = Usuario.query.filter_by(ativo=True).count()

    # Blocos de assinatura
    blocos_em_andamento = BlocoAssinatura.query.filter_by(status='Em Andamento').count()

    # Validações UGQ este mês
    primeiro_dia_mes = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    validacoes_mes = ValidacaoUGQ.query.filter(
        ValidacaoUGQ.data_validacao >= primeiro_dia_mes
    ).count()

    return jsonify({
        'documentos': {
            'total': total_documentos,
            'publicados': docs_publicados,
            'em_aprovacao': docs_em_aprovacao,
            'em_triagem': docs_em_triagem,
            'em_validacao': docs_em_validacao,
            'vencidos': docs_vencidos,
            'vencendo': {
                '30_dias': docs_vencendo_30,
                '60_dias': docs_vencendo_60,
                '90_dias': docs_vencendo_90
            }
        },
        'tarefas': {
            'total': total_tarefas,
            'pendentes': tarefas_pendentes,
            'atrasadas': tarefas_atrasadas,
            'taxa_conclusao': round((total_tarefas - tarefas_pendentes) / total_tarefas * 100, 1) if total_tarefas > 0 else 0
        },
        'usuarios': {
            'total': total_usuarios,
            'ativos': usuarios_ativos,
            'inativos': total_usuarios - usuarios_ativos
        },
        'workflow_ugq': {
            'blocos_assinatura_andamento': blocos_em_andamento,
            'validacoes_este_mes': validacoes_mes
        }
    })


@bp.route('/documentos-por-tipo', methods=['GET'])
@login_required
def documentos_por_tipo():
    """
    Retorna documentos agrupados por tipo
    Com detalhes completos para mostrar em modais
    """
    if not verificar_permissao_executivo():
        return jsonify({'erro': 'Sem permissão'}), 403

    # Query params para filtros
    status = request.args.get('status')
    setor = request.args.get('setor')

    resultado = {}

    # Busca tipos do banco
    from app.models.models import TipoDocumento
    tipos = TipoDocumento.query.filter_by(ativo=True).all()
    tipos_codigos = [t.codigo for t in tipos]

    for tipo in tipos_codigos:
        query = Documento.query.filter_by(tipo_documento=tipo)

        if status:
            query = query.filter_by(status=status)
        if setor:
            query = query.filter_by(setor=setor)

        documentos = query.order_by(Documento.data_criacao.desc()).all()

        resultado[tipo] = {
            'total': len(documentos),
            'documentos': [{
                'id': d.id,
                'titulo': d.titulo,
                'codigo': d.codigo_definitivo or d.codigo_provisorio,
                'status': d.status,
                'setor': d.setor,
                'criador': d.criador.nome,
                'data_criacao': d.data_criacao.isoformat(),
                'data_publicacao': d.data_publicacao.isoformat() if d.data_publicacao else None,
                'data_vencimento': d.data_vencimento.isoformat() if d.data_vencimento else None,
                'dias_ate_vencimento': d.dias_ate_vencimento(),
                'esta_vencido': d.esta_vencido() if d.data_vencimento else False
            } for d in documentos]
        }

    return jsonify(resultado)


@bp.route('/documentos-vencidos', methods=['GET'])
@login_required
def documentos_vencidos():
    """
    Lista completa de documentos vencidos
    Para modal detalhado
    """
    if not verificar_permissao_executivo():
        return jsonify({'erro': 'Sem permissão'}), 403

    agora = datetime.utcnow()

    docs = Documento.query.filter(
        Documento.data_vencimento != None,
        Documento.data_vencimento < agora
    ).order_by(Documento.data_vencimento.asc()).all()

    # Agrupa por tipo (busca do banco)
    from app.models.models import TipoDocumento
    tipos_db = TipoDocumento.query.filter_by(ativo=True).all()
    por_tipo = {}
    for tipo in tipos_db:
        docs_tipo = [d for d in docs if d.tipo_documento == tipo.codigo]
        por_tipo[tipo.codigo] = len(docs_tipo)

    return jsonify({
        'total': len(docs),
        'por_tipo': por_tipo,
        'documentos': [{
            'id': d.id,
            'titulo': d.titulo,
            'tipo_documento': d.tipo_documento,
            'codigo': d.codigo_definitivo or d.codigo_provisorio,
            'status': d.status,
            'setor': d.setor,
            'criador': d.criador.nome,
            'criador_email': d.criador.email,
            'data_publicacao': d.data_publicacao.isoformat() if d.data_publicacao else None,
            'data_vencimento': d.data_vencimento.isoformat(),
            'dias_vencido': abs(d.dias_ate_vencimento()) if d.dias_ate_vencimento() else 0
        } for d in docs]
    })


@bp.route('/documentos-vencendo', methods=['GET'])
@login_required
def documentos_vencendo():
    """
    Lista documentos próximos ao vencimento
    Query param: dias (default 30, opções: 30, 60, 90)
    """
    if not verificar_permissao_executivo():
        return jsonify({'erro': 'Sem permissão'}), 403

    dias = request.args.get('dias', 30, type=int)
    if dias not in [30, 60, 90]:
        dias = 30

    agora = datetime.utcnow()
    data_limite = agora + timedelta(days=dias)

    docs = Documento.query.filter(
        Documento.data_vencimento != None,
        Documento.data_vencimento > agora,
        Documento.data_vencimento <= data_limite,
        Documento.status == Config.STATUS_PUBLICADO
    ).order_by(Documento.data_vencimento.asc()).all()

    # Agrupa por tipo (busca do banco)
    from app.models.models import TipoDocumento
    tipos_db = TipoDocumento.query.filter_by(ativo=True).all()
    por_tipo = {}
    for tipo in tipos_db:
        docs_tipo = [d for d in docs if d.tipo_documento == tipo.codigo]
        por_tipo[tipo.codigo] = len(docs_tipo)

    return jsonify({
        'dias_limite': dias,
        'total': len(docs),
        'por_tipo': por_tipo,
        'documentos': [{
            'id': d.id,
            'titulo': d.titulo,
            'tipo_documento': d.tipo_documento,
            'codigo': d.codigo_definitivo or d.codigo_provisorio,
            'setor': d.setor,
            'criador': d.criador.nome,
            'criador_email': d.criador.email,
            'data_publicacao': d.data_publicacao.isoformat() if d.data_publicacao else None,
            'data_vencimento': d.data_vencimento.isoformat(),
            'dias_ate_vencimento': d.dias_ate_vencimento(),
            'urgencia': 'alta' if d.dias_ate_vencimento() <= 15 else 'media' if d.dias_ate_vencimento() <= 30 else 'baixa'
        } for d in docs]
    })


@bp.route('/documentos-por-status', methods=['GET'])
@login_required
def documentos_por_status():
    """
    Agrupa documentos por status
    Para cards clicáveis que abrem modais
    """
    if not verificar_permissao_executivo():
        return jsonify({'erro': 'Sem permissão'}), 403

    # Conta documentos por status
    docs_por_status = db.session.query(
        Documento.status,
        func.count(Documento.id).label('total')
    ).group_by(Documento.status).all()

    resultado = {}
    for status, total in docs_por_status:
        # Busca documentos deste status
        docs = Documento.query.filter_by(status=status).order_by(
            Documento.data_criacao.desc()
        ).limit(100).all()

        resultado[status] = {
            'total': total,
            'documentos': [{
                'id': d.id,
                'titulo': d.titulo,
                'tipo_documento': d.tipo_documento,
                'codigo': d.codigo_definitivo or d.codigo_provisorio,
                'setor': d.setor,
                'criador': d.criador.nome,
                'data_criacao': d.data_criacao.isoformat()
            } for d in docs]
        }

    return jsonify(resultado)


@bp.route('/tarefas-resumo', methods=['GET'])
@login_required
def tarefas_resumo():
    """
    Resumo de tarefas do sistema
    Agrupado por tipo e status
    """
    if not verificar_permissao_executivo():
        return jsonify({'erro': 'Sem permissão'}), 403

    agora = datetime.utcnow()

    # Tarefas por tipo
    tarefas_por_tipo = db.session.query(
        Tarefa.tipo_tarefa,
        func.count(Tarefa.id).label('total'),
        func.sum(func.cast(Tarefa.concluida == False, db.Integer)).label('pendentes')
    ).group_by(Tarefa.tipo_tarefa).all()

    # Tarefas atrasadas por responsável
    tarefas_atrasadas = db.session.query(
        Usuario.nome,
        Usuario.email,
        Usuario.setor,
        func.count(Tarefa.id).label('total_atrasadas')
    ).join(Tarefa, Tarefa.responsavel_id == Usuario.id).filter(
        Tarefa.concluida == False,
        Tarefa.prazo < agora
    ).group_by(Usuario.id, Usuario.nome, Usuario.email, Usuario.setor).order_by(
        func.count(Tarefa.id).desc()
    ).limit(10).all()

    return jsonify({
        'por_tipo': [{
            'tipo': tipo,
            'total': total,
            'pendentes': pendentes or 0,
            'concluidas': total - (pendentes or 0)
        } for tipo, total, pendentes in tarefas_por_tipo],
        'top_usuarios_atrasados': [{
            'nome': nome,
            'email': email,
            'setor': setor,
            'tarefas_atrasadas': total
        } for nome, email, setor, total in tarefas_atrasadas]
    })


@bp.route('/timeline-criacao', methods=['GET'])
@login_required
def timeline_criacao():
    """
    Timeline de criação de documentos
    Últimos 12 meses
    """
    if not verificar_permissao_executivo():
        return jsonify({'erro': 'Sem permissão'}), 403

    # Documentos por mês nos últimos 12 meses
    doze_meses_atras = datetime.utcnow() - timedelta(days=365)

    docs_por_mes = db.session.query(
        extract('year', Documento.data_criacao).label('ano'),
        extract('month', Documento.data_criacao).label('mes'),
        func.count(Documento.id).label('total')
    ).filter(
        Documento.data_criacao >= doze_meses_atras
    ).group_by('ano', 'mes').order_by('ano', 'mes').all()

    return jsonify({
        'timeline': [{
            'ano': int(ano),
            'mes': int(mes),
            'total': total,
            'periodo': f"{int(ano)}-{int(mes):02d}"
        } for ano, mes, total in docs_por_mes]
    })


@bp.route('/usuarios-ativos', methods=['GET'])
@login_required
def usuarios_ativos_stats():
    """
    Estatísticas de usuários ativos
    Último acesso, documentos criados, tarefas concluídas
    """
    if not verificar_permissao_executivo():
        return jsonify({'erro': 'Sem permissão'}), 403

    # Usuários mais ativos (últimos 30 dias)
    trinta_dias_atras = datetime.utcnow() - timedelta(days=30)

    usuarios_stats = db.session.query(
        Usuario.id,
        Usuario.nome,
        Usuario.email,
        Usuario.perfil,
        Usuario.setor,
        Usuario.ultimo_acesso,
        func.count(Documento.id).label('docs_criados'),
        func.count(Tarefa.id).label('tarefas_concluidas')
    ).outerjoin(
        Documento, Documento.criador_id == Usuario.id
    ).outerjoin(
        Tarefa, db.and_(
            Tarefa.responsavel_id == Usuario.id,
            Tarefa.concluida == True,
            Tarefa.data_conclusao >= trinta_dias_atras
        )
    ).filter(
        Usuario.ativo == True
    ).group_by(
        Usuario.id
    ).order_by(
        func.count(Tarefa.id).desc()
    ).limit(20).all()

    return jsonify({
        'periodo': '30_dias',
        'usuarios': [{
            'id': u.id,
            'nome': u.nome,
            'email': u.email,
            'perfil': u.perfil,
            'setor': u.setor,
            'ultimo_acesso': u.ultimo_acesso.isoformat() if u.ultimo_acesso else None,
            'documentos_criados': u.docs_criados,
            'tarefas_concluidas': u.tarefas_concluidas
        } for u in usuarios_stats]
    })
