"""
Rotas de Dashboard e Relatórios do Sistema GED

Endpoints:
- GET / - Dashboard principal
- GET /dashboard/stats - Estatísticas gerais
- GET /relatorio/tarefas_atrasadas - Relatório de tarefas atrasadas (PDF)
- GET /relatorio/documentos_vencendo - Relatório de documentos próximos ao vencimento (PDF)
- GET /relatorio/geral - Relatório geral do sistema (PDF)
"""

from flask import Blueprint, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func

from app.models import db, Usuario, Documento, Tarefa
from app.services.report_generator import (
    gerar_relatorio_tarefas_atrasadas,
    gerar_relatorio_documentos_vencendo,
    gerar_relatorio_geral
)

bp = Blueprint('dashboard', __name__)


@bp.route('/', methods=['GET'])
@login_required
def index():
    """
    Dashboard principal

    Para usuários comuns: mostra suas tarefas pendentes
    Para gerentes: mostra estatísticas do setor
    Para administradores: mostra estatísticas gerais
    """
    # Tarefas pendentes do usuário
    minhas_tarefas = Tarefa.query.filter_by(
        responsavel_id=current_user.id,
        concluida=False
    ).order_by(Tarefa.prazo.asc()).limit(10).all()

    response = {
        'usuario': {
            'nome': current_user.nome,
            'perfil': current_user.perfil,
            'setor': current_user.setor
        },
        'minhas_tarefas': [{
            'id': t.id,
            'tipo_tarefa': t.tipo_tarefa,
            'documento_titulo': t.documento.titulo,
            'prioridade': t.prioridade,
            'prazo': t.prazo.isoformat() if t.prazo else None,
            'esta_atrasada': t.esta_atrasada()
        } for t in minhas_tarefas]
    }

    # Estatísticas adicionais para gerentes e superior
    if current_user.is_gerente_ou_superior():
        # Documentos do setor
        query_docs = Documento.query
        if current_user.setor and not current_user.is_admin():
            query_docs = query_docs.filter_by(setor=current_user.setor)

        total_documentos = query_docs.count()
        docs_publicados = query_docs.filter_by(status='Aprovado e Publicado').count()
        docs_em_analise = query_docs.filter_by(status='Em Análise').count()

        # Documentos vencendo em 30 dias
        data_limite = datetime.utcnow() + timedelta(days=current_app.config['DIAS_ALERTA_VENCIMENTO'])
        docs_vencendo = query_docs.filter(
            Documento.data_vencimento != None,
            Documento.data_vencimento <= data_limite,
            Documento.data_vencimento > datetime.utcnow(),
            Documento.status == 'Aprovado e Publicado'
        ).count()

        # Tarefas atrasadas do setor
        query_tarefas = Tarefa.query.filter(
            Tarefa.concluida == False,
            Tarefa.prazo < datetime.utcnow()
        )

        if current_user.setor and not current_user.is_admin():
            query_tarefas = query_tarefas.join(Documento).filter(
                Documento.setor == current_user.setor
            )

        tarefas_atrasadas = query_tarefas.count()

        response['estatisticas'] = {
            'total_documentos': total_documentos,
            'documentos_publicados': docs_publicados,
            'documentos_em_analise': docs_em_analise,
            'documentos_vencendo_30_dias': docs_vencendo,
            'tarefas_atrasadas': tarefas_atrasadas
        }

    return jsonify(response)


