"""
Rotas de Notificações do Sistema GED

Endpoints:
- GET /api/notificacoes - Lista notificações não lidas do usuário
- GET /api/notificacoes/todas - Lista todas notificações (lidas e não lidas)
- GET /api/notificacoes/count - Conta notificações não lidas
- POST /api/notificacoes/<id>/marcar-lida - Marca notificação como lida
- POST /api/notificacoes/marcar-todas-lidas - Marca todas como lidas
"""

from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from datetime import datetime
import logging

from app.models import db, Notificacao

# Logger para este módulo
logger = logging.getLogger(__name__)

# Blueprint de notificações
bp = Blueprint('notificacao', __name__, url_prefix='/api/notificacoes')


@bp.route('', methods=['GET'])
@login_required
def listar_nao_lidas():
    """
    Lista notificações não lidas do usuário

    Returns:
        JSON: Lista de notificações não lidas
    """
    try:
        notificacoes = Notificacao.nao_lidas_usuario(current_user.id)

        return jsonify({
            'notificacoes': [{
                'id': n.id,
                'tipo': n.tipo,
                'titulo': n.titulo,
                'mensagem': n.mensagem,
                'link': n.link,
                'data_criacao': n.data_criacao.isoformat(),
                'tempo_relativo': _calcular_tempo_relativo(n.data_criacao)
            } for n in notificacoes],
            'count': len(notificacoes)
        })
    except Exception as e:
        logger.error(f"Erro ao listar notificações: {str(e)}")
        return jsonify({'erro': 'Erro ao carregar notificações'}), 500


@bp.route('/todas', methods=['GET'])
@login_required
def listar_todas():
    """
    Lista todas notificações do usuário (lidas e não lidas)

    Query params:
        - limit: Número máximo de notificações (padrão: 50)
        - offset: Offset para paginação (padrão: 0)

    Returns:
        JSON: Lista de todas as notificações
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        notificacoes = Notificacao.query.filter_by(
            usuario_id=current_user.id
        ).order_by(
            Notificacao.data_criacao.desc()
        ).limit(limit).offset(offset).all()

        total = Notificacao.query.filter_by(usuario_id=current_user.id).count()

        return jsonify({
            'notificacoes': [{
                'id': n.id,
                'tipo': n.tipo,
                'titulo': n.titulo,
                'mensagem': n.mensagem,
                'link': n.link,
                'lida': n.lida,
                'data_criacao': n.data_criacao.isoformat(),
                'data_leitura': n.data_leitura.isoformat() if n.data_leitura else None,
                'tempo_relativo': _calcular_tempo_relativo(n.data_criacao)
            } for n in notificacoes],
            'total': total,
            'limit': limit,
            'offset': offset
        })
    except Exception as e:
        logger.error(f"Erro ao listar todas notificações: {str(e)}")
        return jsonify({'erro': 'Erro ao carregar notificações'}), 500


@bp.route('/count', methods=['GET'])
@login_required
def contar_nao_lidas():
    """
    Conta notificações não lidas do usuário

    Returns:
        JSON: { count: número de não lidas }
    """
    try:
        count = Notificacao.contar_nao_lidas(current_user.id)
        return jsonify({'count': count})
    except Exception as e:
        logger.error(f"Erro ao contar notificações: {str(e)}")
        return jsonify({'erro': 'Erro ao contar notificações'}), 500


@bp.route('/<int:id>/marcar-lida', methods=['POST'])
@login_required
def marcar_lida(id):
    """
    Marca uma notificação como lida

    Args:
        id: ID da notificação

    Returns:
        JSON: { sucesso: true/false }
    """
    try:
        notificacao = Notificacao.query.get_or_404(id)

        # Verifica se notificação pertence ao usuário
        if notificacao.usuario_id != current_user.id:
            logger.warning(f"Usuário {current_user.id} tentou marcar notificação {id} de outro usuário")
            return jsonify({'erro': 'Acesso negado'}), 403

        # Marca como lida
        notificacao.marcar_como_lida()

        logger.info(f"Notificação {id} marcada como lida por usuário {current_user.id}")

        return jsonify({
            'sucesso': True,
            'mensagem': 'Notificação marcada como lida'
        })
    except Exception as e:
        logger.error(f"Erro ao marcar notificação {id} como lida: {str(e)}")
        return jsonify({'erro': 'Erro ao marcar notificação como lida'}), 500


@bp.route('/marcar-todas-lidas', methods=['POST'])
@login_required
def marcar_todas_lidas():
    """
    Marca todas notificações do usuário como lidas

    Returns:
        JSON: { sucesso: true, total: número de notificações marcadas }
    """
    try:
        total = Notificacao.marcar_todas_lidas(current_user.id)

        logger.info(f"{total} notificações marcadas como lidas para usuário {current_user.id}")

        return jsonify({
            'sucesso': True,
            'total': total,
            'mensagem': f'{total} notificação(ões) marcada(s) como lida(s)'
        })
    except Exception as e:
        logger.error(f"Erro ao marcar todas notificações como lidas: {str(e)}")
        return jsonify({'erro': 'Erro ao marcar notificações como lidas'}), 500


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def _calcular_tempo_relativo(data):
    """
    Calcula tempo relativo (ex: há 2 minutos, há 1 hora)

    Args:
        data: datetime object

    Returns:
        str: Tempo em formato relativo
    """
    agora = datetime.utcnow()
    diferenca = agora - data

    segundos = diferenca.total_seconds()

    if segundos < 60:
        return 'agora mesmo'
    elif segundos < 3600:  # Menos de 1 hora
        minutos = int(segundos / 60)
        return f'há {minutos} minuto{"s" if minutos > 1 else ""}'
    elif segundos < 86400:  # Menos de 1 dia
        horas = int(segundos / 3600)
        return f'há {horas} hora{"s" if horas > 1 else ""}'
    elif segundos < 604800:  # Menos de 1 semana
        dias = int(segundos / 86400)
        return f'há {dias} dia{"s" if dias > 1 else ""}'
    elif segundos < 2592000:  # Menos de 1 mês (30 dias)
        semanas = int(segundos / 604800)
        return f'há {semanas} semana{"s" if semanas > 1 else ""}'
    elif segundos < 31536000:  # Menos de 1 ano
        meses = int(segundos / 2592000)
        return f'há {meses} m{"ê" if meses == 1 else "e"}s{"" if meses == 1 else "es"}'
    else:
        anos = int(segundos / 31536000)
        return f'há {anos} ano{"s" if anos > 1 else ""}'
