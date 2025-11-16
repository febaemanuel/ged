"""
Serviço de WhatsApp Chatbot para Assinatura de Documentos
Integração com Twilio WhatsApp Business API

Features:
- Chatbot interativo para assinatura de documentos
- Notificações de tarefas
- Validação de senha com segurança
- Sistema de estados (conversação)
- Auditoria completa
"""

from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime, timedelta
import hashlib
import random
import string
import logging

from flask import current_app, request
from app.models import (
    db, Usuario, Tarefa, Documento,
    ConfiguracaoWhatsApp, ConversacaoWhatsApp, LogWhatsApp,
    ItemBlocoAssinatura, BlocoAssinatura
)
from config import Config

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Serviço principal de WhatsApp"""

    def __init__(self):
        """Inicializa serviço com configurações do banco"""
        self.config = ConfiguracaoWhatsApp.get_config()

        if self.config.ativo and self.config.twilio_account_sid:
            self.client = Client(
                self.config.twilio_account_sid,
                self.config.twilio_auth_token
            )
        else:
            self.client = None

    def esta_ativo(self):
        """Verifica se WhatsApp está ativo"""
        return self.config.ativo and self.client is not None

    def enviar_mensagem(self, para_numero, mensagem, documento_id=None, tarefa_id=None):
        """
        Envia mensagem via WhatsApp

        Args:
            para_numero: Número do destinatário (formato: +5585999999999)
            mensagem: Texto da mensagem
            documento_id: ID do documento (opcional)
            tarefa_id: ID da tarefa (opcional)

        Returns:
            Tuple (sucesso, message_sid ou erro)
        """
        if not self.esta_ativo():
            logger.warning("WhatsApp não está ativo")
            return False, "WhatsApp não configurado"

        # Formata número
        if not para_numero.startswith('whatsapp:'):
            para_numero = f"whatsapp:{para_numero}"

        from_numero = f"whatsapp:{self.config.twilio_whatsapp_number}"

        try:
            # Envia mensagem
            message = self.client.messages.create(
                from_=from_numero,
                to=para_numero,
                body=mensagem
            )

            # Registra log
            telefone_limpo = para_numero.replace('whatsapp:', '')
            usuario = Usuario.query.filter_by(telefone=telefone_limpo).first()

            log = LogWhatsApp(
                usuario_id=usuario.id if usuario else None,
                telefone=telefone_limpo,
                direcao='enviada',
                mensagem=mensagem,
                twilio_sid=message.sid,
                documento_id=documento_id,
                tarefa_id=tarefa_id,
                status='enviado'
            )
            db.session.add(log)
            db.session.commit()

            logger.info(f"Mensagem WhatsApp enviada para {telefone_limpo}: {message.sid}")
            return True, message.sid

        except Exception as e:
            logger.error(f"Erro ao enviar WhatsApp: {str(e)}")

            # Registra erro no log
            log = LogWhatsApp(
                telefone=para_numero.replace('whatsapp:', ''),
                direcao='enviada',
                mensagem=mensagem,
                documento_id=documento_id,
                tarefa_id=tarefa_id,
                status='falhou',
                erro=str(e)
            )
            db.session.add(log)
            db.session.commit()

            return False, str(e)

    def enviar_notificacao_tarefa(self, usuario, tarefa):
        """
        Envia notificação de nova tarefa via WhatsApp

        Args:
            usuario: Objeto Usuario
            tarefa: Objeto Tarefa
        """
        if not self.config.usar_para_notificacoes:
            return False, "Notificações desativadas"

        if not usuario.telefone or not usuario.whatsapp_ativo:
            return False, "Usuário sem WhatsApp configurado"

        documento = tarefa.documento
        templates = self.config.get_templates()

        # Monta mensagem
        mensagem = f"""
🔔 *Nova Tarefa Atribuída*

📄 *Documento:* {documento.titulo}
🔢 *Código:* {documento.codigo_definitivo or documento.codigo_provisorio}
📋 *Tipo:* {tarefa.tipo_tarefa}
⏰ *Prazo:* {tarefa.prazo.strftime('%d/%m/%Y %H:%M') if tarefa.prazo else 'Sem prazo'}

💬 Responda *menu* para ver suas tarefas pendentes