@bp.route('/dashboard/stats', methods=['GET'])
@login_required
def estatisticas():
    """
    Estatísticas detalhadas do sistema
    Acesso baseado em perfil do usuário
    """
    stats = {}

    # Estatísticas do usuário
    stats['usuario'] = {
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

    # Estatísticas gerenciais
    if current_user.is_gerente_ou_superior():
        # Documentos por status
        docs_por_status = db.session.query(
            Documento.status,
            func.count(Documento.id).label('total')
        ).group_by(Documento.status).all()

        stats['documentos_por_status'] = {
            status: total for status, total in docs_por_status
        }

        # Documentos por tipo
        docs_por_tipo = db.session.query(
            Documento.tipo_documento,
            func.count(Documento.id).label('total')
        ).group_by(Documento.tipo_documento).all()

        stats['documentos_por_tipo'] = {
            tipo: total for tipo, total in docs_por_tipo if tipo
        }

        # Tarefas por tipo
        tarefas_por_tipo = db.session.query(
            Tarefa.tipo_tarefa,
            func.count(Tarefa.id).label('total')
        ).filter_by(concluida=False).group_by(Tarefa.tipo_tarefa).all()

        stats['tarefas_pendentes_por_tipo'] = {
            tipo: total for tipo, total in tarefas_por_tipo
        }

        # Documentos vencidos
        stats['documentos_vencidos'] = Documento.query.filter(
            Documento.data_vencimento != None,
            Documento.data_vencimento < datetime.utcnow(),
            Documento.status == 'Aprovado e Publicado'
        ).count()

    # Estatísticas administrativas
    if current_user.is_admin():
        stats['sistema'] = {
            'total_usuarios': Usuario.query.count(),
            'usuarios_ativos': Usuario.query.filter_by(ativo=True).count(),
            'total_documentos': Documento.query.count(),
            'total_tarefas': Tarefa.query.count()
        }

    return jsonify(stats)


@bp.route('/relatorio/preview/tarefas_atrasadas', methods=['GET'])
@login_required
def preview_tarefas_atrasadas():
    """
    Preview de tarefas atrasadas (JSON)
    Para gerentes e superior
    """
    if not current_user.is_gerente_ou_superior():
        return jsonify({'erro': 'Sem permissão para acessar relatórios'}), 403

    query = Tarefa.query.filter(
        Tarefa.concluida == False,
        Tarefa.prazo < datetime.utcnow()
    )

    # Filtro por setor para gerentes
    if current_user.setor and not current_user.is_admin():
        query = query.join(Documento).filter(Documento.setor == current_user.setor)

    tarefas = query.order_by(Tarefa.prazo.asc()).all()

    return jsonify({
        'titulo': 'Relatório de Tarefas Atrasadas',
        'data_geracao': datetime.utcnow().isoformat(),
        'total': len(tarefas),
        'tarefas': [{
            'id': t.id,
            'tipo_tarefa': t.tipo_tarefa,
            'documento_titulo': t.documento.titulo,
            'documento_codigo': t.documento.codigo_provisorio or t.documento.codigo_definitivo,
            'responsavel': t.responsavel.nome,
            'responsavel_email': t.responsavel.email,
            'prazo': t.prazo.isoformat(),
            'dias_atraso': abs(t.dias_ate_prazo()) if t.dias_ate_prazo() else 0,
            'prioridade': t.prioridade
        } for t in tarefas]
    })


@bp.route('/relatorio/preview/documentos_vencendo', methods=['GET'])
@login_required
def preview_documentos_vencendo():
    """
    Preview de documentos próximos ao vencimento (JSON)
    Para gerentes e superior
    """
    if not current_user.is_gerente_ou_superior():
        return jsonify({'erro': 'Sem permissão para acessar relatórios'}), 403

    dias = request.args.get('dias', current_app.config['DIAS_ALERTA_VENCIMENTO'], type=int)
    data_limite = datetime.utcnow() + timedelta(days=dias)

    query = Documento.query.filter(
        Documento.data_vencimento != None,
        Documento.data_vencimento <= data_limite,
        Documento.data_vencimento > datetime.utcnow(),
        Documento.status == 'Aprovado e Publicado'
    )

    # Filtro por setor
    if current_user.setor and not current_user.is_admin():
        query = query.filter_by(setor=current_user.setor)

    documentos = query.order_by(Documento.data_vencimento.asc()).all()

    return jsonify({
        'titulo': f'Relatório de Documentos Vencendo em {dias} Dias',
        'data_geracao': datetime.utcnow().isoformat(),
        'dias_limite': dias,
        'total': len(documentos),
        'documentos': [{
            'id': d.id,
            'titulo': d.titulo,
            'tipo_documento': d.tipo_documento,
            'codigo_definitivo': d.codigo_definitivo,
            'setor': d.setor,
            'data_publicacao': d.data_publicacao.isoformat() if d.data_publicacao else None,
            'data_vencimento': d.data_vencimento.isoformat() if d.data_vencimento else None,
            'dias_ate_vencimento': d.dias_ate_vencimento(),
            'criador': d.criador.nome
        } for d in documentos]
    })


@bp.route('/relatorio/preview/geral', methods=['GET'])
@login_required
def preview_relatorio_geral():
    """
    Preview de relatório geral do sistema (JSON)
    Apenas para administradores
    """
    if not current_user.is_admin():
        return jsonify({'erro': 'Apenas administradores podem acessar relatório geral'}), 403

    # Estatísticas gerais
    total_usuarios = Usuario.query.count()
    usuarios_ativos = Usuario.query.filter_by(ativo=True).count()
    total_documentos = Documento.query.count()
    total_tarefas = Tarefa.query.count()

    # Documentos por status
    docs_por_status = db.session.query(
        Documento.status,
        func.count(Documento.id).label('total')
    ).group_by(Documento.status).all()

    # Tarefas pendentes e atrasadas
    tarefas_pendentes = Tarefa.query.filter_by(concluida=False).count()
    tarefas_atrasadas = Tarefa.query.filter(
        Tarefa.concluida == False,
        Tarefa.prazo < datetime.utcnow()
    ).count()

    # Documentos vencidos e vencendo
    docs_vencidos = Documento.query.filter(
        Documento.data_vencimento != None,
        Documento.data_vencimento < datetime.utcnow()
    ).count()

    data_limite = datetime.utcnow() + timedelta(days=30)
    docs_vencendo = Documento.query.filter(
        Documento.data_vencimento != None,
        Documento.data_vencimento <= data_limite,
        Documento.data_vencimento > datetime.utcnow()
    ).count()

    # Documentos mais recentes
    docs_recentes = Documento.query.order_by(
        Documento.data_criacao.desc()
    ).limit(10).all()

    return jsonify({
        'titulo': 'Relatório Geral do Sistema GED',
        'data_geracao': datetime.utcnow().isoformat(),
        'usuarios': {
            'total': total_usuarios,
            'ativos': usuarios_ativos,
            'inativos': total_usuarios - usuarios_ativos
        },
        'documentos': {
            'total': total_documentos,
            'vencidos': docs_vencidos,
            'vencendo_30_dias': docs_vencendo,
            'por_status': {status: total for status, total in docs_por_status}
        },
        'tarefas': {
            'total': total_tarefas,
            'pendentes': tarefas_pendentes,
            'atrasadas': tarefas_atrasadas
        },
        'documentos_recentes': [{
            'id': d.id,
            'titulo': d.titulo,
            'tipo': d.tipo_documento,
            'status': d.status,
            'data_criacao': d.data_criacao.isoformat(),
            'criador': d.criador.nome
        } for d in docs_recentes]
    })


@bp.route('/rotina/verificar_vencimentos', methods=['POST'])
@login_required
def verificar_vencimentos():
    """
    Rotina para verificar e atualizar documentos vencidos
    Apenas para administradores

    Atualiza status de documentos vencidos para 'Obsoleto'
    """
    if not current_user.is_admin():
        return jsonify({'erro': 'Apenas administradores podem executar rotinas'}), 403

    agora = datetime.utcnow()

    # Busca documentos vencidos que ainda estão publicados
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

    return jsonify({
        'mensagem': 'Rotina de verificação de vencimentos executada',
        'total_documentos_atualizados': total_atualizados,
        'documentos_atualizados': [{
            'id': d.id,
            'titulo': d.titulo,
            'codigo_definitivo': d.codigo_definitivo,
            'data_vencimento': d.data_vencimento.isoformat()
        } for d in documentos_vencidos]
    })


@bp.route('/search', methods=['GET'])
@login_required
def buscar():
    """
    Busca global de documentos

    Query params:
        - q: Termo de busca
        - tipo: Tipo de documento
        - status: Status do documento
        - setor: Setor
    """
    q = request.args.get('q', '').strip()

    if not q:
        return jsonify({'erro': 'Parâmetro "q" é obrigatório'}), 400

    query = Documento.query

    # Filtro de acesso
    if not current_user.is_admin():
        if current_user.perfil == 'comum':
            query = query.filter_by(criador_id=current_user.id)
        elif current_user.setor:
            query = query.filter_by(setor=current_user.setor)

    # FIX: SQL Injection - sanitiza input antes de usar em ILIKE
    q_safe = sanitize_like_pattern(q)
    query = query.filter(
        (Documento.titulo.ilike(f'%{q_safe}%')) |
        (Documento.codigo_provisorio.ilike(f'%{q_safe}%')) |
        (Documento.codigo_definitivo.ilike(f'%{q_safe}%')) |
        (Documento.descricao.ilike(f'%{q_safe}%'))
    )

    # Filtros adicionais
    tipo = request.args.get('tipo')
    if tipo:
        query = query.filter_by(tipo_documento=tipo)

    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)

    setor = request.args.get('setor')
    if setor:
        query = query.filter_by(setor=setor)

    # Limita resultados
    documentos = query.order_by(Documento.data_criacao.desc()).limit(50).all()

    return jsonify({
        'total': len(documentos),
        'resultados': [{
            'id': d.id,
            'titulo': d.titulo,
            'tipo_documento': d.tipo_documento,
            'codigo': d.codigo_provisorio or d.codigo_definitivo,
            'status': d.status,
            'setor': d.setor,
            'data_criacao': d.data_criacao.isoformat(),
            'criador': d.criador.nome
        } for d in documentos]
    })


