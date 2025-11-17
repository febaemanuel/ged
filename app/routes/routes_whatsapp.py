"""
Rotas de WhatsApp - Webhooks e Administração

Endpoints:
- POST /whatsapp/webhook - Recebe mensagens do Twilio
- GET /whatsapp/webhook - Valida webhook do Twilio
- GET /admin/whatsapp - Painel de configuração (admin apenas)
- POST /admin/whatsapp/config - Salva configurações
- POST /admin/whatsapp/testar - Testa envio de mensagem
"""

from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app.models import db, ConfiguracaoWhatsApp, LogWhatsApp, Usuario
from app.services.whatsapp_service import WhatsAppChatbot, WhatsAppService
import logging

logger = logging.getLogger(__name__)

# Blueprint para webhooks (sem autenticação)
webhook_bp = Blueprint('whatsapp_webhook', __name__, url_prefix='/whatsapp')

# Blueprint para administração (com autenticação)
admin_bp = Blueprint('whatsapp_admin', __name__, url_prefix='/admin/whatsapp')


# ============================================================================
# WEBHOOKS - Recebe mensagens do Twilio
# ============================================================================

@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    """
    Webhook que recebe mensagens do WhatsApp via Twilio

    Este endpoint é chamado pelo Twilio toda vez que alguém envia mensagem
    para o número do WhatsApp Business configurado.

    Twilio envia:
    - From: whatsapp:+5585999999999 (número do remetente)
    - Body: Texto da mensagem
    - MessageSid: ID único da mensagem
    """
    try:
        from_numero = request.form.get('From')  # whatsapp:+5585999999999
        body = request.form.get('Body')  # Texto da mensagem
        message_sid = request.form.get('MessageSid')

        logger.info(f"Mensagem recebida de {from_numero}: {body[:50]}...")

        # Processa mensagem com chatbot
        chatbot = WhatsAppChatbot()
        response = chatbot.processar_mensagem_recebida(from_numero, body)

        return response, 200, {'Content-Type': 'text/xml'}

    except Exception as e:
        logger.error(f"Erro no webhook WhatsApp: {str(e)}", exc_info=True)

        # Retorna mensagem de erro genérica
        from twilio.twiml.messaging_response import MessagingResponse
        response = MessagingResponse()
        response.message("❌ Erro ao processar mensagem. Tente novamente em instantes.")
        return str(response), 200, {'Content-Type': 'text/xml'}


@webhook_bp.route('/webhook', methods=['GET'])
def webhook_validacao():
    """
    Endpoint de validação do webhook (Twilio usa para verificar se está ativo)
    """
    return "Webhook WhatsApp OK", 200


# ============================================================================
# PAINEL ADMINISTRATIVO - Configuração do WhatsApp
# ============================================================================

@admin_bp.route('/', methods=['GET'])
@login_required
def configuracao():
    """
    Painel de configuração do WhatsApp
    Apenas administradores têm acesso
    """
    if not current_user.is_admin():
        flash('Apenas administradores podem acessar as configurações do WhatsApp', 'danger')
        return redirect(url_for('view.dashboard'))

    config = ConfiguracaoWhatsApp.get_config()

    # Estatísticas de uso
    total_mensagens = LogWhatsApp.query.count()
    mensagens_enviadas = LogWhatsApp.query.filter_by(direcao='enviada').count()
    mensagens_recebidas = LogWhatsApp.query.filter_by(direcao='recebida').count()
    mensagens_falhas = LogWhatsApp.query.filter_by(status='falhou').count()

    # Usuários com WhatsApp ativo
    usuarios_whatsapp = Usuario.query.filter(
        Usuario.telefone.isnot(None),
        Usuario.whatsapp_ativo == True
    ).count()

    stats = {
        'total_mensagens': total_mensagens,
        'mensagens_enviadas': mensagens_enviadas,
        'mensagens_recebidas': mensagens_recebidas,
        'mensagens_falhas': mensagens_falhas,
        'usuarios_whatsapp': usuarios_whatsapp
    }

    return render_template('admin/whatsapp_config.html', config=config, stats=stats)


