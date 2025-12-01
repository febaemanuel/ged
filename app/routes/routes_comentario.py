"""
Rotas de Sistema de Comentários

Endpoints:
- GET /comentario/documento/<doc_id> - Lista comentários de um documento
- POST /comentario/criar - Criar novo comentário
- PUT /comentario/<id> - Editar comentário
- DELETE /comentario/<id> - Deletar comentário
- POST /comentario/<id>/responder - Responder a um comentário
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import logging

from app.models import db, Comentario, Documento, Notificacao

bp = Blueprint('comentario', __name__, url_prefix='/comentario')
logger = logging.getLogger(__name__)


def enviar_email_comentario(destinatario_email, destinatario_nome, assunto, mensagem, documento=None):
    """
    Wrapper para envio de email de comentários
    Falha silenciosamente se houver erro (email é opcional)
    """
    try:
        from app.services.email_service import EmailService

        corpo_html = EmailService._gerar_template_base(
            titulo=assunto,
            mensagem=f"<p>Olá <strong>{destinatario_nome}</strong>,</p><p>{mensagem}</p>"
        )

        EmailService._enviar_email(destinatario_email, assunto, corpo_html)
    except Exception as e:
        logger.warning(f'Erro ao enviar email de comentário: {e}')
        pass


@bp.route('/documento/<int:documento_id>', methods=['GET'])
@login_required
def listar_comentarios(documento_id):
    """
    Lista comentários de um documento
    Retorna apenas comentários principais (sem pai)
    Respostas vêm como subitens
    """
    documento = Documento.query.get_or_404(documento_id)

    # Comentários são públicos para documentos publicados
    # Para outros status, verifica permissão
    if documento.status != 'Publicado':
        if not documento.pode_editar(current_user) and documento.criador_id != current_user.id:
            if not current_user.is_gerente_ou_superior():
                return jsonify({'erro': 'Sem permissão para ver comentários deste documento'}), 403

    # Busca comentários principais (sem pai)
    comentarios_principais = Comentario.query.filter_by(
        documento_id=documento_id,
        pai_id=None
    ).order_by(Comentario.data_criacao.desc()).all()

    def serializar_comentario(comentario):
        """Serializa comentário com suas respostas"""
        respostas = Comentario.query.filter_by(
            pai_id=comentario.id
        ).order_by(Comentario.data_criacao.asc()).all()

        return {
            'id': comentario.id,
            'texto': comentario.texto,
            'secao': comentario.secao,
            'editado': comentario.editado,
            'data_criacao': comentario.data_criacao.isoformat(),
            'data_edicao': comentario.data_edicao.isoformat() if comentario.data_edicao else None,
            'usuario': {
                'id': comentario.usuario.id,
                'nome': comentario.usuario.nome,
                'email': comentario.usuario.email,
                'perfil': comentario.usuario.perfil
            },
            'mencoes': comentario.get_mencoes(),
            'total_respostas': len(respostas),
            'respostas': [serializar_comentario(r) for r in respostas],
            'pode_editar': comentario.pode_editar(current_user),
            'pode_deletar': comentario.pode_deletar(current_user)
        }

    return jsonify({
        'documento_id': documento_id,
        'total_comentarios': len(comentarios_principais),
        'comentarios': [serializar_comentario(c) for c in comentarios_principais]
    })


@bp.route('/criar', methods=['POST'])
@login_required
def criar_comentario():
    """
    Cria novo comentário em um documento
    Suporta @menções
    """
    data = request.get_json()

    # Validação
    documento_id = data.get('documento_id')
    texto = data.get('texto', '').strip()

    if not documento_id:
        return jsonify({'erro': 'documento_id é obrigatório'}), 400

    if not texto:
        return jsonify({'erro': 'Texto do comentário é obrigatório'}), 400

    documento = Documento.query.get_or_404(documento_id)

    # Comentários são públicos para documentos publicados
    # Para outros status, verifica permissão
    if documento.status != 'Publicado':
        if not documento.pode_editar(current_user) and documento.criador_id != current_user.id:
            if not current_user.is_gerente_ou_superior():
                return jsonify({'erro': 'Sem permissão para comentar neste documento'}), 403

    # Cria comentário
    comentario = Comentario(
        documento_id=documento_id,
        usuario_id=current_user.id,
        texto=texto,
        secao=data.get('secao')
    )

    db.session.add(comentario)
    db.session.flush()  # Para obter ID antes de processar menções

    # Processa @menções
    usuarios_mencionados = comentario.processar_mencoes()

    db.session.commit()

    # Envia notificações para usuários mencionados
    for usuario in usuarios_mencionados:
        # Cria notificação no sistema
        notif = Notificacao(
            usuario_id=usuario.id,
            documento_id=documento_id,
            tipo='mencao_comentario',
            titulo=f'{current_user.nome} mencionou você em um comentário',
            mensagem=f'Documento: {documento.titulo}\nComentário: {texto[:100]}...'
        )
        db.session.add(notif)

        # Envia email (se configurado)
        enviar_email_comentario(
            destinatario_email=usuario.email,
            destinatario_nome=usuario.nome,
            assunto=f'Você foi mencionado em: {documento.titulo}',
            mensagem=f'{current_user.nome} mencionou você em um comentário:<br><br>"{texto}"',
            documento=documento
        )

    db.session.commit()

    return jsonify({
        'mensagem': 'Comentário criado com sucesso',
        'comentario': {
            'id': comentario.id,
            'texto': comentario.texto,
            'data_criacao': comentario.data_criacao.isoformat(),
            'mencoes_enviadas': len(usuarios_mencionados)
        }
    }), 201


@bp.route('/<int:comentario_id>', methods=['PUT'])
@login_required
def editar_comentario(comentario_id):
    """Edita um comentário existente"""
    comentario = Comentario.query.get_or_404(comentario_id)

    # Verifica permissão
    if not comentario.pode_editar(current_user):
        return jsonify({'erro': 'Sem permissão para editar este comentário'}), 403

    data = request.get_json()
    novo_texto = data.get('texto', '').strip()

    if not novo_texto:
        return jsonify({'erro': 'Texto do comentário é obrigatório'}), 400

    # Edita comentário
    comentario.editar_texto(novo_texto)

    # Reprocessa menções
    usuarios_mencionados = comentario.processar_mencoes()

    db.session.commit()

    # Envia notificações para novos mencionados
    for usuario in usuarios_mencionados:
        notif = Notificacao(
            usuario_id=usuario.id,
            documento_id=comentario.documento_id,
            tipo='mencao_comentario',
            titulo=f'{current_user.nome} mencionou você em um comentário editado',
            mensagem=f'Comentário: {novo_texto[:100]}...'
        )
        db.session.add(notif)

    db.session.commit()

    return jsonify({
        'mensagem': 'Comentário editado com sucesso',
        'comentario': {
            'id': comentario.id,
            'texto': comentario.texto,
            'editado': comentario.editado,
            'data_edicao': comentario.data_edicao.isoformat()
        }
    })


@bp.route('/<int:comentario_id>', methods=['DELETE'])
@login_required
def deletar_comentario(comentario_id):
    """Deleta um comentário"""
    comentario = Comentario.query.get_or_404(comentario_id)

    # Verifica permissão
    if not comentario.pode_deletar(current_user):
        return jsonify({'erro': 'Sem permissão para deletar este comentário'}), 403

    # Remove comentário (respostas são removidas por cascade)
    db.session.delete(comentario)
    db.session.commit()

    return jsonify({
        'mensagem': 'Comentário deletado com sucesso'
    })


@bp.route('/<int:comentario_id>/responder', methods=['POST'])
@login_required
def responder_comentario(comentario_id):
    """
    Responde a um comentário
    Cria um comentário filho
    """
    comentario_pai = Comentario.query.get_or_404(comentario_id)

    data = request.get_json()
    texto = data.get('texto', '').strip()

    if not texto:
        return jsonify({'erro': 'Texto da resposta é obrigatório'}), 400

    # Verifica permissão no documento
    documento = comentario_pai.documento
    if not documento.pode_editar(current_user) and documento.criador_id != current_user.id:
        if not current_user.is_gerente_ou_superior():
            return jsonify({'erro': 'Sem permissão para responder'}), 403

    # Cria resposta
    resposta = Comentario(
        documento_id=comentario_pai.documento_id,
        usuario_id=current_user.id,
        texto=texto,
        pai_id=comentario_id
    )

    db.session.add(resposta)
    db.session.flush()

    # Processa menções
    usuarios_mencionados = resposta.processar_mencoes()

    db.session.commit()

    # Notifica autor do comentário original
    if comentario_pai.usuario_id != current_user.id:
        notif = Notificacao(
            usuario_id=comentario_pai.usuario_id,
            documento_id=documento.id,
            tipo='resposta_comentario',
            titulo=f'{current_user.nome} respondeu seu comentário',
            mensagem=f'Resposta: {texto[:100]}...'
        )
        db.session.add(notif)

        # Email
        enviar_email_comentario(
            destinatario_email=comentario_pai.usuario.email,
            destinatario_nome=comentario_pai.usuario.nome,
            assunto=f'Nova resposta ao seu comentário - {documento.titulo}',
            mensagem=f'{current_user.nome} respondeu:<br><br>"{texto}"',
            documento=documento
        )

    # Notifica mencionados
    for usuario in usuarios_mencionados:
        notif = Notificacao(
            usuario_id=usuario.id,
            documento_id=documento.id,
            tipo='mencao_comentario',
            titulo=f'{current_user.nome} mencionou você',
            mensagem=f'Resposta: {texto[:100]}...'
        )
        db.session.add(notif)

    db.session.commit()

    return jsonify({
        'mensagem': 'Resposta criada com sucesso',
        'resposta': {
            'id': resposta.id,
            'texto': resposta.texto,
            'pai_id': resposta.pai_id,
            'data_criacao': resposta.data_criacao.isoformat()
        }
    }), 201
