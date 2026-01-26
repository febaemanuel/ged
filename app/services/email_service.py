"""
Serviço de Envio de E-mails
Gerencia o envio de notificações por e-mail para os usuários
"""
from flask import current_app, render_template_string
from flask_mail import Message
from app import mail
from app.models import Usuario
import logging

logger = logging.getLogger(__name__)


def _is_email_enabled():
    """
    Verifica se o envio de e-mail está habilitado no sistema.

    Returns:
        bool: True se o email estiver ativo e configurado
    """
    try:
        from app.models import ConfiguracaoSistema
        config = ConfiguracaoSistema.get_config()
        if config:
            # Se email_ativo está explicitamente False, não envia
            if not config.email_ativo:
                return False
            # Se está ativo, verifica se tem configuração SMTP
            if config.smtp_usuario:
                return True
    except Exception as e:
        logger.warning(f"Erro ao verificar configuração de email: {e}")

    # Fallback: verifica configuração via variável de ambiente
    return bool(current_app.config.get('MAIL_USERNAME'))


def _get_email_config():
    """
    Retorna configurações de email do sistema.

    Prioridade:
    1. ConfiguracaoSistema (banco de dados)
    2. Fallback para current_app.config (variáveis de ambiente)
    """
    try:
        from app.models import ConfiguracaoSistema
        config = ConfiguracaoSistema.get_config()

        if config and config.email_ativo and config.smtp_usuario:
            return {
                'server': config.smtp_servidor,
                'port': config.smtp_porta,
                'use_tls': config.smtp_use_tls,
                'use_ssl': config.smtp_use_ssl,
                'username': config.smtp_usuario,
                'password': config.smtp_senha,
                'sender': config.email_remetente or config.smtp_usuario,
                'nome_sistema': config.nome_sistema or 'Sistema GED'
            }
    except Exception as e:
        logger.warning(f"Erro ao buscar configuração de email do banco: {e}")

    # Fallback para variáveis de ambiente
    return {
        'server': current_app.config.get('MAIL_SERVER'),
        'port': current_app.config.get('MAIL_PORT'),
        'use_tls': current_app.config.get('MAIL_USE_TLS'),
        'use_ssl': current_app.config.get('MAIL_USE_SSL'),
        'username': current_app.config.get('MAIL_USERNAME'),
        'password': current_app.config.get('MAIL_PASSWORD'),
        'sender': current_app.config.get('MAIL_DEFAULT_SENDER'),
        'nome_sistema': 'Sistema GED'
    }