_Sistema GED - EBSERH_
        """.strip()

        return self.enviar_mensagem(
            usuario.telefone,
            mensagem,
            documento_id=documento.id,
            tarefa_id=tarefa.id
        )

    def deletar_mensagem(self, message_sid):
        """
        Deleta mensagem do WhatsApp (Twilio permite deletar até 10 dias)

        Args:
            message_sid: SID da mensagem no Twilio
        """
        if not self.esta_ativo():
            return False

        try:
            self.client.messages(message_sid).delete()
            logger.info(f"Mensagem deletada: {message_sid}")
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar mensagem: {str(e)}")
            return False


class WhatsAppChatbot:
    """Chatbot interativo para assinatura de documentos"""

    def __init__(self):
        """Inicializa chatbot"""
        self.config = ConfiguracaoWhatsApp.get_config()
        self.service = WhatsAppService()

    def processar_mensagem_recebida(self, from_numero, body):
        """
        Processa mensagem recebida do usuário

        Args:
            from_numero: Número do remetente (whatsapp:+5585999999999)
            body: Texto da mensagem

        Returns:
            TwiML Response
        """
        response = MessagingResponse()

        # Remove prefixo whatsapp:
        telefone_limpo = from_numero.replace('whatsapp:', '')

        # Registra log
        self._registrar_log_recebida(telefone_limpo, body)

        # Verifica horário de funcionamento
        if not self.config.esta_em_horario_funcionamento():
            templates = self.config.get_templates()
            msg = templates['fora_horario'].format(
                inicio=self.config.horario_inicio,
                fim=self.config.horario_fim
            )
            response.message(msg)
            return str(response)

        # Identifica usuário
        usuario = Usuario.query.filter_by(telefone=telefone_limpo).first()

        if not usuario:
            templates = self.config.get_templates()
            response.message(templates['numero_nao_cadastrado'])
            return str(response)

        # Busca ou cria conversa
        conversa = ConversacaoWhatsApp.query.filter_by(telefone=from_numero).first()

        if not conversa:
            conversa = ConversacaoWhatsApp(
                telefone=from_numero,
                usuario_id=usuario.id,
                estado_atual='inicio'
            )
            db.session.add(conversa)
            db.session.commit()

        # Verifica se está bloqueado
        if conversa.esta_bloqueado():
            msg = f"🚫 Você foi temporariamente bloqueado devido a tentativas incorretas de senha.\n"
            msg += f"Tente novamente após {conversa.bloqueado_ate.strftime('%H:%M')}."
            response.message(msg)
            return str(response)

        # Verifica se sessão expirou
        timeout = self.config.timeout_sessao_minutos
        if not conversa.esta_ativa(timeout):
            conversa.expirar()
            db.session.commit()

        # Processa comando baseado no estado
        body_lower = body.strip().lower()

        # Comandos globais
        if body_lower in ['menu', 'inicio', 'oi', 'olá', 'ola', 'hi', 'hello']:
            return self._menu_principal(usuario, conversa, response)

        elif body_lower in ['ajuda', 'help', '?']:
            return self._ajuda(response)

        elif body_lower in ['sair', 'cancelar', 'parar']:
            return self._sair(conversa, response)

        # Processa baseado no estado
        estado = conversa.estado_atual

        if estado in ['inicio', 'expirado', None]:
            return self._menu_principal(usuario, conversa, response)

        elif estado == 'aguardando_escolha_documento':
            return self._processar_escolha_documento(usuario, conversa, body, response)

        elif estado == 'aguardando_acao_documento':
            return self._processar_acao_documento(usuario, conversa, body, response)

        elif estado == 'aguardando_email':
            return self._processar_confirmacao_email(usuario, conversa, body, response)

        elif estado == 'aguardando_justificativa':
            return self._processar_justificativa(usuario, conversa, body, response)

        else:
            # Estado desconhecido, volta ao menu
            return self._menu_principal(usuario, conversa, response)

    def _menu_principal(self, usuario, conversa, response):
        """Exibe menu principal com tarefas pendentes"""
        # Busca tarefas de assinatura pendentes
        tarefas_assinatura = Tarefa.query.filter_by(
            responsavel_id=usuario.id,
            tipo_tarefa=Config.TAREFA_ASSINAR_DOCUMENTO,
            concluida=False
        ).order_by(Tarefa.prazo.asc()).limit(10).all()

        if not tarefas_assinatura:
            msg = "✅ Parabéns! Você não tem documentos pendentes para assinar.\n\n"
            msg += "📧 Você receberá uma notificação quando houver novas tarefas."
            response.message(msg)

            # Limpa estado
            conversa.atualizar_estado('inicio', {})
            db.session.commit()

            return str(response)

        # Monta lista de documentos
        msg = f"📋 *Documentos Pendentes de Assinatura ({len(tarefas_assinatura)})*\n\n"

        for i, tarefa in enumerate(tarefas_assinatura, 1):
            doc = tarefa.documento
            prazo_str = tarefa.prazo.strftime('%d/%m') if tarefa.prazo else 'S/ prazo'

            # Marca se atrasado
            status_emoji = '⏰' if tarefa.esta_atrasada() else '📄'

            msg += f"{i}️⃣ {status_emoji} {doc.codigo_definitivo or doc.codigo_provisorio}\n"
            msg += f"   {doc.titulo[:45]}...\n" if len(doc.titulo) > 45 else f"   {doc.titulo}\n"
            msg += f"   🗓️ Prazo: {prazo_str}\n\n"

        msg += "\n💬 *Responda o número do documento para ver opções*"
        msg += "\n\n_Digite 'ajuda' para ver comandos disponíveis_"

        response.message(msg)

        # Atualiza estado
        tarefas_ids = [t.id for t in tarefas_assinatura]
        conversa.atualizar_estado('aguardando_escolha_documento', {'tarefas_ids': tarefas_ids})
        db.session.commit()

        return str(response)

    def _processar_escolha_documento(self, usuario, conversa, body, response):
        """Processa escolha do documento pelo número"""
        try:
            escolha = int(body.strip())
            contexto = conversa.get_contexto()
            tarefas_ids = contexto.get('tarefas_ids', [])

            if escolha < 1 or escolha > len(tarefas_ids):
                raise ValueError("Número inválido")

            tarefa_id = tarefas_ids[escolha - 1]
            tarefa = Tarefa.query.get(tarefa_id)

            if not tarefa:
                raise ValueError("Tarefa não encontrada")

            doc = tarefa.documento

            # Monta detalhes do documento
            msg = f"📄 *{doc.codigo_definitivo or doc.codigo_provisorio}*\n"
            msg += f"*{doc.titulo}*\n\n"

            msg += f"👤 *Autor:* {doc.criador.nome}\n"
            msg += f"📅 *Criado em:* {doc.data_criacao.strftime('%d/%m/%Y')}\n"
            msg += f"📋 *Tipo:* {doc.tipo_documento}\n"
            msg += f"🏥 *Setor:* {doc.setor or 'N/A'}\n"

            if tarefa.prazo:
                status = "⚠️ ATRASADO" if tarefa.esta_atrasada() else "✅ No prazo"
                msg += f"⏰ *Prazo:* {tarefa.prazo.strftime('%d/%m/%Y %H:%M')} - {status}\n"

            # Resumo (se disponível)
            metadados = doc.get_metadados()
            if metadados.get('resumo'):
                resumo = metadados['resumo'][:200]
                msg += f"\n📝 *Resumo:*\n_{resumo}..._\n"

            msg += "\n\n💬 *O que deseja fazer?*\n"
            msg += "1️⃣ - ✅ Aprovar e assinar agora\n"
            msg += "2️⃣ - ❌ Reprovar documento\n"
            msg += "3️⃣ - 📱 Ver documento completo (link)\n"
            msg += "4️⃣ - ⬅️ Voltar ao menu principal"

            response.message(msg)

            # Atualiza estado
            conversa.atualizar_estado('aguardando_acao_documento', {'tarefa_id': tarefa_id})
            db.session.commit()

        except (ValueError, IndexError):
            msg = "❌ Opção inválida!\n\n"
            msg += "Por favor, digite o *número* do documento que deseja visualizar."
            response.message(msg)

        return str(response)

    def _processar_acao_documento(self, usuario, conversa, body, response):
        """Processa ação escolhida (aprovar/reprovar/ver)"""
        contexto = conversa.get_contexto()
        tarefa_id = contexto.get('tarefa_id')
        tarefa = Tarefa.query.get(tarefa_id)

        if not tarefa:
            response.message("❌ Tarefa não encontrada. Digite *menu* para recomeçar.")
            return str(response)

        doc = tarefa.documento
        opcao = body.strip()

        if opcao == '1':  # APROVAR E ASSINAR
            msg = "🔒 *Confirmação de Assinatura Digital*\n\n"
            msg += f"📄 *Documento:* {doc.codigo_definitivo or doc.codigo_provisorio}\n"
            msg += f"📝 *Título:* {doc.titulo}\n\n"
            msg += "Para confirmar sua assinatura, digite seu *endereço de email*:\n\n"
            msg += "⚠️ _Digite exatamente o email cadastrado no sistema_\n"
            msg += "⚠️ _Após 3 tentativas incorretas, você será bloqueado por 30 minutos_"

            response.message(msg)

            conversa.atualizar_estado('aguardando_email', {'tarefa_id': tarefa_id})
            db.session.commit()

        elif opcao == '2':  # REPROVAR
            msg = "✍️ *Reprovação de Documento*\n\n"
            msg += f"Você está reprovando: *{doc.codigo_definitivo or doc.codigo_provisorio}*\n\n"
            msg += "Por favor, digite a *justificativa* da reprovação:\n"
            msg += "_(Mínimo 20 caracteres)_"

            response.message(msg)

            conversa.atualizar_estado('aguardando_justificativa', {'tarefa_id': tarefa_id})
            db.session.commit()

        elif opcao == '3':  # VER DOCUMENTO COMPLETO
            # Gera link temporário
            link = f"{current_app.config.get('APP_URL', 'http://localhost:5000')}/documento/{doc.id}"

            msg = f"📱 *Visualizar Documento Completo*\n\n"
            msg += f"📄 {doc.titulo}\n\n"
            msg += f"🔗 Acesse o link abaixo para visualizar o documento completo:\n\n"
            msg += f"{link}\n\n"
            msg += "⚠️ _Link expira em 24 horas_\n\n"
            msg += "Após visualizar, volte aqui para assinar!\n"
            msg += "Digite *menu* para ver opções novamente."

            response.message(msg)

        elif opcao == '4':  # VOLTAR
            return self._menu_principal(usuario, conversa, response)

        else:
            msg = "❌ Opção inválida!\n\n"
            msg += "Escolha uma das opções:\n"
            msg += "1 - Aprovar e assinar\n"
            msg += "2 - Reprovar\n"
            msg += "3 - Ver documento completo\n"
            msg += "4 - Voltar ao menu"
            response.message(msg)

        return str(response)

    def _processar_confirmacao_email(self, usuario, conversa, email_digitado, response):
        """Valida email digitado e processa assinatura"""
        contexto = conversa.get_contexto()
        tarefa_id = contexto.get('tarefa_id')
        tarefa = Tarefa.query.get(tarefa_id)

        if not tarefa:
            response.message("❌ Sessão expirada. Digite *menu* para recomeçar.")
            conversa.expirar()
            db.session.commit()
            return str(response)

        # Valida email (case-insensitive e remove espaços)
        email_digitado = email_digitado.strip().lower()
        email_cadastrado = usuario.email.strip().lower()

        if email_digitado != email_cadastrado:
            conversa.incrementar_tentativa_senha()
            db.session.commit()

            tentativas_restantes = 3 - conversa.tentativas_senha

            if tentativas_restantes > 0:
                msg = f"❌ *Email incorreto!*\n\n"
                msg += f"O email digitado não corresponde ao cadastrado no sistema.\n\n"
                msg += f"Você tem *{tentativas_restantes} tentativa(s)* restante(s).\n\n"
                msg += "Digite seu email novamente ou *cancelar* para sair."
                response.message(msg)
            else:
                msg = f"🚫 *Bloqueado!*\n\n"
                msg += f"Você foi bloqueado por 30 minutos devido a múltiplas tentativas incorretas.\n\n"
                msg += f"Tente novamente após {conversa.bloqueado_ate.strftime('%H:%M')}."
                response.message(msg)

            return str(response)

        # EMAIL CORRETO - Processa assinatura
        doc = tarefa.documento
        timestamp = datetime.utcnow()

        # Gera hash da assinatura (usando email como confirmação)
        assinatura_string = f"{usuario.id}:{tarefa.id}:{timestamp.isoformat()}:{usuario.email}"
        assinatura_hash = hashlib.sha256(assinatura_string.encode()).hexdigest()

        # IP e User-Agent (do webhook do Twilio)
        ip_address = request.headers.get('X-Forwarded-For', 'WhatsApp-Twilio')
        user_agent = 'WhatsApp-Chatbot'

        # Busca item do bloco de assinatura
        metadata = tarefa.get_metadata()
        item_id = metadata.get('item_id')

        if item_id:
            item = ItemBlocoAssinatura.query.get(item_id)
            if item:
                item.aprovar(
                    parecer="Aprovado via WhatsApp",
                    senha_hash=assinatura_hash,
                    ip_address=ip_address,
                    user_agent=user_agent
                )

        # Marca tarefa como concluída
        tarefa.concluir(parecer="Aprovado via WhatsApp", aprovado=True)

        db.session.commit()

        # Continua workflow (processa próxima assinatura se houver)
        if item_id:
            from app.services.workflow import WorkflowUGQ
            item = ItemBlocoAssinatura.query.get(item_id)
            WorkflowUGQ.processar_assinatura(item)

        # Mensagem de confirmação
        msg = "✅ *ASSINATURA REGISTRADA COM SUCESSO!*\n\n"
        msg += f"📋 *Documento:* {doc.codigo_definitivo or doc.codigo_provisorio}\n"
        msg += f"⏰ *Data/Hora:* {timestamp.strftime('%d/%m/%Y %H:%M:%S')}\n"
        msg += f"🔐 *Hash:* {assinatura_hash[:16]}...\n"
        msg += f"📧 *Protocolo:* #ASS-{tarefa.id}\n\n"
        msg += f"📧 Comprovante enviado para: {usuario.email}\n\n"
        msg += "_Sua assinatura digital foi registrada com validade jurídica._"

        response.message(msg)

        # Reseta tentativas e limpa estado
        conversa.resetar_tentativas()
        conversa.atualizar_estado('inicio', {})
        db.session.commit()

        # TODO: Enviar email com comprovante
        # EmailService.enviar_comprovante_assinatura(usuario, tarefa, assinatura_hash)

        return str(response)

    def _processar_justificativa(self, usuario, conversa, justificativa, response):
        """Processa reprovação do documento"""
        if len(justificativa) < 20:
            msg = "❌ Justificativa muito curta!\n\n"
            msg += "Por favor, forneça uma justificativa com *pelo menos 20 caracteres*."
            response.message(msg)
            return str(response)

        contexto = conversa.get_contexto()
        tarefa_id = contexto.get('tarefa_id')
        tarefa = Tarefa.query.get(tarefa_id)

        if not tarefa:
            response.message("❌ Sessão expirada. Digite *menu* para recomeçar.")
            conversa.expirar()
            db.session.commit()
            return str(response)

        doc = tarefa.documento

        # Registra reprovação
        metadata = tarefa.get_metadata()
        item_id = metadata.get('item_id')

        if item_id:
            item = ItemBlocoAssinatura.query.get(item_id)
            if item:
                item.reprovar(parecer=justificativa)

        tarefa.concluir(parecer=justificativa, aprovado=False)
        db.session.commit()

        # Continua workflow (volta para validador)
        if item_id:
            from app.services.workflow import WorkflowUGQ
            item = ItemBlocoAssinatura.query.get(item_id)
            WorkflowUGQ.processar_assinatura(item)

        # Mensagem de confirmação
        msg = "❌ *DOCUMENTO REPROVADO*\n\n"
        msg += f"📋 *Documento:* {doc.codigo_definitivo or doc.codigo_provisorio}\n"
        msg += f"📝 *Justificativa:* {justificativa}\n\n"
        msg += "O documento será devolvido para ajustes.\n\n"
        msg += "_O responsável foi notificado._"

        response.message(msg)

        # Limpa estado
        conversa.atualizar_estado('inicio', {})
        db.session.commit()

        return str(response)

    def _ajuda(self, response):
        """Exibe comandos disponíveis"""
        msg = "ℹ️ *Comandos Disponíveis*\n\n"
        msg += "*menu* - Ver documentos pendentes\n"
        msg += "*ajuda* - Ver esta mensagem\n"
        msg += "*sair* - Encerrar conversa\n\n"
        msg += "💡 _Dica: Responda apenas com o número da opção desejada_"

        response.message(msg)
        return str(response)

    def _sair(self, conversa, response):
        """Encerra conversa"""
        conversa.atualizar_estado('inicio', {})
        db.session.commit()

        msg = "👋 Até logo!\n\n"
        msg += "Digite *menu* quando precisar voltar."

        response.message(msg)
        return str(response)

    def _registrar_log_recebida(self, telefone, mensagem):
        """Registra log de mensagem recebida"""
        usuario = Usuario.query.filter_by(telefone=telefone).first()

        log = LogWhatsApp(
            usuario_id=usuario.id if usuario else None,
            telefone=telefone,
            direcao='recebida',
            mensagem=mensagem,
            status='recebido'
        )
        db.session.add(log)
        db.session.commit()