@bp.route('/relatorio/pdf/tarefas_atrasadas', methods=['GET'])
@login_required
def relatorio_pdf_tarefas_atrasadas():
    """
    Gera relatório PDF de tarefas atrasadas
    Para gerentes e superior
    """
    if not current_user.is_gerente_ou_superior():
        return jsonify({'erro': 'Sem permissão para gerar relatórios'}), 403

    query = Tarefa.query.filter(
        Tarefa.concluida == False,
        Tarefa.prazo < datetime.utcnow()
    )

    # Filtro por setor para gerentes
    if current_user.setor and not current_user.is_admin():
        query = query.join(Documento).filter(Documento.setor == current_user.setor)

    tarefas = query.order_by(Tarefa.prazo.asc()).all()

    tarefas_data = [{
        'id': t.id,
        'tipo_tarefa': t.tipo_tarefa,
        'documento_titulo': t.documento.titulo,
        'responsavel': t.responsavel.nome,
        'prazo': t.prazo.isoformat(),
        'dias_atraso': abs(t.dias_ate_prazo()) if t.dias_ate_prazo() else 0,
        'prioridade': t.prioridade
    } for t in tarefas]

    # Gera PDF
    pdf_buffer = gerar_relatorio_tarefas_atrasadas(tarefas_data, current_user.nome)

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'relatorio_tarefas_atrasadas_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.pdf'
    )


