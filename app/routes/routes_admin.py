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

# Valores padrão para garantir compatibilidade
ABRANGENCIAS_DEFAULT = ['CHUFC', 'HUWC', 'MEAC']
TIPOS_DOCUMENTO_DEFAULT = ['POP', 'Manual', 'Protocolo', 'Política', 'Regimento', 'Regulamento']
TIPOS_VALIDADE_4_ANOS_DEFAULT = ['Política', 'Regimento', 'Regulamento']
SETORES_DEFAULT = {
    'CHUFC': ['Administração', 'Qualidade', 'Tecnologia da Informação', 'Gestão de Pessoas'],
    'HUWC': ['Administração', 'Enfermagem', 'Farmácia', 'Laboratório', 'UTI'],
    'MEAC': ['Administração', 'Enfermagem', 'Neonatologia', 'Obstetrícia']
}


def get_abrangencias():
    """Retorna lista de abrangências (com fallback)"""
    return getattr(Config, 'ABRANGENCIAS', ABRANGENCIAS_DEFAULT)


def get_tipos_documento():
    """Retorna tipos de documento (com fallback)"""
    return getattr(Config, 'TIPOS_DOCUMENTO', TIPOS_DOCUMENTO_DEFAULT)


def get_tipos_validade_4_anos():
    """Retorna tipos com validade de 4 anos (com fallback)"""
    return getattr(Config, 'TIPOS_VALIDADE_4_ANOS', TIPOS_VALIDADE_4_ANOS_DEFAULT)


def get_setores_por_abrangencia(abrangencia):
    """Retorna setores de uma abrangência (com fallback)"""
    if hasattr(Config, 'get_setores_por_abrangencia'):
        return Config.get_setores_por_abrangencia(abrangencia)
    elif hasattr(Config, 'SETORES_POR_ABRANGENCIA'):
        return Config.SETORES_POR_ABRANGENCIA.get(abrangencia, [])
    return SETORES_DEFAULT.get(abrangencia, [])


def get_all_setores():
    """Retorna todos os setores com suas abrangências"""
    if hasattr(Config, 'SETORES_POR_ABRANGENCIA'):
        setores_dict = Config.SETORES_POR_ABRANGENCIA
    else:
        setores_dict = SETORES_DEFAULT

    todos = []
    for abrang, setores in setores_dict.items():
        for setor in setores:
            todos.append({'setor': setor, 'abrangencia': abrang})
    return sorted(todos, key=lambda x: (x['setor'], x['abrangencia']))


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
# PÁGINA ÚNICA DE CONFIGURAÇÕES
# ============================================================================

@admin_bp.route('/configuracoes')
@login_required
@admin_required
def configuracoes():
    """Página unificada de configurações do sistema"""
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

    # Dados de abrangências
    abrangencias_info = []
    for abrang in get_abrangencias():
        setores = get_setores_por_abrangencia(abrang)
        docs_count = Documento.query.filter_by(abrangencia=abrang).count()
        abrangencias_info.append({
            'nome': abrang,
            'setores': setores,
            'total_setores': len(setores),
            'total_documentos': docs_count,
        })

    # Dados de tipos de documento
    tipos_info = []
    tipos_validade_4 = get_tipos_validade_4_anos()
    for tipo in get_tipos_documento():
        count = Documento.query.filter_by(tipo_documento=tipo).count()
        validade = 4 if tipo in tipos_validade_4 else 2
        tipos_info.append({
            'nome': tipo,
            'total': count,
            'validade_anos': validade
        })

    # Dados de setores
    setores_info = []
    for abrang in get_abrangencias():
        for setor in get_setores_por_abrangencia(abrang):
            docs_count = Documento.query.filter_by(setor=setor, abrangencia=abrang).count()
            users_count = Usuario.query.filter_by(setor=setor).count()
            setores_info.append({
                'nome': setor,
                'abrangencia': abrang,
                'total_documentos': docs_count,
                'total_usuarios': users_count
            })
    setores_info.sort(key=lambda x: (x['abrangencia'], x['nome']))

    # Dados de permissões
    perfis = [
        {
            'nome': 'comum',
            'descricao': 'Usuário comum',
            'permissoes': ['Criar documentos', 'Executar tarefas', 'Ver repositório']
        },
        {
            'nome': 'gerente',
            'descricao': 'Gerente de setor',
            'permissoes': ['Tudo de comum', 'Aprovar documentos', 'Usar IA']
        },
        {
            'nome': 'qualidade_triador',
            'descricao': 'Triador UGQ',
            'permissoes': ['Triagem', 'Verificar duplicidade', 'Devolver documentos']
        },
        {
            'nome': 'qualidade_validador',
            'descricao': 'Validador UGQ',
            'permissoes': ['Validar', 'Codificar', 'Criar blocos', 'Publicar']
        },
        {
            'nome': 'administrador',
            'descricao': 'Administrador',
            'permissoes': ['Acesso total', 'Gerenciar usuários', 'Configurações']
        }
    ]
    for perfil in perfis:
        perfil['total_usuarios'] = Usuario.query.filter_by(perfil=perfil['nome']).count()

    # Usuários
    usuarios = Usuario.query.order_by(Usuario.nome).all()

    return render_template('admin/configuracoes.html',
                          stats=stats,
                          abrangencias=abrangencias_info,
                          tipos=tipos_info,
                          setores=setores_info,
                          perfis=perfis,
                          usuarios=usuarios,
                          abrangencias_list=get_abrangencias())


