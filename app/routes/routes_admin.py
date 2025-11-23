"""
Routes ADMIN - Rotas para administração do sistema
Painel de controle completo para administradores
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import logging

from app import db
from app.models.models import (
    Usuario, Documento, Tarefa, ListaMestra,
    Abrangencia, TipoDocumento, Setor, PerfilPermissao
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