@bp.route('/relatorio/pdf/documentos_vencendo', methods=['GET'])
@login_required
def relatorio_pdf_documentos_vencendo():
    """
    Gera relatório PDF de documentos próximos ao vencimento
    Para gerentes e superior
    """
    if not current_user.is_gerente_ou_superior():
        return jsonify({'erro': 'Sem permissão para gerar relatórios'}), 403

    dias = request.args.get('dias', current_app.config['DIAS_ALERTA_VENCIMENTO'], type=int)
    data_limite = datetime.utcnow() + timedelta(days=dias)

    query = Documento.query.filter(
        Documento.data_vencimento != None,
        Documento.data_vencimento <= data_limite,
        Documento.data_vencimento > datetime.utcnow(),
        Documento.status == 'Aprovado e Publicado'
    )

    # Filtro por setor
    if current_user.setor and not current_user.is_admin():
        query = query.filter_by(setor=current_user.setor)

    documentos = query.order_by(Documento.data_vencimento.asc()).all()

    docs_data = [{
        'id': d.id,
        'titulo': d.titulo,
        'tipo_documento': d.tipo_documento,
        'codigo_definitivo': d.codigo_definitivo,
        'setor': d.setor,
        'data_publicacao': d.data_publicacao.isoformat() if d.data_publicacao else None,
        'data_vencimento': d.data_vencimento.isoformat() if d.data_vencimento else None,
        'dias_ate_vencimento': d.dias_ate_vencimento()
    } for d in documentos]

    # Gera PDF
    pdf_buffer = gerar_relatorio_documentos_vencendo(docs_data, dias, current_user.nome)

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'relatorio_documentos_vencendo_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.pdf'
    )