# ============================================================================
# PAINEL PRINCIPAL DE ADMINISTRAÇÃO (redireciona para configurações)
# ============================================================================

@admin_bp.route('/')
@login_required
@admin_required
def painel():
    """Redireciona para página de configurações"""
    return redirect(url_for('admin.configuracoes'))


# ============================================================================
# GESTÃO DE ABRANGÊNCIAS
# ============================================================================

@admin_bp.route('/abrangencias')
@login_required
@admin_required
def abrangencias():
    """Gestão de abrangências"""
    abrangencias_info = []
    for abrang in get_abrangencias():
        setores = get_setores_por_abrangencia(abrang)
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
    tipos_validade_4 = get_tipos_validade_4_anos()
    for tipo in get_tipos_documento():
        count = Documento.query.filter_by(tipo_documento=tipo).count()
        publicados = Documento.query.filter_by(tipo_documento=tipo, status='Publicado').count()
        validade = 4 if tipo in tipos_validade_4 else 2
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

    for abrang in get_abrangencias():
        for setor in get_setores_por_abrangencia(abrang):
            docs_count = Documento.query.filter_by(setor=setor, abrangencia=abrang).count()
            users_count = Usuario.query.filter_by(setor=setor).count()
            setores_info.append({
                'nome': setor,
                'abrangencia': abrang,
                'total_documentos': docs_count,
                'total_usuarios': users_count
            })

    setores_info.sort(key=lambda x: (x['abrangencia'], x['nome']))

    return render_template('admin/setores.html', setores=setores_info, abrangencias=get_abrangencias())


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
                          abrangencias=get_abrangencias(),
                          tipos=get_tipos_documento())


# ============================================================================
# APIs DE ADMINISTRAÇÃO
# ============================================================================

@admin_bp.route('/api/setores')
@login_required
def api_setores():
    """API para obter setores por abrangência"""
    abrangencia = request.args.get('abrangencia', 'CHUFC')
    setores = get_setores_por_abrangencia(abrangencia)
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
    abrangencias = get_abrangencias()
    setores_dict = {}
    for abrang in abrangencias:
        setores_dict[abrang] = get_setores_por_abrangencia(abrang)

    return jsonify({
        'abrangencias': abrangencias,
        'setores_por_abrangencia': setores_dict
    })


@admin_bp.route('/api/tipos-documento')
@login_required
def api_tipos_documento():
    """API para obter tipos de documento"""
    tipos = []
    tipos_validade_4 = get_tipos_validade_4_anos()
    for tipo in get_tipos_documento():
        tipos.append({
            'nome': tipo,
            'validade_anos': 4 if tipo in tipos_validade_4 else 2
        })
    return jsonify({'tipos': tipos})
