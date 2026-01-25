"""
Routes ADMIN - Rotas para administração do sistema
Painel de controle completo para administradores
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import logging
import json

from app import db
from app.models.models import (
    Usuario, Documento, Tarefa, ListaMestra,
    Abrangencia, TipoDocumento, Setor, PerfilPermissao,
    ConfiguracaoSistema, ConfiguracaoWhatsApp
)

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
# PÁGINA PRINCIPAL DE CONFIGURAÇÕES
# ============================================================================

@admin_bp.route('/')
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

    # Dados do banco
    abrangencias = Abrangencia.query.order_by(Abrangencia.ordem).all()
    tipos = TipoDocumento.query.order_by(TipoDocumento.ordem).all()
    setores = Setor.query.order_by(Setor.nome).all()
    perfis = PerfilPermissao.query.order_by(PerfilPermissao.codigo).all()
    usuarios = Usuario.query.order_by(Usuario.nome).all()

    return render_template('admin/configuracoes.html',
                          stats=stats,
                          abrangencias=abrangencias,
                          tipos=tipos,
                          setores=setores,
                          perfis=perfis,
                          usuarios=usuarios)


# ============================================================================
# CRUD - ABRANGÊNCIAS
# ============================================================================

@admin_bp.route('/abrangencia/criar', methods=['POST'])
@login_required
@admin_required
def abrangencia_criar():
    """Criar nova abrangência"""
    codigo = request.form.get('codigo', '').upper().strip()
    nome = request.form.get('nome', '').strip()
    descricao = request.form.get('descricao', '').strip()
    cor = request.form.get('cor', '#2563eb')
    icone = request.form.get('icone', 'bi-building')

    if not codigo or not nome:
        flash('Código e nome são obrigatórios', 'danger')
        return redirect(url_for('admin.configuracoes'))

    # Verifica se já existe
    if Abrangencia.query.filter_by(codigo=codigo).first():
        flash(f'Abrangência {codigo} já existe', 'danger')
        return redirect(url_for('admin.configuracoes'))

    # Calcula ordem
    max_ordem = db.session.query(db.func.max(Abrangencia.ordem)).scalar() or 0

    abrangencia = Abrangencia(
        codigo=codigo,
        nome=nome,
        descricao=descricao,
        cor=cor,
        icone=icone,
        ordem=max_ordem + 1
    )
    db.session.add(abrangencia)
    db.session.commit()

    flash(f'Abrangência {codigo} criada com sucesso!', 'success')
    return redirect(url_for('admin.configuracoes'))


@admin_bp.route('/abrangencia/<int:id>/editar', methods=['POST'])
@login_required
@admin_required
def abrangencia_editar(id):
    """Editar abrangência"""
    abrangencia = Abrangencia.query.get_or_404(id)

    abrangencia.codigo = request.form.get('codigo', abrangencia.codigo).upper().strip()
    abrangencia.nome = request.form.get('nome', abrangencia.nome).strip()
    abrangencia.descricao = request.form.get('descricao', '').strip()
    abrangencia.cor = request.form.get('cor', abrangencia.cor)
    abrangencia.icone = request.form.get('icone', abrangencia.icone)
    abrangencia.ativo = request.form.get('ativo') == 'on'

    db.session.commit()
    flash(f'Abrangência {abrangencia.codigo} atualizada!', 'success')
    return redirect(url_for('admin.configuracoes'))


@admin_bp.route('/abrangencia/<int:id>/excluir', methods=['POST'])
@login_required
@admin_required
def abrangencia_excluir(id):
    """Excluir abrangência"""
    abrangencia = Abrangencia.query.get_or_404(id)

    # Verifica se tem setores vinculados
    if abrangencia.setores.count() > 0:
        flash(f'Não é possível excluir. Existem {abrangencia.setores.count()} setores vinculados.', 'danger')
        return redirect(url_for('admin.configuracoes'))

    db.session.delete(abrangencia)
    db.session.commit()
    flash('Abrangência excluída!', 'success')
    return redirect(url_for('admin.configuracoes'))


# ============================================================================
# CRUD - TIPOS DE DOCUMENTO
# ============================================================================

@admin_bp.route('/tipo-documento/criar', methods=['POST'])
@login_required
@admin_required
def tipo_documento_criar():
    """Criar novo tipo de documento"""
    codigo = request.form.get('codigo', '').upper().strip()
    nome = request.form.get('nome', '').strip()
    descricao = request.form.get('descricao', '').strip()
    validade_anos = request.form.get('validade_anos', 2, type=int)
    prefixo_codigo = request.form.get('prefixo_codigo', '').upper().strip()

    if not codigo or not nome:
        flash('Código e nome são obrigatórios', 'danger')
        return redirect(url_for('admin.configuracoes'))

    if TipoDocumento.query.filter_by(codigo=codigo).first():
        flash(f'Tipo {codigo} já existe', 'danger')
        return redirect(url_for('admin.configuracoes'))

    max_ordem = db.session.query(db.func.max(TipoDocumento.ordem)).scalar() or 0

    tipo = TipoDocumento(
        codigo=codigo,
        nome=nome,
        descricao=descricao,
        validade_anos=validade_anos,
        prefixo_codigo=prefixo_codigo or codigo[:3],
        ordem=max_ordem + 1
    )
    db.session.add(tipo)
    db.session.commit()

    flash(f'Tipo {codigo} criado com sucesso!', 'success')
    return redirect(url_for('admin.configuracoes'))


@admin_bp.route('/tipo-documento/<int:id>/editar', methods=['POST'])
@login_required
@admin_required
def tipo_documento_editar(id):
    """Editar tipo de documento"""
    tipo = TipoDocumento.query.get_or_404(id)

    tipo.codigo = request.form.get('codigo', tipo.codigo).upper().strip()
    tipo.nome = request.form.get('nome', tipo.nome).strip()
    tipo.descricao = request.form.get('descricao', '').strip()
    tipo.validade_anos = request.form.get('validade_anos', tipo.validade_anos, type=int)
    tipo.prefixo_codigo = request.form.get('prefixo_codigo', tipo.prefixo_codigo).upper().strip()
    tipo.ativo = request.form.get('ativo') == 'on'

    db.session.commit()
    flash(f'Tipo {tipo.codigo} atualizado!', 'success')
    return redirect(url_for('admin.configuracoes'))


@admin_bp.route('/tipo-documento/<int:id>/excluir', methods=['POST'])
@login_required
@admin_required
def tipo_documento_excluir(id):
    """Excluir tipo de documento"""
    tipo = TipoDocumento.query.get_or_404(id)
    db.session.delete(tipo)
    db.session.commit()
    flash('Tipo de documento excluído!', 'success')
    return redirect(url_for('admin.configuracoes'))


# ============================================================================
# CRUD - SETORES
# ============================================================================

@admin_bp.route('/setor/criar', methods=['POST'])
@login_required
@admin_required
def setor_criar():
    """Criar novo setor"""
    nome = request.form.get('nome', '').strip()
    abrangencia_id = request.form.get('abrangencia_id', type=int)
    descricao = request.form.get('descricao', '').strip()
    sigla = request.form.get('sigla', '').upper().strip()
    responsavel = request.form.get('responsavel', '').strip()
    email = request.form.get('email', '').strip()
    telefone = request.form.get('telefone', '').strip()

    if not nome or not abrangencia_id:
        flash('Nome e abrangência são obrigatórios', 'danger')
        return redirect(url_for('admin.configuracoes'))

    setor = Setor(
        nome=nome,
        abrangencia_id=abrangencia_id,
        descricao=descricao,
        sigla=sigla,
        responsavel=responsavel,
        email=email,
        telefone=telefone
    )
    db.session.add(setor)
    db.session.commit()

    flash(f'Setor {nome} criado com sucesso!', 'success')
    return redirect(url_for('admin.configuracoes'))


@admin_bp.route('/setor/<int:id>/editar', methods=['POST'])
@login_required
@admin_required
def setor_editar(id):
    """Editar setor"""
    setor = Setor.query.get_or_404(id)

    setor.nome = request.form.get('nome', setor.nome).strip()
    setor.abrangencia_id = request.form.get('abrangencia_id', setor.abrangencia_id, type=int)
    setor.descricao = request.form.get('descricao', '').strip()
    setor.sigla = request.form.get('sigla', '').upper().strip()
    setor.responsavel = request.form.get('responsavel', '').strip()
    setor.email = request.form.get('email', '').strip()
    setor.telefone = request.form.get('telefone', '').strip()
    setor.ativo = request.form.get('ativo') == 'on'

    db.session.commit()
    flash(f'Setor {setor.nome} atualizado!', 'success')
    return redirect(url_for('admin.configuracoes'))


@admin_bp.route('/setor/<int:id>/excluir', methods=['POST'])
@login_required
@admin_required
def setor_excluir(id):
    """Excluir setor"""
    setor = Setor.query.get_or_404(id)
    db.session.delete(setor)
    db.session.commit()
    flash('Setor excluído!', 'success')
    return redirect(url_for('admin.configuracoes'))


# ============================================================================
# CRUD - PERFIS/PERMISSÕES
# ============================================================================

@admin_bp.route('/perfil/criar', methods=['POST'])
@login_required
@admin_required
def perfil_criar():
    """Criar novo perfil"""
    codigo = request.form.get('codigo', '').lower().strip()
    nome = request.form.get('nome', '').strip()
    descricao = request.form.get('descricao', '').strip()
    cor = request.form.get('cor', '#6b7280')
    permissoes = request.form.getlist('permissoes')

    if not codigo or not nome:
        flash('Código e nome são obrigatórios', 'danger')
        return redirect(url_for('admin.configuracoes'))

    if PerfilPermissao.query.filter_by(codigo=codigo).first():
        flash(f'Perfil {codigo} já existe', 'danger')
        return redirect(url_for('admin.configuracoes'))

    perfil = PerfilPermissao(
        codigo=codigo,
        nome=nome,
        descricao=descricao,
        cor=cor
    )
    perfil.set_permissoes(permissoes)
    db.session.add(perfil)
    db.session.commit()

    flash(f'Perfil {nome} criado com sucesso!', 'success')
    return redirect(url_for('admin.configuracoes'))


@admin_bp.route('/perfil/<int:id>/editar', methods=['POST'])
@login_required
@admin_required
def perfil_editar(id):
    """Editar perfil"""
    perfil = PerfilPermissao.query.get_or_404(id)

    perfil.codigo = request.form.get('codigo', perfil.codigo).lower().strip()
    perfil.nome = request.form.get('nome', perfil.nome).strip()
    perfil.descricao = request.form.get('descricao', '').strip()
    perfil.cor = request.form.get('cor', perfil.cor)
    perfil.ativo = request.form.get('ativo') == 'on'

    permissoes = request.form.getlist('permissoes')
    perfil.set_permissoes(permissoes)

    db.session.commit()
    flash(f'Perfil {perfil.nome} atualizado!', 'success')
    return redirect(url_for('admin.configuracoes'))


@admin_bp.route('/perfil/<int:id>/excluir', methods=['POST'])
@login_required
@admin_required
def perfil_excluir(id):
    """Excluir perfil"""
    perfil = PerfilPermissao.query.get_or_404(id)
    db.session.delete(perfil)
    db.session.commit()
    flash('Perfil excluído!', 'success')
    return redirect(url_for('admin.configuracoes'))


# ============================================================================
# INICIALIZAR DADOS PADRÃO
# ============================================================================

@admin_bp.route('/inicializar-dados', methods=['GET', 'POST'])
@login_required
@admin_required
def inicializar_dados():
    """Inicializa dados padrão no banco (GET ou POST)"""
    try:
        # Abrangências padrão
        abrangencias_padrao = [
            {'codigo': 'CHUFC', 'nome': 'Complexo Hospitalar Universitário da UFC', 'cor': '#2563eb', 'icone': 'bi-building'},
            {'codigo': 'HUWC', 'nome': 'Hospital Universitário Walter Cantídio', 'cor': '#059669', 'icone': 'bi-hospital'},
            {'codigo': 'MEAC', 'nome': 'Maternidade Escola Assis Chateaubriand', 'cor': '#d97706', 'icone': 'bi-heart'},
        ]
        for i, a in enumerate(abrangencias_padrao):
            if not Abrangencia.query.filter_by(codigo=a['codigo']).first():
                db.session.add(Abrangencia(ordem=i, **a))

        # Tipos de documento padrão (codigo JÁ É a abreviação)
        tipos_padrao = [
            {'codigo': 'POP', 'nome': 'Procedimento Operacional Padrão', 'validade_anos': 2},
            {'codigo': 'MAN', 'nome': 'Manual', 'validade_anos': 2},
            {'codigo': 'PROT', 'nome': 'Protocolo', 'validade_anos': 2},
            {'codigo': 'POL', 'nome': 'Política', 'validade_anos': 4},
            {'codigo': 'REG', 'nome': 'Regimento', 'validade_anos': 4},
            {'codigo': 'REGUL', 'nome': 'Regulamento', 'validade_anos': 4},
        ]
        for i, t in enumerate(tipos_padrao):
            if not TipoDocumento.query.filter_by(codigo=t['codigo']).first():
                db.session.add(TipoDocumento(ordem=i, **t))

        # Perfis padrão
        perfis_padrao = [
            {'codigo': 'comum', 'nome': 'Usuário Comum', 'cor': '#6b7280',
             'descricao': 'Cria documentos e executa tarefas'},
            {'codigo': 'gerente', 'nome': 'Gerente', 'cor': '#ca8a04',
             'descricao': 'Gerencia documentos e equipe do setor'},
            {'codigo': 'qualidade_triador', 'nome': 'Triador UGQ', 'cor': '#2563eb',
             'descricao': 'Faz triagem inicial de documentos'},
            {'codigo': 'qualidade_validador', 'nome': 'Validador UGQ', 'cor': '#16a34a',
             'descricao': 'Valida, codifica e publica documentos'},
            {'codigo': 'administrador', 'nome': 'Administrador', 'cor': '#dc2626',
             'descricao': 'Controle total do sistema'},
        ]
        for p in perfis_padrao:
            if not PerfilPermissao.query.filter_by(codigo=p['codigo']).first():
                db.session.add(PerfilPermissao(**p))

        db.session.commit()
        flash('Dados padrão inicializados com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao inicializar dados: {str(e)}', 'danger')

    return redirect(url_for('admin.configuracoes'))


# ============================================================================
# APIs
# ============================================================================

@admin_bp.route('/api/setores')
@login_required
def api_setores():
    """API para obter setores por abrangência"""
    abrangencia_id = request.args.get('abrangencia_id', type=int)
    abrangencia_codigo = request.args.get('abrangencia')

    if abrangencia_id:
        setores = Setor.query.filter_by(abrangencia_id=abrangencia_id, ativo=True).order_by(Setor.nome).all()
    elif abrangencia_codigo:
        abrang = Abrangencia.query.filter_by(codigo=abrangencia_codigo).first()
        if abrang:
            setores = Setor.query.filter_by(abrangencia_id=abrang.id, ativo=True).order_by(Setor.nome).all()
        else:
            setores = []
    else:
        setores = Setor.query.filter_by(ativo=True).order_by(Setor.nome).all()

    return jsonify({
        'setores': [{'id': s.id, 'nome': s.nome, 'sigla': s.sigla} for s in setores]
    })


@admin_bp.route('/api/abrangencias')
@login_required
def api_abrangencias():
    """API para obter abrangências"""
    abrangencias = Abrangencia.query.filter_by(ativo=True).order_by(Abrangencia.ordem).all()
    return jsonify({
        'abrangencias': [{'id': a.id, 'codigo': a.codigo, 'nome': a.nome, 'cor': a.cor} for a in abrangencias]
    })


@admin_bp.route('/api/tipos-documento')
@login_required
def api_tipos_documento():
    """API para obter tipos de documento"""
    tipos = TipoDocumento.query.filter_by(ativo=True).order_by(TipoDocumento.ordem).all()
    return jsonify({
        'tipos': [{'id': t.id, 'codigo': t.codigo, 'nome': t.nome, 'validade_anos': t.validade_anos} for t in tipos]
    })


# ============================================================================
# PÁGINA DE CONFIGURAÇÕES AVANÇADAS DO SISTEMA
# ============================================================================

@admin_bp.route('/configuracoes-sistema')
@login_required
@admin_required
def configuracoes_sistema():
    """Página de configurações avançadas do sistema"""
    config = ConfiguracaoSistema.get_config()
    whatsapp_config = ConfiguracaoWhatsApp.get_config()

    # Estatísticas para o header
    stats = {
        'total_usuarios': Usuario.query.count(),
        'usuarios_ativos': Usuario.query.filter_by(ativo=True).count(),
        'total_documentos': Documento.query.count(),
        'documentos_publicados': Documento.query.filter_by(status='Publicado').count(),
        'tarefas_pendentes': Tarefa.query.filter_by(concluida=False).count(),
    }

    return render_template('admin/configuracoes_sistema.html',
                          config=config,
                          whatsapp_config=whatsapp_config,
                          stats=stats)


@admin_bp.route('/configuracoes-sistema/salvar', methods=['POST'])
@login_required
@admin_required
def configuracoes_sistema_salvar():
    """Salva todas as configurações do sistema"""
    config = ConfiguracaoSistema.get_config()
    secao = request.form.get('secao', 'geral')

    try:
        if secao == 'geral':
            config.nome_sistema = request.form.get('nome_sistema', config.nome_sistema)
            config.nome_instituicao = request.form.get('nome_instituicao', config.nome_instituicao)
            config.sigla_instituicao = request.form.get('sigla_instituicao', config.sigla_instituicao)
            config.logo_url = request.form.get('logo_url', config.logo_url)
            config.favicon_url = request.form.get('favicon_url', config.favicon_url)
            config.cor_primaria = request.form.get('cor_primaria', config.cor_primaria)
            config.cor_secundaria = request.form.get('cor_secundaria', config.cor_secundaria)
            config.rodape_texto = request.form.get('rodape_texto', config.rodape_texto)
            config.timezone = request.form.get('timezone', config.timezone)
            config.idioma = request.form.get('idioma', config.idioma)

        elif secao == 'email':
            config.email_ativo = request.form.get('email_ativo') == 'on'
            config.smtp_servidor = request.form.get('smtp_servidor', config.smtp_servidor)
            config.smtp_porta = request.form.get('smtp_porta', config.smtp_porta, type=int)
            config.smtp_usuario = request.form.get('smtp_usuario', config.smtp_usuario)
            # Só atualiza senha se foi preenchida
            nova_senha = request.form.get('smtp_senha')
            if nova_senha and nova_senha.strip():
                config.smtp_senha = nova_senha
            config.smtp_use_tls = request.form.get('smtp_use_tls') == 'on'
            config.smtp_use_ssl = request.form.get('smtp_use_ssl') == 'on'
            config.email_remetente = request.form.get('email_remetente', config.email_remetente)
            config.email_remetente_nome = request.form.get('email_remetente_nome', config.email_remetente_nome)
            config.email_assunto_prefixo = request.form.get('email_assunto_prefixo', config.email_assunto_prefixo)

        elif secao == 'ia':
            config.ia_ativo = request.form.get('ia_ativo') == 'on'
            config.ia_api_url = request.form.get('ia_api_url', config.ia_api_url)
            # Só atualiza API key se foi preenchida
            nova_key = request.form.get('ia_api_key')
            if nova_key and nova_key.strip():
                config.ia_api_key = nova_key
            config.ia_modelo = request.form.get('ia_modelo', config.ia_modelo)
            config.ia_timeout = request.form.get('ia_timeout', config.ia_timeout, type=int)
            config.ia_max_tokens = request.form.get('ia_max_tokens', config.ia_max_tokens, type=int)
            config.ia_temperatura = request.form.get('ia_temperatura', config.ia_temperatura, type=float)
            config.ia_auto_extrair = request.form.get('ia_auto_extrair') == 'on'
            config.ia_auto_classificar = request.form.get('ia_auto_classificar') == 'on'
            config.ia_auto_resumir = request.form.get('ia_auto_resumir') == 'on'

        elif secao == 'seguranca':
            config.sessao_timeout_minutos = request.form.get('sessao_timeout_minutos', config.sessao_timeout_minutos, type=int)
            config.senha_min_caracteres = request.form.get('senha_min_caracteres', config.senha_min_caracteres, type=int)
            config.senha_exigir_maiuscula = request.form.get('senha_exigir_maiuscula') == 'on'
            config.senha_exigir_numero = request.form.get('senha_exigir_numero') == 'on'
            config.senha_exigir_especial = request.form.get('senha_exigir_especial') == 'on'
            config.senha_expirar_dias = request.form.get('senha_expirar_dias', config.senha_expirar_dias, type=int)
            config.login_max_tentativas = request.form.get('login_max_tentativas', config.login_max_tentativas, type=int)
            config.login_bloqueio_minutos = request.form.get('login_bloqueio_minutos', config.login_bloqueio_minutos, type=int)
            config.permitir_multiplas_sessoes = request.form.get('permitir_multiplas_sessoes') == 'on'
            config.registrar_log_acesso = request.form.get('registrar_log_acesso') == 'on'

        elif secao == 'documentos':
            config.doc_extensoes_permitidas = request.form.get('doc_extensoes_permitidas', config.doc_extensoes_permitidas)
            config.doc_tamanho_max_mb = request.form.get('doc_tamanho_max_mb', config.doc_tamanho_max_mb, type=int)
            config.doc_versao_inicial = request.form.get('doc_versao_inicial', config.doc_versao_inicial)
            config.doc_gerar_codigo_provisorio = request.form.get('doc_gerar_codigo_provisorio') == 'on'
            config.doc_exigir_descricao = request.form.get('doc_exigir_descricao') == 'on'
            config.doc_notificar_criacao = request.form.get('doc_notificar_criacao') == 'on'
            config.doc_notificar_aprovacao = request.form.get('doc_notificar_aprovacao') == 'on'
            config.doc_notificar_publicacao = request.form.get('doc_notificar_publicacao') == 'on'
            config.doc_dias_alerta_vencimento = request.form.get('doc_dias_alerta_vencimento', config.doc_dias_alerta_vencimento, type=int)
            config.doc_permitir_download_publico = request.form.get('doc_permitir_download_publico') == 'on'

        elif secao == 'workflow':
            config.workflow_ativo = request.form.get('workflow_ativo') == 'on'
            config.workflow_modo = request.form.get('workflow_modo', config.workflow_modo)
            config.workflow_prazo_triagem_dias = request.form.get('workflow_prazo_triagem_dias', config.workflow_prazo_triagem_dias, type=int)
            config.workflow_prazo_validacao_dias = request.form.get('workflow_prazo_validacao_dias', config.workflow_prazo_validacao_dias, type=int)
            config.workflow_prazo_aprovacao_dias = request.form.get('workflow_prazo_aprovacao_dias', config.workflow_prazo_aprovacao_dias, type=int)
            config.workflow_prazo_correcao_dias = request.form.get('workflow_prazo_correcao_dias', config.workflow_prazo_correcao_dias, type=int)
            config.workflow_permitir_auto_aprovacao = request.form.get('workflow_permitir_auto_aprovacao') == 'on'
            config.workflow_notificar_atraso = request.form.get('workflow_notificar_atraso') == 'on'
            config.workflow_escalar_atraso_dias = request.form.get('workflow_escalar_atraso_dias', config.workflow_escalar_atraso_dias, type=int)

        elif secao == 'notificacoes':
            config.notif_email_ativo = request.form.get('notif_email_ativo') == 'on'
            config.notif_whatsapp_ativo = request.form.get('notif_whatsapp_ativo') == 'on'
            config.notif_sistema_ativo = request.form.get('notif_sistema_ativo') == 'on'
            config.notif_frequencia_resumo = request.form.get('notif_frequencia_resumo', config.notif_frequencia_resumo)
            config.notif_hora_resumo = request.form.get('notif_hora_resumo', config.notif_hora_resumo)
            config.notif_dias_lembrete = request.form.get('notif_dias_lembrete', config.notif_dias_lembrete, type=int)

        elif secao == 'backup':
            config.backup_ativo = request.form.get('backup_ativo') == 'on'
            config.backup_frequencia = request.form.get('backup_frequencia', config.backup_frequencia)
            config.backup_hora = request.form.get('backup_hora', config.backup_hora)
            config.backup_retencao_dias = request.form.get('backup_retencao_dias', config.backup_retencao_dias, type=int)
            config.backup_incluir_arquivos = request.form.get('backup_incluir_arquivos') == 'on'
            config.backup_destino = request.form.get('backup_destino', config.backup_destino)
            config.backup_notificar_admin = request.form.get('backup_notificar_admin') == 'on'

        elif secao == 'manutencao':
            config.manutencao_ativa = request.form.get('manutencao_ativa') == 'on'
            config.manutencao_mensagem = request.form.get('manutencao_mensagem', config.manutencao_mensagem)
            config.manutencao_permitir_admin = request.form.get('manutencao_permitir_admin') == 'on'
            config.log_nivel = request.form.get('log_nivel', config.log_nivel)
            config.log_retencao_dias = request.form.get('log_retencao_dias', config.log_retencao_dias, type=int)
            config.limpar_sessoes_expiradas = request.form.get('limpar_sessoes_expiradas') == 'on'

        elif secao == 'interface':
            config.ui_itens_por_pagina = request.form.get('ui_itens_por_pagina', config.ui_itens_por_pagina, type=int)
            config.ui_mostrar_estatisticas_dashboard = request.form.get('ui_mostrar_estatisticas_dashboard') == 'on'
            config.ui_mostrar_documentos_recentes = request.form.get('ui_mostrar_documentos_recentes') == 'on'
            config.ui_mostrar_tarefas_pendentes = request.form.get('ui_mostrar_tarefas_pendentes') == 'on'
            config.ui_tema = request.form.get('ui_tema', config.ui_tema)
            config.ui_sidebar_expandida = request.form.get('ui_sidebar_expandida') == 'on'
            config.ui_animacoes = request.form.get('ui_animacoes') == 'on'

        # Auditoria
        config.atualizado_por_id = current_user.id
        config.atualizado_em = datetime.utcnow()

        db.session.commit()
        flash(f'Configuracoes de "{secao.title()}" salvas com sucesso!', 'success')

    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao salvar configuracoes: {str(e)}")
        flash(f'Erro ao salvar configuracoes: {str(e)}', 'danger')

    return redirect(url_for('admin.configuracoes_sistema') + f'#{secao}')


@admin_bp.route('/configuracoes-sistema/testar-email', methods=['POST'])
@login_required
@admin_required
def testar_email():
    """Testa a configuracao de email enviando um email de teste"""
    config = ConfiguracaoSistema.get_config()

    if not config.email_ativo:
        return jsonify({'success': False, 'message': 'Email nao esta ativo nas configuracoes'})

    if not config.smtp_servidor or not config.smtp_usuario:
        return jsonify({'success': False, 'message': 'Configuracoes de SMTP incompletas'})

    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart()
        msg['From'] = f"{config.email_remetente_nome} <{config.email_remetente}>"
        msg['To'] = current_user.email
        msg['Subject'] = f"{config.email_assunto_prefixo} Teste de Email"

        body = f"""
        <h2>Teste de Email do Sistema GED</h2>
        <p>Este e um email de teste enviado pelo Sistema GED.</p>
        <p>Se voce recebeu este email, a configuracao de SMTP esta funcionando corretamente!</p>
        <p><strong>Servidor:</strong> {config.smtp_servidor}:{config.smtp_porta}</p>
        <p><strong>TLS:</strong> {'Sim' if config.smtp_use_tls else 'Nao'}</p>
        <p><strong>SSL:</strong> {'Sim' if config.smtp_use_ssl else 'Nao'}</p>
        <hr>
        <small>Enviado em: {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')} UTC</small>
        """

        msg.attach(MIMEText(body, 'html'))

        if config.smtp_use_ssl:
            server = smtplib.SMTP_SSL(config.smtp_servidor, config.smtp_porta)
        else:
            server = smtplib.SMTP(config.smtp_servidor, config.smtp_porta)
            if config.smtp_use_tls:
                server.starttls()

        server.login(config.smtp_usuario, config.smtp_senha)
        server.send_message(msg)
        server.quit()

        return jsonify({'success': True, 'message': f'Email de teste enviado para {current_user.email}'})

    except Exception as e:
        logger.error(f"Erro ao testar email: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})


@admin_bp.route('/configuracoes-sistema/testar-ia', methods=['POST'])
@login_required
@admin_required
def testar_ia():
    """Testa a conexao com a API de IA"""
    config = ConfiguracaoSistema.get_config()

    if not config.ia_ativo:
        return jsonify({'success': False, 'message': 'IA nao esta ativa nas configuracoes'})

    if not config.ia_api_url or not config.ia_api_key:
        return jsonify({'success': False, 'message': 'Configuracoes de IA incompletas'})

    try:
        import requests

        headers = {
            'Authorization': f'Bearer {config.ia_api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': config.ia_modelo,
            'messages': [
                {'role': 'user', 'content': 'Responda apenas: OK'}
            ],
            'max_tokens': 10,
            'temperature': 0.1
        }

        response = requests.post(
            f'{config.ia_api_url}/chat/completions',
            headers=headers,
            json=payload,
            timeout=config.ia_timeout
        )

        if response.status_code == 200:
            data = response.json()
            resposta = data.get('choices', [{}])[0].get('message', {}).get('content', 'Sem resposta')
            return jsonify({
                'success': True,
                'message': f'Conexao com IA funcionando! Resposta: {resposta}',
                'modelo': config.ia_modelo
            })
        else:
            return jsonify({'success': False, 'message': f'Erro HTTP {response.status_code}: {response.text}'})

    except requests.Timeout:
        return jsonify({'success': False, 'message': f'Timeout apos {config.ia_timeout} segundos'})
    except Exception as e:
        logger.error(f"Erro ao testar IA: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})


@admin_bp.route('/configuracoes-sistema/exportar', methods=['GET'])
@login_required
@admin_required
def exportar_configuracoes():
    """Exporta todas as configuracoes em formato JSON"""
    config = ConfiguracaoSistema.get_config()

    # Remove campos sensiveis
    dados = {
        'geral': {
            'nome_sistema': config.nome_sistema,
            'nome_instituicao': config.nome_instituicao,
            'sigla_instituicao': config.sigla_instituicao,
            'cor_primaria': config.cor_primaria,
            'cor_secundaria': config.cor_secundaria,
            'rodape_texto': config.rodape_texto,
            'timezone': config.timezone,
            'idioma': config.idioma,
        },
        'email': {
            'email_ativo': config.email_ativo,
            'smtp_servidor': config.smtp_servidor,
            'smtp_porta': config.smtp_porta,
            'smtp_use_tls': config.smtp_use_tls,
            'smtp_use_ssl': config.smtp_use_ssl,
            'email_remetente': config.email_remetente,
            'email_remetente_nome': config.email_remetente_nome,
            'email_assunto_prefixo': config.email_assunto_prefixo,
        },
        'ia': {
            'ia_ativo': config.ia_ativo,
            'ia_api_url': config.ia_api_url,
            'ia_modelo': config.ia_modelo,
            'ia_timeout': config.ia_timeout,
            'ia_max_tokens': config.ia_max_tokens,
            'ia_temperatura': config.ia_temperatura,
            'ia_auto_extrair': config.ia_auto_extrair,
            'ia_auto_classificar': config.ia_auto_classificar,
            'ia_auto_resumir': config.ia_auto_resumir,
        },
        'seguranca': {
            'sessao_timeout_minutos': config.sessao_timeout_minutos,
            'senha_min_caracteres': config.senha_min_caracteres,
            'senha_exigir_maiuscula': config.senha_exigir_maiuscula,
            'senha_exigir_numero': config.senha_exigir_numero,
            'senha_exigir_especial': config.senha_exigir_especial,
            'login_max_tentativas': config.login_max_tentativas,
            'login_bloqueio_minutos': config.login_bloqueio_minutos,
        },
        'documentos': {
            'doc_extensoes_permitidas': config.doc_extensoes_permitidas,
            'doc_tamanho_max_mb': config.doc_tamanho_max_mb,
            'doc_versao_inicial': config.doc_versao_inicial,
            'doc_gerar_codigo_provisorio': config.doc_gerar_codigo_provisorio,
            'doc_dias_alerta_vencimento': config.doc_dias_alerta_vencimento,
        },
        'workflow': {
            'workflow_ativo': config.workflow_ativo,
            'workflow_modo': config.workflow_modo,
            'workflow_prazo_triagem_dias': config.workflow_prazo_triagem_dias,
            'workflow_prazo_validacao_dias': config.workflow_prazo_validacao_dias,
            'workflow_prazo_aprovacao_dias': config.workflow_prazo_aprovacao_dias,
        },
        'backup': {
            'backup_ativo': config.backup_ativo,
            'backup_frequencia': config.backup_frequencia,
            'backup_hora': config.backup_hora,
            'backup_retencao_dias': config.backup_retencao_dias,
        },
        'interface': {
            'ui_itens_por_pagina': config.ui_itens_por_pagina,
            'ui_tema': config.ui_tema,
            'ui_mostrar_estatisticas_dashboard': config.ui_mostrar_estatisticas_dashboard,
        },
        'exportado_em': datetime.utcnow().isoformat(),
        'exportado_por': current_user.nome
    }

    response = jsonify(dados)
    response.headers['Content-Disposition'] = f'attachment; filename=configuracoes_ged_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'
    return response


@admin_bp.route('/configuracoes-sistema/importar', methods=['POST'])
@login_required
@admin_required
def importar_configuracoes():
    """Importa configuracoes de um arquivo JSON"""
    if 'arquivo' not in request.files:
        flash('Nenhum arquivo enviado', 'danger')
        return redirect(url_for('admin.configuracoes_sistema'))

    arquivo = request.files['arquivo']
    if arquivo.filename == '':
        flash('Nenhum arquivo selecionado', 'danger')
        return redirect(url_for('admin.configuracoes_sistema'))

    try:
        dados = json.loads(arquivo.read().decode('utf-8'))
        config = ConfiguracaoSistema.get_config()

        # Importa apenas campos seguros
        if 'geral' in dados:
            for key, value in dados['geral'].items():
                if hasattr(config, key):
                    setattr(config, key, value)

        if 'email' in dados:
            for key, value in dados['email'].items():
                if hasattr(config, key) and key not in ['smtp_senha']:
                    setattr(config, key, value)

        if 'ia' in dados:
            for key, value in dados['ia'].items():
                if hasattr(config, key) and key not in ['ia_api_key']:
                    setattr(config, key, value)

        if 'seguranca' in dados:
            for key, value in dados['seguranca'].items():
                if hasattr(config, key):
                    setattr(config, key, value)

        if 'documentos' in dados:
            for key, value in dados['documentos'].items():
                if hasattr(config, key):
                    setattr(config, key, value)

        if 'workflow' in dados:
            for key, value in dados['workflow'].items():
                if hasattr(config, key):
                    setattr(config, key, value)

        if 'backup' in dados:
            for key, value in dados['backup'].items():
                if hasattr(config, key):
                    setattr(config, key, value)

        if 'interface' in dados:
            for key, value in dados['interface'].items():
                if hasattr(config, key):
                    setattr(config, key, value)

        config.atualizado_por_id = current_user.id
        config.atualizado_em = datetime.utcnow()

        db.session.commit()
        flash('Configuracoes importadas com sucesso! Chaves sensiveis (senhas/API keys) nao foram importadas.', 'success')

    except json.JSONDecodeError:
        flash('Arquivo JSON invalido', 'danger')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao importar configuracoes: {str(e)}")
        flash(f'Erro ao importar: {str(e)}', 'danger')

    return redirect(url_for('admin.configuracoes_sistema'))


@admin_bp.route('/configuracoes-sistema/resetar', methods=['POST'])
@login_required
@admin_required
def resetar_configuracoes():
    """Reseta todas as configuracoes para os valores padrao"""
    secao = request.form.get('secao', 'todas')

    try:
        config = ConfiguracaoSistema.get_config()

        if secao == 'geral' or secao == 'todas':
            config.nome_sistema = 'Sistema GED EBSERH'
            config.nome_instituicao = 'Complexo Hospitalar Universitario'
            config.sigla_instituicao = 'CHUFC'
            config.logo_url = None
            config.favicon_url = None
            config.cor_primaria = '#4f46e5'
            config.cor_secundaria = '#059669'
            config.rodape_texto = 'Sistema de Gestao Eletronica de Documentos - EBSERH'
            config.timezone = 'America/Fortaleza'
            config.idioma = 'pt-BR'

        if secao == 'email' or secao == 'todas':
            config.email_ativo = False
            config.smtp_servidor = 'smtp.gmail.com'
            config.smtp_porta = 587
            config.smtp_use_tls = True
            config.smtp_use_ssl = False
            config.email_assunto_prefixo = '[GED]'

        if secao == 'ia' or secao == 'todas':
            config.ia_ativo = False
            config.ia_api_url = 'https://api.deepseek.com'
            config.ia_modelo = 'deepseek-chat'
            config.ia_timeout = 30
            config.ia_max_tokens = 4000
            config.ia_temperatura = 0.7
            config.ia_auto_extrair = True
            config.ia_auto_classificar = True
            config.ia_auto_resumir = False

        if secao == 'seguranca' or secao == 'todas':
            config.sessao_timeout_minutos = 1440
            config.senha_min_caracteres = 8
            config.senha_exigir_maiuscula = True
            config.senha_exigir_numero = True
            config.senha_exigir_especial = False
            config.senha_expirar_dias = 0
            config.login_max_tentativas = 5
            config.login_bloqueio_minutos = 15
            config.permitir_multiplas_sessoes = True
            config.registrar_log_acesso = True

        if secao == 'documentos' or secao == 'todas':
            config.doc_extensoes_permitidas = '.doc,.docx,.odt,.pdf,.xls,.xlsx,.ppt,.pptx'
            config.doc_tamanho_max_mb = 50
            config.doc_versao_inicial = '1.0'
            config.doc_gerar_codigo_provisorio = True
            config.doc_exigir_descricao = False
            config.doc_notificar_criacao = True
            config.doc_notificar_aprovacao = True
            config.doc_notificar_publicacao = True
            config.doc_dias_alerta_vencimento = 30
            config.doc_permitir_download_publico = False

        if secao == 'workflow' or secao == 'todas':
            config.workflow_ativo = True
            config.workflow_modo = 'ugq'
            config.workflow_prazo_triagem_dias = 3
            config.workflow_prazo_validacao_dias = 5
            config.workflow_prazo_aprovacao_dias = 7
            config.workflow_prazo_correcao_dias = 5
            config.workflow_permitir_auto_aprovacao = False
            config.workflow_notificar_atraso = True
            config.workflow_escalar_atraso_dias = 3

        if secao == 'notificacoes' or secao == 'todas':
            config.notif_email_ativo = True
            config.notif_whatsapp_ativo = False
            config.notif_sistema_ativo = True
            config.notif_frequencia_resumo = 'diario'
            config.notif_hora_resumo = '08:00'
            config.notif_dias_lembrete = 1

        if secao == 'backup' or secao == 'todas':
            config.backup_ativo = True
            config.backup_frequencia = 'diario'
            config.backup_hora = '03:00'
            config.backup_retencao_dias = 30
            config.backup_incluir_arquivos = True
            config.backup_destino = '/backups'
            config.backup_notificar_admin = True

        if secao == 'manutencao' or secao == 'todas':
            config.manutencao_ativa = False
            config.manutencao_mensagem = 'Sistema em manutencao. Por favor, tente novamente mais tarde.'
            config.manutencao_permitir_admin = True
            config.log_nivel = 'INFO'
            config.log_retencao_dias = 90
            config.limpar_sessoes_expiradas = True

        if secao == 'interface' or secao == 'todas':
            config.ui_itens_por_pagina = 20
            config.ui_mostrar_estatisticas_dashboard = True
            config.ui_mostrar_documentos_recentes = True
            config.ui_mostrar_tarefas_pendentes = True
            config.ui_tema = 'claro'
            config.ui_sidebar_expandida = True
            config.ui_animacoes = True

        config.atualizado_por_id = current_user.id
        config.atualizado_em = datetime.utcnow()

        db.session.commit()

        if secao == 'todas':
            flash('Todas as configuracoes foram resetadas para os valores padrao!', 'success')
        else:
            flash(f'Configuracoes de "{secao.title()}" resetadas para os valores padrao!', 'success')

    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao resetar configuracoes: {str(e)}")
        flash(f'Erro ao resetar configuracoes: {str(e)}', 'danger')

    return redirect(url_for('admin.configuracoes_sistema'))


@admin_bp.route('/api/configuracoes')
@login_required
@admin_required
def api_configuracoes():
    """API para obter configuracoes do sistema"""
    config = ConfiguracaoSistema.get_config()
    return jsonify(config.to_dict())