@bp.route('/relatorio/pdf/geral', methods=['GET'])
@login_required
def relatorio_pdf_geral():
    """
    Gera relatório geral do sistema em PDF
    Apenas para administradores
    """
    if not current_user.is_admin():
        return jsonify({'erro': 'Apenas administradores podem gerar relatório geral'}), 403

    # Coleta dados (mesmo código do preview)
    total_usuarios = Usuario.query.count()
    usuarios_ativos = Usuario.query.filter_by(ativo=True).count()
    total_documentos = Documento.query.count()
    total_tarefas = Tarefa.query.count()

    docs_por_status = db.session.query(
        Documento.status,
        func.count(Documento.id).label('total')
    ).group_by(Documento.status).all()

    tarefas_pendentes = Tarefa.query.filter_by(concluida=False).count()
    tarefas_atrasadas = Tarefa.query.filter(
        Tarefa.concluida == False,
        Tarefa.prazo < datetime.utcnow()
    ).count()

    docs_vencidos = Documento.query.filter(
        Documento.data_vencimento != None,
        Documento.data_vencimento < datetime.utcnow()
    ).count()

    data_limite = datetime.utcnow() + timedelta(days=30)
    docs_vencendo = Documento.query.filter(
        Documento.data_vencimento != None,
        Documento.data_vencimento <= data_limite,
        Documento.data_vencimento > datetime.utcnow()
    ).count()

    docs_recentes = Documento.query.order_by(
        Documento.data_criacao.desc()
    ).limit(10).all()

    dados = {
        'usuarios': {
            'total': total_usuarios,
            'ativos': usuarios_ativos,
            'inativos': total_usuarios - usuarios_ativos
        },
        'documentos': {
            'total': total_documentos,
            'vencidos': docs_vencidos,
            'vencendo_30_dias': docs_vencendo,
            'por_status': {status: total for status, total in docs_por_status}
        },
        'tarefas': {
            'total': total_tarefas,
            'pendentes': tarefas_pendentes,
            'atrasadas': tarefas_atrasadas
        },
        'documentos_recentes': [{
            'id': d.id,
            'titulo': d.titulo,
            'tipo': d.tipo_documento,
            'status': d.status,
            'data_criacao': d.data_criacao.isoformat(),
            'criador': d.criador.nome
        } for d in docs_recentes]
    }

    # Gera PDF
    pdf_buffer = gerar_relatorio_geral(dados, current_user.nome)

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'relatorio_geral_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.pdf'
    )