@admin_bp.route('/config', methods=['POST'])
@login_required
def salvar_configuracao():
    """
    Salva configurações do WhatsApp
    """
    if not current_user.is_admin():
        return jsonify({'erro': 'Acesso negado'}), 403

    try:
        config = ConfiguracaoWhatsApp.get_config()

        # Log estado anterior
        estado_anterior_ativo = config.ativo
        logger.info(f"Estado anterior WhatsApp ativo: {estado_anterior_ativo}")

        # Atualiza configurações
        # IMPORTANTE: Checkbox envia 'on' quando marcado, nada quando desmarcado
        novo_estado_ativo = request.form.get('ativo') == 'on'
        config.ativo = novo_estado_ativo

        config.twilio_account_sid = request.form.get('twilio_account_sid', '').strip()
        config.twilio_auth_token = request.form.get('twilio_auth_token', '').strip()
        config.twilio_whatsapp_number = request.form.get('twilio_whatsapp_number', '').strip()

        # Funcionalidades
        config.usar_para_notificacoes = request.form.get('usar_para_notificacoes') == 'on'
        config.usar_para_assinaturas = request.form.get('usar_para_assinaturas') == 'on'
        config.usar_para_lembretes = request.form.get('usar_para_lembretes') == 'on'

        # Método de confirmação
        config.metodo_confirmacao = request.form.get('metodo_confirmacao', 'ambos')

        # Segurança
        config.exigir_2fa = request.form.get('exigir_2fa') == 'on'
        config.timeout_sessao_minutos = int(request.form.get('timeout_sessao_minutos', 15))
        config.deletar_mensagens_sensiveis = request.form.get('deletar_mensagens_sensiveis') == 'on'

        # Horários
        config.horario_inicio = request.form.get('horario_inicio', '08:00')
        config.horario_fim = request.form.get('horario_fim', '18:00')

        # Dias da semana (checkboxes múltiplos)
        dias_selecionados = request.form.getlist('dias_semana')
        config.dias_semana = ','.join(dias_selecionados) if dias_selecionados else '1,2,3,4,5'

        # Auditoria
        config.atualizado_por_id = current_user.id
        from datetime import datetime
        config.atualizado_em = datetime.utcnow()

        # Commit com validação
        db.session.commit()

        # Log confirmação
        logger.info(f"WhatsApp {estado_anterior_ativo} -> {novo_estado_ativo}")
        logger.info(f"Configuração salva com sucesso por usuário {current_user.nome}")

        # Mensagem flash informativa
        status_msg = "ATIVADO" if novo_estado_ativo else "DESATIVADO"
        flash(f'Configurações do WhatsApp salvas com sucesso! Status: {status_msg}', 'success')

        return redirect(url_for('whatsapp_admin.configuracao'))

    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao salvar configurações WhatsApp: {str(e)}", exc_info=True)
        flash(f'Erro ao salvar configurações: {str(e)}', 'danger')
        return redirect(url_for('whatsapp_admin.configuracao'))


@admin_bp.route('/testar', methods=['POST'])
@login_required
def testar_envio():
    """
    Testa envio de mensagem via WhatsApp
    """
    if not current_user.is_admin():
        return jsonify({'erro': 'Acesso negado'}), 403

    telefone = request.form.get('telefone_teste')

    if not telefone:
        return jsonify({'erro': 'Telefone não informado'}), 400

    # Formata número (remove espaços, parênteses, etc)
    telefone = telefone.replace(' ', '').replace('(', '').replace(')', '').replace('-', '')

    if not telefone.startswith('+'):
        telefone = '+55' + telefone  # Assume Brasil se não tem código de país

    # Envia mensagem de teste
    service = WhatsAppService()

    if not service.esta_ativo():
        return jsonify({'erro': 'WhatsApp não está ativo ou não configurado'}), 400

    mensagem_teste = f"""
🧪 *Mensagem de Teste - Sistema GED*

Olá! Esta é uma mensagem de teste do sistema GED EBSERH.

✅ Configuração do WhatsApp está funcionando corretamente!

📱 Responda *menu* para ver suas tarefas pendentes.

_Teste realizado por: {current_user.nome}_
_Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}_
    """.strip()

    sucesso, resultado = service.enviar_mensagem(telefone, mensagem_teste)

    if sucesso:
        return jsonify({
            'sucesso': True,
            'mensagem': f'Mensagem enviada com sucesso para {telefone}!',
            'message_sid': resultado
        })
    else:
        return jsonify({
            'sucesso': False,
            'erro': f'Erro ao enviar mensagem: {resultado}'
        }), 400


@admin_bp.route('/logs', methods=['GET'])
@login_required
def logs():
    """
    Visualiza logs de mensagens WhatsApp
    """
    if not current_user.is_admin():
        flash('Acesso negado', 'danger')
        return redirect(url_for('view.dashboard'))

    page = request.args.get('page', 1, type=int)
    per_page = 50

    # Filtros
    direcao = request.args.get('direcao')
    status = request.args.get('status')

    query = LogWhatsApp.query

    if direcao:
        query = query.filter_by(direcao=direcao)

    if status:
        query = query.filter_by(status=status)

    logs = query.order_by(LogWhatsApp.criado_em.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('admin/whatsapp_logs.html', logs=logs)


@admin_bp.route('/templates', methods=['GET', 'POST'])
@login_required
def templates():
    """
    Edita templates de mensagens
    """
    if not current_user.is_admin():
        flash('Acesso negado', 'danger')
        return redirect(url_for('view.dashboard'))

    config = ConfiguracaoWhatsApp.get_config()

    if request.method == 'POST':
        # Atualiza templates
        templates_dict = {
            'boas_vindas': request.form.get('template_boas_vindas'),
            'menu_principal': request.form.get('template_menu_principal'),
            'documento_detalhes': request.form.get('template_documento_detalhes'),
            'pedir_senha': request.form.get('template_pedir_senha'),
            'assinatura_sucesso': request.form.get('template_assinatura_sucesso'),
            'senha_incorreta': request.form.get('template_senha_incorreta'),
            'sessao_expirada': request.form.get('template_sessao_expirada'),
            'fora_horario': request.form.get('template_fora_horario'),
            'numero_nao_cadastrado': request.form.get('template_numero_nao_cadastrado')
        }

        config.set_templates(templates_dict)
        config.atualizado_por_id = current_user.id
        db.session.commit()

        flash('Templates atualizados com sucesso!', 'success')
        return redirect(url_for('whatsapp_admin.templates'))

    templates_atuais = config.get_templates()

    return render_template('admin/whatsapp_templates.html', templates=templates_atuais)
