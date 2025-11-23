"""
Routes ADMIN - Rotas para administração do sistema
Painel de controle completo para administradores
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import logging

from app import db
from app.models.models import Usuario, Documento, Tarefa, ListaMestra
from config import Config

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Decorator para exigir perfil de administrador"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Acesso negado. Apenas administradores podem acessar esta área.', 'danger')
            return redirect(url_for('view.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# PAINEL PRINCIPAL DE ADMINISTRAÇÃO
# ============================================================================

@admin_bp.route('/')
@login_required
@admin_required
def painel():
    """Painel principal de administração"""
    # Estatísticas gerais
    stats = {
        'total_usuarios': Usuario.query.count(),
        'usuarios_ativos': Usuario.query.filter_by(ativo=True).count(),
        'total_documentos': Documento.query.count(),
        'documentos_publicados': Documento.query.filter_by(status='Publicado').count(),
        'documentos_em_fluxo': Documento.query.filter(Documento.status.notin_(['Publicado', 'Cancelado', 'Obsoleto'])).count(),
        'tarefas_pendentes': Tarefa.query.filter_by(concluida=False).count(),
    }

    # Contagem por perfil
    perfis_count = db.session.query(
        Usuario.perfil, db.func.count(Usuario.id)
    ).group_by(Usuario.perfil).all()
    stats['perfis'] = dict(perfis_count)

    # Contagem por status de documento
    status_count = db.session.query(
        Documento.status, db.func.count(Documento.id)
    ).group_by(Documento.status).all()
    stats['status_documentos'] = dict(status_count)

    # Contagem por abrangência
    abrangencia_count = db.session.query(
        Documento.abrangencia, db.func.count(Documento.id)
    ).filter(Documento.abrangencia != None).group_by(Documento.abrangencia).all()
    stats['abrangencias'] = dict(abrangencia_count)

    return render_template('admin/painel.html', stats=stats)


# ============================================================================
# GESTÃO DE ABRANGÊNCIAS
# ============================================================================

@admin_bp.route('/abrangencias')
@login_required
@admin_required
def abrangencias():
    """Gestão de abrangências"""
    abrangencias_info = []
    for abrang in Config.ABRANGENCIAS:
        setores = Config.get_setores_por_abrangencia(abrang)
        docs_count = Documento.query.filter_by(abrangencia=abrang).count()
        docs_publicados = Documento.query.filter_by(abrangencia=abrang, status='Publicado').count()
        abrangencias_info.append({
            'nome': abrang,
            'setores': setores,
            'total_setores': len(setores),
            'total_documentos': docs_count,
            'docs_publicados': docs_publicados
        })

    return render_template('admin/abrangencias.html', abrangencias=abrangencias_info)


# ============================================================================
# GESTÃO DE TIPOS DE DOCUMENTO
# ============================================================================

@admin_bp.route('/tipos-documento')
@login_required
@admin_required
def tipos_documento():
    """Gestão de tipos de documento"""
    tipos_info = []
    for tipo in Config.TIPOS_DOCUMENTO:
        count = Documento.query.filter_by(tipo_documento=tipo).count()
        publicados = Documento.query.filter_by(tipo_documento=tipo, status='Publicado').count()
        validade = 4 if tipo in Config.TIPOS_VALIDADE_4_ANOS else 2
        tipos_info.append({
            'nome': tipo,
            'total': count,
            'publicados': publicados,
            'validade_anos': validade
        })

    return render_template('admin/tipos_documento.html', tipos=tipos_info)


# ============================================================================
# GESTÃO DE SETORES
# ============================================================================

@admin_bp.route('/setores')
@login_required
@admin_required
def setores():
    """Gestão de setores"""
    setores_info = []

    for abrang, setores_list in Config.SETORES_POR_ABRANGENCIA.items():
        for setor in setores_list:
            docs_count = Documento.query.filter_by(setor=setor, abrangencia=abrang).count()
            users_count = Usuario.query.filter_by(setor=setor).count()
            setores_info.append({
                'nome': setor,
                'abrangencia': abrang,
                'total_documentos': docs_count,
                'total_usuarios': users_count
            })

    # Ordena por abrangência e nome
    setores_info.sort(key=lambda x: (x['abrangencia'], x['nome']))

    return render_template('admin/setores.html', setores=setores_info, abrangencias=Config.ABRANGENCIAS)


# ============================================================================
# GESTÃO DE PERMISSÕES
# ============================================================================

@admin_bp.route('/permissoes')
@login_required
@admin_required
def permissoes():
    """Gestão de permissões por perfil"""
    perfis = [
        {
            'nome': 'comum',
            'descricao': 'Usuário comum - Cria documentos e executa tarefas atribuídas',
            'permissoes': [
                'Criar documentos',
                'Editar próprios documentos (se em status inicial)',
                'Executar tarefas atribuídas',
                'Visualizar documentos publicados',
                'Acessar repositório público'
            ]
        },
        {
            'nome': 'gerente',
            'descricao': 'Gerente - Gerencia documentos e equipe do setor',
            'permissoes': [
                'Todas permissões de comum',
                'Aprovar documentos como assinante',
                'Visualizar tarefas do setor',
                'Usar funções de IA',
                'Criar tarefas para equipe'
            ]
        },
        {
            'nome': 'qualidade_triador',
            'descricao': 'Triador UGQ - Faz triagem inicial de documentos',
            'permissoes': [
                'Receber documentos para triagem',
                'Verificar duplicidade na Lista Mestra',
                'Verificar formatação EBSERH',
                'Aprovar ou devolver documentos',
                'Editar documentos em triagem',
                'Definir abrangência de documentos'
            ]
        },
        {
            'nome': 'qualidade_validador',
            'descricao': 'Validador UGQ - Valida, codifica e publica documentos',
            'permissoes': [
                'Receber documentos triados',
                'Codificar documentos (código definitivo)',
                'Criar blocos de assinatura',
                'Gerenciar aprovadores',
                'Publicar documentos aprovados',
                'Editar documentos em validação',
                'Alterar status de documentos',
                'Definir abrangência e setor'
            ]
        },
        {
            'nome': 'responsavel_interno',
            'descricao': 'Responsável Interno - Gerencia fluxos específicos',
            'permissoes': [
                'Todas permissões de gerente',
                'Gerenciar fluxos de documentos específicos',
                'Aprovar documentos como responsável'
            ]
        },
        {
            'nome': 'administrador',
            'descricao': 'Administrador - Controle total do sistema',
            'permissoes': [
                'Todas as permissões do sistema',
                'Gerenciar usuários',
                'Gerenciar configurações',
                'Alterar qualquer documento',
                'Acessar painel administrativo',
                'Excluir documentos e usuários',
                'Configurar WhatsApp',
                'Visualizar logs e auditoria'
            ]
        }
    ]

    # Conta usuários por perfil
    for perfil in perfis:
        perfil['total_usuarios'] = Usuario.query.filter_by(perfil=perfil['nome']).count()

    return render_template('admin/permissoes.html', perfis=perfis)


# ============================================================================
# LISTA MESTRA
# ============================================================================

@admin_bp.route('/lista-mestra')
@login_required
@admin_required
def lista_mestra():
    """Visualização da Lista Mestra de documentos"""
    page = request.args.get('page', 1, type=int)
    per_page = 50

    # Filtros
    abrangencia = request.args.get('abrangencia')
    tipo = request.args.get('tipo')
    setor = request.args.get('setor')
    status = request.args.get('status')

    query = ListaMestra.query

    if abrangencia:
        query = query.filter_by(abrangencia=abrangencia)
    if tipo:
        query = query.filter_by(tipo=tipo)
    if setor:
        query = query.filter_by(setor=setor)
    if status:
        query = query.filter_by(status=status)

    registros = query.order_by(ListaMestra.codigo).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('admin/lista_mestra.html',
                          registros=registros,
                          abrangencias=Config.ABRANGENCIAS,
                          tipos=Config.TIPOS_DOCUMENTO)


# ============================================================================
# APIs DE ADMINISTRAÇÃO
# ============================================================================

@admin_bp.route('/api/setores')
@login_required
def api_setores():
    """API para obter setores por abrangência"""
    abrangencia = request.args.get('abrangencia', 'CHUFC')
    setores = Config.get_setores_por_abrangencia(abrangencia)
    return jsonify({'setores': setores, 'abrangencia': abrangencia})


@admin_bp.route('/api/stats')
@login_required
@admin_required
def api_stats():
    """API para estatísticas do sistema"""
    stats = {
        'usuarios': {
            'total': Usuario.query.count(),
            'ativos': Usuario.query.filter_by(ativo=True).count(),
        },
        'documentos': {
            'total': Documento.query.count(),
            'publicados': Documento.query.filter_by(status='Publicado').count(),
            'em_fluxo': Documento.query.filter(Documento.status.notin_(['Publicado', 'Cancelado', 'Obsoleto'])).count(),
        },
        'tarefas': {
            'pendentes': Tarefa.query.filter_by(concluida=False).count(),
            'concluidas_mes': Tarefa.query.filter(
                Tarefa.concluida == True,
                Tarefa.data_conclusao >= datetime.utcnow().replace(day=1)
            ).count(),
        }
    }
    return jsonify(stats)


@admin_bp.route('/api/abrangencias')
@login_required
def api_abrangencias():
    """API para obter abrangências disponíveis"""
    return jsonify({
        'abrangencias': Config.ABRANGENCIAS,
        'setores_por_abrangencia': Config.SETORES_POR_ABRANGENCIA
    })


@admin_bp.route('/api/tipos-documento')
@login_required
def api_tipos_documento():
    """API para obter tipos de documento"""
    tipos = []
    for tipo in Config.TIPOS_DOCUMENTO:
        tipos.append({
            'nome': tipo,
            'validade_anos': 4 if tipo in Config.TIPOS_VALIDADE_4_ANOS else 2
        })
    return jsonify({'tipos': tipos})


# Rota alternativa para compatibilidade com o template de edição
@admin_bp.route('/setores', methods=['GET'])
@login_required
def api_setores_alt():
    """API alternativa para setores (rota /api/admin/setores)"""
    abrangencia = request.args.get('abrangencia', 'CHUFC')
    setores = Config.get_setores_por_abrangencia(abrangencia)
    return jsonify({'setores': setores, 'abrangencia': abrangencia})