class EmailService:
    """Serviço para envio de e-mails"""

    @staticmethod
    def _enviar_email(destinatario_email, assunto, corpo_html, corpo_texto=None):
        """
        Envia um e-mail

        Args:
            destinatario_email: E-mail do destinatário
            assunto: Assunto do e-mail
            corpo_html: Corpo do e-mail em HTML
            corpo_texto: Corpo do e-mail em texto simples (opcional)

        Returns:
            bool: True se enviado com sucesso, False caso contrário
        """
        try:
            # Verifica se o envio de e-mail está habilitado
            if not _is_email_enabled():
                logger.warning('Envio de e-mail desabilitado ou não configurado. E-mail não será enviado.')
                return False

            # Obtém configurações de email
            email_config = _get_email_config()

            msg = Message(
                subject=assunto,
                recipients=[destinatario_email],
                html=corpo_html,
                body=corpo_texto or corpo_html
            )

            mail.send(msg)
            logger.info(f'E-mail enviado com sucesso para {destinatario_email}: {assunto}')
            return True

        except Exception as e:
            logger.error(f'Erro ao enviar e-mail para {destinatario_email}: {str(e)}')
            return False

    @staticmethod
    def _gerar_template_base(titulo, mensagem, link_texto=None, link_url=None):
        """
        Gera template HTML base para e-mails

        Args:
            titulo: Título do e-mail
            mensagem: Mensagem principal
            link_texto: Texto do link (opcional)
            link_url: URL do link (opcional)

        Returns:
            str: HTML formatado
        """
        link_html = ''
        if link_texto and link_url:
            link_html = f'<p style="margin: 20px 0;"><a href="{link_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">{link_texto}</a></p>'

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; border-left: 4px solid #007bff; padding: 20px; margin-bottom: 20px;">
                <h2 style="margin: 0; color: #007bff;">{titulo}</h2>
            </div>
            <div style="padding: 20px; background-color: white;">
                {mensagem}
                {link_html}
            </div>
            <div style="margin-top: 20px; padding: 20px; background-color: #f8f9fa; font-size: 12px; color: #6c757d; text-align: center;">
                <p>Este é um e-mail automático do {_get_email_config().get('nome_sistema', 'Sistema GED')}. Por favor, não responda.</p>
            </div>
        </body>
        </html>
        """

    @classmethod
    def enviar_notificacao_tarefa(cls, usuario_id, tipo_tarefa, documento_titulo, documento_codigo=None):
        """
        Envia e-mail quando uma nova tarefa é atribuída ao usuário

        Args:
            usuario_id: ID do usuário
            tipo_tarefa: Tipo da tarefa
            documento_titulo: Título do documento
            documento_codigo: Código do documento (opcional)
        """
        usuario = Usuario.query.get(usuario_id)
        if not usuario or not usuario.email:
            logger.warning(f'Usuário {usuario_id} não encontrado ou sem e-mail')
            return False

        codigo_texto = f' ({documento_codigo})' if documento_codigo else ''
        assunto = f'Nova Tarefa: {tipo_tarefa}'

        mensagem = f"""
        <p>Olá <strong>{usuario.nome}</strong>,</p>
        <p>Você tem uma nova tarefa atribuída:</p>
        <ul>
            <li><strong>Tipo:</strong> {tipo_tarefa}</li>
            <li><strong>Documento:</strong> {documento_titulo}{codigo_texto}</li>
        </ul>
        <p>Por favor, acesse o sistema para visualizar e processar esta tarefa.</p>
        """

        corpo_html = cls._gerar_template_base(
            titulo='Nova Tarefa Atribuída',
            mensagem=mensagem,
            link_texto='Acessar Sistema GED',
            link_url=current_app.config.get('APP_URL', '#')
        )

        return cls._enviar_email(usuario.email, assunto, corpo_html)

    @classmethod
    def enviar_notificacao_documento_devolvido(cls, usuario_id, documento_titulo, documento_codigo, motivo):
        """
        Envia e-mail quando um documento é devolvido para correção

        Args:
            usuario_id: ID do usuário (autor)
            documento_titulo: Título do documento
            documento_codigo: Código do documento
            motivo: Motivo da devolução
        """
        usuario = Usuario.query.get(usuario_id)
        if not usuario or not usuario.email:
            return False

        assunto = f'Documento Devolvido para Correção: {documento_codigo}'

        mensagem = f"""
        <p>Olá <strong>{usuario.nome}</strong>,</p>
        <p>Seu documento foi devolvido para correção:</p>
        <ul>
            <li><strong>Documento:</strong> {documento_titulo} ({documento_codigo})</li>
            <li><strong>Motivo:</strong> {motivo}</li>
        </ul>
        <p>Por favor, realize as correções necessárias e reenvie o documento.</p>
        """

        corpo_html = cls._gerar_template_base(
            titulo='Documento Devolvido',
            mensagem=mensagem,
            link_texto='Acessar Sistema GED',
            link_url=current_app.config.get('APP_URL', '#')
        )

        return cls._enviar_email(usuario.email, assunto, corpo_html)

    @classmethod
    def enviar_notificacao_documento_aprovado(cls, usuario_id, documento_titulo, documento_codigo, versao):
        """
        Envia e-mail quando um documento é aprovado

        Args:
            usuario_id: ID do usuário
            documento_titulo: Título do documento
            documento_codigo: Código do documento
            versao: Versão do documento
        """
        usuario = Usuario.query.get(usuario_id)
        if not usuario or not usuario.email:
            return False

        assunto = f'Documento Aprovado: {documento_codigo}'

        mensagem = f"""
        <p>Olá <strong>{usuario.nome}</strong>,</p>
        <p>O documento que você participou foi aprovado:</p>
        <ul>
            <li><strong>Documento:</strong> {documento_titulo}</li>
            <li><strong>Código:</strong> {documento_codigo}</li>
            <li><strong>Versão:</strong> {versao}</li>
        </ul>
        <p>O documento está pronto para publicação.</p>
        """

        corpo_html = cls._gerar_template_base(
            titulo='Documento Aprovado',
            mensagem=mensagem,
            link_texto='Visualizar Documento',
            link_url=current_app.config.get('APP_URL', '#')
        )

        return cls._enviar_email(usuario.email, assunto, corpo_html)

    @classmethod
    def enviar_notificacao_documento_publicado(cls, usuario_id, documento_titulo, documento_codigo, versao):
        """
        Envia e-mail quando um documento é publicado

        Args:
            usuario_id: ID do usuário
            documento_titulo: Título do documento
            documento_codigo: Código do documento
            versao: Versão do documento
        """
        usuario = Usuario.query.get(usuario_id)
        if not usuario or not usuario.email:
            return False

        assunto = f'Documento Publicado: {documento_codigo}'

        mensagem = f"""
        <p>Olá <strong>{usuario.nome}</strong>,</p>
        <p>O documento foi publicado com sucesso:</p>
        <ul>
            <li><strong>Documento:</strong> {documento_titulo}</li>
            <li><strong>Código:</strong> {documento_codigo}</li>
            <li><strong>Versão:</strong> {versao}</li>
        </ul>
        <p>O documento já está disponível no repositório público.</p>
        """

        corpo_html = cls._gerar_template_base(
            titulo='Documento Publicado',
            mensagem=mensagem,
            link_texto='Ver no Repositório Público',
            link_url=current_app.config.get('APP_URL', '#') + '/publico'
        )

        return cls._enviar_email(usuario.email, assunto, corpo_html)

    @classmethod
    def enviar_notificacao_nova_versao(cls, usuario_id, documento_titulo, codigo_original, nova_versao, motivo, criador_nome):
        """
        Envia e-mail quando uma nova versão do documento é criada

        Args:
            usuario_id: ID do usuário (autor original)
            documento_titulo: Título do documento
            codigo_original: Código do documento original
            nova_versao: Nova versão criada
            motivo: Motivo da revisão
            criador_nome: Nome de quem criou a nova versão
        """
        usuario = Usuario.query.get(usuario_id)
        if not usuario or not usuario.email:
            return False

        assunto = f'Nova Versão do Documento: {codigo_original}'

        mensagem = f"""
        <p>Olá <strong>{usuario.nome}</strong>,</p>
        <p>Uma nova versão do seu documento foi criada:</p>
        <ul>
            <li><strong>Documento:</strong> {documento_titulo}</li>
            <li><strong>Código:</strong> {codigo_original}</li>
            <li><strong>Nova Versão:</strong> {nova_versao}</li>
            <li><strong>Criado por:</strong> {criador_nome}</li>
            <li><strong>Motivo:</strong> {motivo}</li>
        </ul>
        <p>A versão anterior foi marcada como obsoleta.</p>
        """

        corpo_html = cls._gerar_template_base(
            titulo='Nova Versão Criada',
            mensagem=mensagem,
            link_texto='Acessar Sistema GED',
            link_url=current_app.config.get('APP_URL', '#')
        )

        return cls._enviar_email(usuario.email, assunto, corpo_html)

    @classmethod
    def enviar_notificacao_documento_reprovado(cls, usuario_id, documento_titulo, documento_codigo, parecer):
        """
        Envia e-mail quando um documento é reprovado na assinatura

        Args:
            usuario_id: ID do usuário
            documento_titulo: Título do documento
            documento_codigo: Código do documento
            parecer: Parecer do aprovador que reprovou
        """
        usuario = Usuario.query.get(usuario_id)
        if not usuario or not usuario.email:
            return False

        assunto = f'Documento Reprovado: {documento_codigo}'

        mensagem = f"""
        <p>Olá <strong>{usuario.nome}</strong>,</p>
        <p>Um documento foi reprovado durante o processo de aprovação:</p>
        <ul>
            <li><strong>Documento:</strong> {documento_titulo} ({documento_codigo})</li>
            <li><strong>Parecer:</strong> {parecer}</li>
        </ul>
        <p>O documento necessita de ajustes antes de prosseguir.</p>
        """

        corpo_html = cls._gerar_template_base(
            titulo='Documento Reprovado',
            mensagem=mensagem,
            link_texto='Acessar Sistema GED',
            link_url=current_app.config.get('APP_URL', '#')
        )

        return cls._enviar_email(usuario.email, assunto, corpo_html)

    @classmethod
    def enviar_notificacao_documento_validado(cls, usuario_id, documento_titulo, codigo_definitivo, versao):
        """
        Envia e-mail quando um documento é validado e codificado

        Args:
            usuario_id: ID do usuário (autor)
            documento_titulo: Título do documento
            codigo_definitivo: Código definitivo atribuído
            versao: Versão do documento
        """
        usuario = Usuario.query.get(usuario_id)
        if not usuario or not usuario.email:
            return False

        assunto = f'Documento Validado: {codigo_definitivo}'

        mensagem = f"""
        <p>Olá <strong>{usuario.nome}</strong>,</p>
        <p>Seu documento foi validado e codificado:</p>
        <ul>
            <li><strong>Documento:</strong> {documento_titulo}</li>
            <li><strong>Código Definitivo:</strong> {codigo_definitivo}</li>
            <li><strong>Versão:</strong> {versao}</li>
        </ul>
        <p>O documento seguirá para o processo de aprovação.</p>
        """

        corpo_html = cls._gerar_template_base(
            titulo='Documento Validado',
            mensagem=mensagem,
            link_texto='Acessar Sistema GED',
            link_url=current_app.config.get('APP_URL', '#')
        )

        return cls._enviar_email(usuario.email, assunto, corpo_html)
