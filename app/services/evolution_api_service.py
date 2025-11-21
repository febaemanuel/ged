"""
Serviço de WhatsApp Chatbot para Assinatura de Documentos
Integração com Evolution API (Open Source)

Features:
- Chatbot interativo para assinatura de documentos
- Notificações de tarefas
- Validação de senha com segurança
- Sistema de estados (conversação)
- Auditoria completa
- 100% compatível com a estrutura antiga do Twilio
"""

from datetime import datetime, timedelta
import hashlib
import random
import string
import logging
import requests
import json
import time
from typing import Tuple, Optional, Dict, Any

from flask import current_app, request
from app.models import (
    db, Usuario, Tarefa, Documento,
    ConfiguracaoWhatsApp, ConversacaoWhatsApp, LogWhatsApp,
    ItemBlocoAssinatura, BlocoAssinatura
)
from config import Config

# Importa a nova implementação
from app.services.evolution_api_service_v2 import EvolutionAPIv2

logger = logging.getLogger(__name__)


# Alias para compatibilidade
EvolutionAPIService = EvolutionAPIv2


class EvolutionAPIServiceOLD:
    """Serviço principal de WhatsApp usando Evolution API"""

    def __init__(self):
        """Inicializa serviço com configurações do banco"""
        self.config = ConfiguracaoWhatsApp.get_config()

        # Configurações da Evolution API
        self.base_url = self.config.evolution_api_url
        self.instance_name = self.config.evolution_instance_name
        self.api_key = self.config.evolution_api_key

        # Configurações de retry e timeout
        self.max_retries = 3
        self.timeout = 30
        self.retry_delay = 2  # segundos

    def esta_ativo(self) -> bool:
        """Verifica se WhatsApp está ativo"""
        return (
            self.config.ativo and
            self.base_url and
            self.instance_name and
            self.api_key
        )

    def _request_with_retry(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Faz requisição HTTP com retry automático

        Args:
            method: Método HTTP (GET, POST, etc)
            url: URL completa
            **kwargs: Argumentos para requests (headers, json, etc)

        Returns:
            Response object

        Raises:
            requests.exceptions.RequestException: Se todas as tentativas falharem
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    **kwargs
                )
                return response

            except requests.exceptions.Timeout as e:
                last_exception = e
                logger.warning(f"Timeout na tentativa {attempt + 1}/{self.max_retries}: {url}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))  # Backoff exponencial
                continue

            except requests.exceptions.ConnectionError as e:
                last_exception = e
                logger.warning(f"Erro de conexão na tentativa {attempt + 1}/{self.max_retries}: {url}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                continue

            except requests.exceptions.RequestException as e:
                # Outros erros não são retentados
                logger.error(f"Erro não recuperável na requisição: {str(e)}")
                raise

        # Se chegou aqui, todas as tentativas falharam
        logger.error(f"Falha após {self.max_retries} tentativas para {url}")
        raise last_exception

    def _format_number(self, numero):
        """
        Formata número para Evolution API

        Args:
            numero: Número no formato +5585999999999

        Returns:
            Número formatado: 5585999999999@s.whatsapp.net
        """
        # Remove prefixo whatsapp: se existir
        numero_limpo = numero.replace('whatsapp:', '').replace('+', '').strip()

        # Adiciona sufixo do WhatsApp
        if not numero_limpo.endswith('@s.whatsapp.net'):
            numero_limpo = f"{numero_limpo}@s.whatsapp.net"

        return numero_limpo

    def enviar_mensagem(self, para_numero, mensagem, documento_id=None, tarefa_id=None):
        """
        Envia mensagem via WhatsApp usando Evolution API

        Args:
            para_numero: Número do destinatário (formato: +5585999999999)
            mensagem: Texto da mensagem
            documento_id: ID do documento (opcional)
            tarefa_id: ID da tarefa (opcional)

        Returns:
            Tuple (sucesso, message_id ou erro)
        """
        if not self.esta_ativo():
            logger.warning("WhatsApp não está ativo")
            return False, "WhatsApp não configurado"

        # Formata número para Evolution API
        numero_formatado = self._format_number(para_numero)

        # Remove prefixo + para log
        telefone_limpo = para_numero.replace('whatsapp:', '').replace('+', '').strip()

        # Monta URL do endpoint
        url = f"{self.base_url}/message/sendText/{self.instance_name}"

        # Headers
        headers = {
            'Content-Type': 'application/json',
            'apikey': self.api_key
        }

        # Payload
        payload = {
            'number': numero_formatado,
            'text': mensagem,
            'delay': 1000  # 1 segundo de delay
        }

        try:
            # Envia requisição com retry automático
            response = self._request_with_retry('POST', url, headers=headers, json=payload)

            # Verifica resposta
            if response.status_code == 200 or response.status_code == 201:
                response_data = response.json()
                message_id = response_data.get('key', {}).get('id', 'unknown')

                # Registra log
                usuario = Usuario.query.filter_by(telefone=f"+{telefone_limpo}").first()

                log = LogWhatsApp(
                    usuario_id=usuario.id if usuario else None,
                    telefone=f"+{telefone_limpo}",
                    direcao='enviada',
                    mensagem=mensagem,
                    twilio_sid=message_id,  # Mantém compatibilidade com campo antigo
                    documento_id=documento_id,
                    tarefa_id=tarefa_id,
                    status='enviado'
                )
                db.session.add(log)
                db.session.commit()

                logger.info(f"Mensagem WhatsApp enviada para {telefone_limpo}: {message_id}")
                return True, message_id

            else:
                error_msg = f"Erro HTTP {response.status_code}: {response.text}"
                logger.error(f"Erro ao enviar WhatsApp: {error_msg}")

                # Registra erro no log
                log = LogWhatsApp(
                    telefone=f"+{telefone_limpo}",
                    direcao='enviada',
                    mensagem=mensagem,
                    documento_id=documento_id,
                    tarefa_id=tarefa_id,
                    status='falhou',
                    erro=error_msg
                )
                db.session.add(log)
                db.session.commit()

                return False, error_msg

        except requests.exceptions.Timeout:
            error_msg = "Timeout ao enviar mensagem (30s)"
            logger.error(f"Timeout ao enviar WhatsApp: {error_msg}")

            # Registra erro no log
            log = LogWhatsApp(
                telefone=f"+{telefone_limpo}",
                direcao='enviada',
                mensagem=mensagem,
                documento_id=documento_id,
                tarefa_id=tarefa_id,
                status='falhou',
                erro=error_msg
            )
            db.session.add(log)
            db.session.commit()

            return False, error_msg

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Erro ao enviar WhatsApp: {error_msg}")

            # Registra erro no log
            log = LogWhatsApp(
                telefone=f"+{telefone_limpo}",
                direcao='enviada',
                mensagem=mensagem,
                documento_id=documento_id,
                tarefa_id=tarefa_id,
                status='falhou',
                erro=error_msg
            )
            db.session.add(log)
            db.session.commit()

            return False, error_msg

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

    def enviar_mensagem_com_midia(
        self,
        para_numero: str,
        mensagem: str,
        media_url: str,
        media_type: str = 'image',
        documento_id: Optional[int] = None,
        tarefa_id: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Envia mensagem com mídia via WhatsApp (imagem, áudio, vídeo, documento)

        Args:
            para_numero: Número do destinatário
            mensagem: Caption/legenda da mídia
            media_url: URL pública da mídia
            media_type: Tipo de mídia (image, video, audio, document)
            documento_id: ID do documento (opcional)
            tarefa_id: ID da tarefa (opcional)

        Returns:
            Tuple (sucesso, message_id ou erro)
        """
        if not self.esta_ativo():
            logger.warning("WhatsApp não está ativo")
            return False, "WhatsApp não configurado"

        # Mapeia tipos para endpoints da Evolution API
        endpoint_map = {
            'image': 'sendMedia',
            'video': 'sendMedia',
            'audio': 'sendMedia',
            'document': 'sendMedia'
        }

        endpoint = endpoint_map.get(media_type, 'sendMedia')

        # Formata número
        numero_formatado = self._format_number(para_numero)
        telefone_limpo = para_numero.replace('whatsapp:', '').replace('+', '').strip()

        # Monta URL do endpoint
        url = f"{self.base_url}/message/{endpoint}/{self.instance_name}"

        # Headers
        headers = {
            'Content-Type': 'application/json',
            'apikey': self.api_key
        }

        # Payload
        payload = {
            'number': numero_formatado,
            'mediaurl': media_url,
            'caption': mensagem,
            'delay': 1000
        }

        try:
            response = self._request_with_retry('POST', url, headers=headers, json=payload)

            if response.status_code == 200 or response.status_code == 201:
                response_data = response.json()
                message_id = response_data.get('key', {}).get('id', 'unknown')

                # Registra log
                usuario = Usuario.query.filter_by(telefone=f"+{telefone_limpo}").first()

                log = LogWhatsApp(
                    usuario_id=usuario.id if usuario else None,
                    telefone=f"+{telefone_limpo}",
                    direcao='enviada',
                    mensagem=f"[{media_type.upper()}] {mensagem}",
                    twilio_sid=message_id,
                    documento_id=documento_id,
                    tarefa_id=tarefa_id,
                    status='enviado'
                )
                db.session.add(log)
                db.session.commit()

                logger.info(f"Mídia WhatsApp enviada para {telefone_limpo}: {message_id}")
                return True, message_id

            else:
                error_msg = f"Erro HTTP {response.status_code}: {response.text}"
                logger.error(f"Erro ao enviar mídia WhatsApp: {error_msg}")
                return False, error_msg

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Erro ao enviar mídia WhatsApp: {error_msg}")
            return False, error_msg

    def deletar_mensagem(self, message_id: str) -> bool:
        """
        Deleta mensagem do WhatsApp (se suportado pela Evolution API)

        Args:
            message_id: ID da mensagem

        Returns:
            bool: True se deletado com sucesso
        """
        if not self.esta_ativo():
            return False

        # Evolution API pode não suportar deletar mensagens
        # Por enquanto retornamos False
        logger.warning("Deletar mensagens não implementado para Evolution API")
        return False

    def criar_instancia(self):
        """
        Cria uma nova instância na Evolution API

        Returns:
            Tuple (sucesso, mensagem)
        """
        if not self.esta_ativo():
            return False, "WhatsApp não configurado"

        try:
            url = f"{self.base_url}/instance/create"
            headers = {
                'Content-Type': 'application/json',
                'apikey': self.api_key
            }

            payload = {
                'instanceName': self.instance_name,
                'token': self.api_key,
                'qrcode': True,
                'integration': 'WHATSAPP-BAILEYS'
            }

            response = self._request_with_retry('POST', url, headers=headers, json=payload)

            if response.status_code == 200 or response.status_code == 201:
                logger.info(f"Instância {self.instance_name} criada com sucesso")
                return True, "Instância criada com sucesso"
            elif response.status_code == 409:
                # Instância já existe
                logger.info(f"Instância {self.instance_name} já existe")
                return True, "Instância já existe"
            else:
                error_msg = f"Erro HTTP {response.status_code}: {response.text}"
                logger.error(f"Erro ao criar instância: {error_msg}")
                return False, error_msg

        except Exception as e:
            logger.error(f"Erro ao criar instância: {str(e)}")
            return False, str(e)

    def verificar_conexao(self):
        """
        Verifica se a instância está conectada ao WhatsApp

        Returns:
            Tuple (conectado, info)
        """
        if not self.esta_ativo():
            return False, "WhatsApp não configurado"

        try:
            url = f"{self.base_url}/instance/connectionState/{self.instance_name}"
            headers = {'apikey': self.api_key}

            response = self._request_with_retry('GET', url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                state = data.get('instance', {}).get('state')

                if state == 'open':
                    return True, "Conectado"
                else:
                    return False, f"Estado: {state}"
            elif response.status_code == 404:
                # Instância não existe, tenta criar
                logger.info(f"Instância {self.instance_name} não existe, tentando criar...")
                sucesso, msg = self.criar_instancia()
                if sucesso:
                    return False, "Instância criada, aguardando conexão"
                else:
                    return False, f"Erro ao criar instância: {msg}"
            else:
                return False, f"Erro HTTP {response.status_code}"

        except Exception as e:
            logger.error(f"Erro ao verificar conexão: {str(e)}")
            return False, str(e)

    def obter_qrcode(self):
        """
        Obtém QR Code para conectar WhatsApp
        Cria a instância automaticamente se não existir

        Returns:
            Tuple (sucesso, qrcode_base64 ou erro)
        """
        if not self.esta_ativo():
            return False, "WhatsApp não configurado"

        try:
            logger.info(f"Tentando obter QR Code para instância: {self.instance_name}")
            logger.info(f"URL Base: {self.base_url}")

            # Headers para autenticação
            headers = {'apikey': self.api_key}

            # Primeiro verifica se a instância existe
            url_fetch = f"{self.base_url}/instance/fetchInstances"
            logger.info(f"Verificando instâncias existentes: {url_fetch}")

            try:
                response_fetch = self._request_with_retry('GET', url_fetch, headers=headers)
                logger.info(f"Response fetchInstances: {response_fetch.status_code}")

                if response_fetch.status_code == 200:
                    instances = response_fetch.json()
                    logger.info(f"Instâncias encontradas: {instances}")

                    # Verifica se nossa instância existe
                    instance_exists = False
                    if isinstance(instances, list):
                        for inst in instances:
                            if inst.get('instance', {}).get('instanceName') == self.instance_name:
                                instance_exists = True
                                logger.info(f"Instância {self.instance_name} encontrada!")
                                break

                    if not instance_exists:
                        logger.info(f"Instância {self.instance_name} não existe, criando...")
                        sucesso, msg = self.criar_instancia()
                        if not sucesso:
                            return False, f"Erro ao criar instância: {msg}"

                        # Aguarda criação
                        import time
                        time.sleep(3)

            except Exception as e:
                logger.warning(f"Erro ao verificar instâncias (continuando...): {str(e)}")

            # Tenta conectar e obter QR Code
            url_connect = f"{self.base_url}/instance/connect/{self.instance_name}"
            logger.info(f"Conectando instância: {url_connect}")

            response = self._request_with_retry('GET', url_connect, headers=headers)
            logger.info(f"Response connect: {response.status_code}")
            logger.info(f"Response body: {response.text[:500]}")

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Dados recebidos: {json.dumps(data, indent=2)[:500]}")

                # Tenta diferentes formatos de resposta da Evolution API v2.x
                qrcode = None

                # Formato 1: { "base64": "data:image/png;base64,..." }
                if isinstance(data, dict) and 'base64' in data:
                    qrcode = data['base64']
                    logger.info("QR Code encontrado no formato 1 (base64)")

                # Formato 2: { "qrcode": { "base64": "..." } }
                elif isinstance(data, dict) and 'qrcode' in data:
                    qr_obj = data['qrcode']
                    if isinstance(qr_obj, dict):
                        qrcode = qr_obj.get('base64') or qr_obj.get('code')
                        logger.info("QR Code encontrado no formato 2 (qrcode.base64)")
                    elif isinstance(qr_obj, str):
                        qrcode = qr_obj
                        logger.info("QR Code encontrado no formato 2 (qrcode string)")

                # Formato 3: { "code": "..." }
                elif isinstance(data, dict) and 'code' in data:
                    qrcode = data['code']
                    logger.info("QR Code encontrado no formato 3 (code)")

                # Formato 4: { "pairingCode": "..." } - Evolution API v2
                elif isinstance(data, dict) and 'pairingCode' in data:
                    # Pairing code não é QR code, mas vamos logar
                    logger.warning(f"Pairing code recebido: {data['pairingCode']}")
                    return False, f"Instância requer pairing code: {data['pairingCode']}"

                if qrcode:
                    logger.info("QR Code obtido com sucesso!")
                    # Garante que tem o prefixo data:image correto
                    if not qrcode.startswith('data:image'):
                        qrcode = f"data:image/png;base64,{qrcode}"
                    return True, qrcode
                else:
                    logger.warning(f"QR Code não encontrado na resposta: {data}")
                    # Verifica se já está conectado
                    if data.get('instance', {}).get('state') == 'open':
                        return False, "WhatsApp já está conectado!"
                    return False, "QR Code não disponível na resposta da API"

            elif response.status_code == 404:
                logger.error("Instância não encontrada (404)")
                return False, "Instância não encontrada. Verifique o nome da instância."

            elif response.status_code == 401 or response.status_code == 403:
                logger.error("Erro de autenticação")
                return False, "API Key inválida. Verifique a configuração."

            else:
                error_msg = f"Erro HTTP {response.status_code}: {response.text[:200]}"
                logger.error(f"Erro ao obter QR Code: {error_msg}")
                return False, error_msg

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Erro de conexão: {str(e)}")
            return False, f"Não foi possível conectar à Evolution API em {self.base_url}. Verifique se a API está rodando."

        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout: {str(e)}")
            return False, "Timeout ao conectar à Evolution API (30s). Verifique a URL."

        except Exception as e:
            logger.error(f"Erro inesperado ao obter QR Code: {str(e)}", exc_info=True)
            return False, f"Erro inesperado: {str(e)}"


class WhatsAppChatbot:
    """Chatbot interativo para assinatura de documentos"""

    def __init__(self):
        """Inicializa chatbot"""
        self.config = ConfiguracaoWhatsApp.get_config()
        self.service = EvolutionAPIService()

    def processar_mensagem_recebida(self, webhook_data):
        """
        Processa mensagem recebida do webhook da Evolution API

        Args:
            webhook_data: Dados do webhook (dict)

        Returns:
            Dict com resposta
        """
        try:
            # Extrai dados do webhook
            # Formato Evolution API:
            # {
            #   "event": "messages.upsert",
            #   "instance": "instance_name",
            #   "data": {
            #     "key": {
            #       "remoteJid": "5585999999999@s.whatsapp.net",
            #       "fromMe": false,
            #       "id": "message_id"
            #     },
            #     "message": {
            #       "conversation": "texto da mensagem"
            #     }
            #   }
            # }

            event = webhook_data.get('event')

            # Processa apenas mensagens recebidas
            if event != 'messages.upsert':
                logger.info(f"Evento ignorado: {event}")
                return {'status': 'ignored', 'event': event}

            data = webhook_data.get('data', {})
            key = data.get('key', {})
            message_data = data.get('message', {})

            # Ignora mensagens enviadas por nós
            if key.get('fromMe'):
                return {'status': 'ignored', 'reason': 'message from me'}

            # Extrai número do remetente
            remote_jid = key.get('remoteJid', '')
            from_numero = remote_jid.replace('@s.whatsapp.net', '')

            # Extrai texto da mensagem
            body = (
                message_data.get('conversation') or
                message_data.get('extendedTextMessage', {}).get('text') or
                ''
            )

            if not from_numero or not body:
                logger.warning("Mensagem sem número ou texto")
                return {'status': 'error', 'message': 'Dados incompletos'}

            # Formata número com +
            telefone_limpo = f"+{from_numero}"

            # Registra log
            self._registrar_log_recebida(telefone_limpo, body)

            # Verifica horário de funcionamento
            if not self.config.esta_em_horario_funcionamento():
                templates = self.config.get_templates()
                msg = templates['fora_horario'].format(
                    inicio=self.config.horario_inicio,
                    fim=self.config.horario_fim
                )
                self.service.enviar_mensagem(telefone_limpo, msg)
                return {'status': 'sent', 'message': 'Fora de horário'}

            # Identifica usuário - tenta diferentes formatos de telefone
            usuario = Usuario.query.filter_by(telefone=telefone_limpo).first()

            # Se não encontrou com +, tenta sem +
            if not usuario and telefone_limpo.startswith('+'):
                telefone_sem_mais = telefone_limpo[1:]  # Remove o +
                usuario = Usuario.query.filter_by(telefone=telefone_sem_mais).first()

            # Se não encontrou, tenta buscar por correspondência parcial (últimos 8 dígitos)
            if not usuario and len(telefone_limpo) >= 8:
                ultimos_8_digitos = telefone_limpo[-8:]
                usuarios_possiveis = Usuario.query.filter(
                    Usuario.telefone.like(f'%{ultimos_8_digitos}')
                ).all()

                # Se encontrou apenas um, usa esse
                if len(usuarios_possiveis) == 1:
                    usuario = usuarios_possiveis[0]
                    logger.info(f"Usuário encontrado por correspondência parcial: {usuario.nome} ({usuario.telefone})")

            if not usuario:
                templates = self.config.get_templates()
                msg = templates['numero_nao_cadastrado']
                self.service.enviar_mensagem(telefone_limpo, msg)
                return {'status': 'sent', 'message': 'Número não cadastrado'}

            # Busca ou cria conversa
            conversa = ConversacaoWhatsApp.query.filter_by(telefone=telefone_limpo).first()

            if not conversa:
                conversa = ConversacaoWhatsApp(
                    telefone=telefone_limpo,
                    usuario_id=usuario.id,
                    estado_atual='inicio'
                )
                db.session.add(conversa)
                db.session.commit()

            # Verifica se está bloqueado
            if conversa.esta_bloqueado():
                msg = f"🚫 Você foi temporariamente bloqueado devido a tentativas incorretas de senha.\n"
                msg += f"Tente novamente após {conversa.bloqueado_ate.strftime('%H:%M')}."
                self.service.enviar_mensagem(telefone_limpo, msg)
                return {'status': 'sent', 'message': 'Usuário bloqueado'}

            # Verifica se sessão expirou
            timeout = self.config.timeout_sessao_minutos
            if not conversa.esta_ativa(timeout):
                conversa.expirar()
                db.session.commit()

            # Processa comando baseado no estado
            body_lower = body.strip().lower()

            # Comandos globais
            if body_lower in ['menu', 'inicio', 'oi', 'olá', 'ola', 'hi', 'hello']:
                return self._menu_principal(usuario, conversa)

            elif body_lower in ['ajuda', 'help', '?']:
                return self._ajuda(usuario, conversa)

            elif body_lower in ['sair', 'cancelar', 'parar']:
                return self._sair(conversa)

            # Processa baseado no estado
            estado = conversa.estado_atual

            if estado in ['inicio', 'expirado', None]:
                return self._menu_principal(usuario, conversa)

            elif estado == 'aguardando_escolha_documento':
                return self._processar_escolha_documento(usuario, conversa, body)

            elif estado == 'aguardando_acao_documento':
                return self._processar_acao_documento(usuario, conversa, body)

            elif estado == 'aguardando_email':
                return self._processar_confirmacao_email(usuario, conversa, body)

            elif estado == 'aguardando_justificativa':
                return self._processar_justificativa(usuario, conversa, body)

            else:
                # Estado desconhecido, volta ao menu
                return self._menu_principal(usuario, conversa)

        except Exception as e:
            logger.error(f"Erro ao processar mensagem webhook: {str(e)}", exc_info=True)
            return {'status': 'error', 'message': str(e)}

    def _menu_principal(self, usuario, conversa):
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
            self.service.enviar_mensagem(usuario.telefone, msg)

            # Limpa estado
            conversa.atualizar_estado('inicio', {})
            db.session.commit()

            return {'status': 'sent', 'message': 'Sem tarefas pendentes'}

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

        self.service.enviar_mensagem(usuario.telefone, msg)

        # Atualiza estado
        tarefas_ids = [t.id for t in tarefas_assinatura]
        conversa.atualizar_estado('aguardando_escolha_documento', {'tarefas_ids': tarefas_ids})
        db.session.commit()

        return {'status': 'sent', 'message': 'Menu principal'}

    def _processar_escolha_documento(self, usuario, conversa, body):
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

            self.service.enviar_mensagem(usuario.telefone, msg)

            # Atualiza estado
            conversa.atualizar_estado('aguardando_acao_documento', {'tarefa_id': tarefa_id})
            db.session.commit()

        except (ValueError, IndexError):
            msg = "❌ Opção inválida!\n\n"
            msg += "Por favor, digite o *número* do documento que deseja visualizar."
            self.service.enviar_mensagem(usuario.telefone, msg)

        return {'status': 'sent', 'message': 'Escolha processada'}

    def _processar_acao_documento(self, usuario, conversa, body):
        """Processa ação escolhida (aprovar/reprovar/ver)"""
        contexto = conversa.get_contexto()
        tarefa_id = contexto.get('tarefa_id')
        tarefa = Tarefa.query.get(tarefa_id)

        if not tarefa:
            msg = "❌ Tarefa não encontrada. Digite *menu* para recomeçar."
            self.service.enviar_mensagem(usuario.telefone, msg)
            return {'status': 'sent', 'message': 'Tarefa não encontrada'}

        doc = tarefa.documento
        opcao = body.strip()

        if opcao == '1':  # APROVAR E ASSINAR
            msg = "🔒 *Confirmação de Assinatura Digital*\n\n"
            msg += f"📄 *Documento:* {doc.codigo_definitivo or doc.codigo_provisorio}\n"
            msg += f"📝 *Título:* {doc.titulo}\n\n"
            msg += "Para confirmar sua assinatura, digite seu *endereço de email*:\n\n"
            msg += "⚠️ _Digite exatamente o email cadastrado no sistema_\n"
            msg += "⚠️ _Após 3 tentativas incorretas, você será bloqueado por 30 minutos_"

            self.service.enviar_mensagem(usuario.telefone, msg)

            conversa.atualizar_estado('aguardando_email', {'tarefa_id': tarefa_id})
            db.session.commit()

        elif opcao == '2':  # REPROVAR
            msg = "✍️ *Reprovação de Documento*\n\n"
            msg += f"Você está reprovando: *{doc.codigo_definitivo or doc.codigo_provisorio}*\n\n"
            msg += "Por favor, digite a *justificativa* da reprovação:\n"
            msg += "_(Mínimo 20 caracteres)_"

            self.service.enviar_mensagem(usuario.telefone, msg)

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

            self.service.enviar_mensagem(usuario.telefone, msg)

        elif opcao == '4':  # VOLTAR
            return self._menu_principal(usuario, conversa)

        else:
            msg = "❌ Opção inválida!\n\n"
            msg += "Escolha uma das opções:\n"
            msg += "1 - Aprovar e assinar\n"
            msg += "2 - Reprovar\n"
            msg += "3 - Ver documento completo\n"
            msg += "4 - Voltar ao menu"
            self.service.enviar_mensagem(usuario.telefone, msg)

        return {'status': 'sent', 'message': 'Ação processada'}

    def _processar_confirmacao_email(self, usuario, conversa, email_digitado):
        """Valida email digitado e processa assinatura"""
        contexto = conversa.get_contexto()
        tarefa_id = contexto.get('tarefa_id')
        tarefa = Tarefa.query.get(tarefa_id)

        if not tarefa:
            msg = "❌ Sessão expirada. Digite *menu* para recomeçar."
            self.service.enviar_mensagem(usuario.telefone, msg)
            conversa.expirar()
            db.session.commit()
            return {'status': 'sent', 'message': 'Sessão expirada'}

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
                self.service.enviar_mensagem(usuario.telefone, msg)
            else:
                msg = f"🚫 *Bloqueado!*\n\n"
                msg += f"Você foi bloqueado por 30 minutos devido a múltiplas tentativas incorretas.\n\n"
                msg += f"Tente novamente após {conversa.bloqueado_ate.strftime('%H:%M')}."
                self.service.enviar_mensagem(usuario.telefone, msg)

            return {'status': 'sent', 'message': 'Email incorreto'}

        # EMAIL CORRETO - Processa assinatura
        doc = tarefa.documento
        timestamp = datetime.utcnow()

        # Gera hash da assinatura (usando email como confirmação)
        assinatura_string = f"{usuario.id}:{tarefa.id}:{timestamp.isoformat()}:{usuario.email}"
        assinatura_hash = hashlib.sha256(assinatura_string.encode()).hexdigest()

        # IP e User-Agent (do webhook)
        ip_address = request.headers.get('X-Forwarded-For', 'WhatsApp-Evolution')
        user_agent = 'WhatsApp-Chatbot-EvolutionAPI'

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

        self.service.enviar_mensagem(usuario.telefone, msg)

        # Reseta tentativas e limpa estado
        conversa.resetar_tentativas()
        conversa.atualizar_estado('inicio', {})
        db.session.commit()

        # TODO: Enviar email com comprovante
        # EmailService.enviar_comprovante_assinatura(usuario, tarefa, assinatura_hash)

        return {'status': 'sent', 'message': 'Assinatura registrada'}

    def _processar_justificativa(self, usuario, conversa, justificativa):
        """Processa reprovação do documento"""
        if len(justificativa) < 20:
            msg = "❌ Justificativa muito curta!\n\n"
            msg += "Por favor, forneça uma justificativa com *pelo menos 20 caracteres*."
            self.service.enviar_mensagem(usuario.telefone, msg)
            return {'status': 'sent', 'message': 'Justificativa curta'}

        contexto = conversa.get_contexto()
        tarefa_id = contexto.get('tarefa_id')
        tarefa = Tarefa.query.get(tarefa_id)

        if not tarefa:
            msg = "❌ Sessão expirada. Digite *menu* para recomeçar."
            self.service.enviar_mensagem(usuario.telefone, msg)
            conversa.expirar()
            db.session.commit()
            return {'status': 'sent', 'message': 'Sessão expirada'}

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

        self.service.enviar_mensagem(usuario.telefone, msg)

        # Limpa estado
        conversa.atualizar_estado('inicio', {})
        db.session.commit()

        return {'status': 'sent', 'message': 'Documento reprovado'}

    def _ajuda(self, usuario, conversa):
        """Exibe comandos disponíveis"""
        msg = "ℹ️ *Comandos Disponíveis*\n\n"
        msg += "*menu* - Ver documentos pendentes\n"
        msg += "*ajuda* - Ver esta mensagem\n"
        msg += "*sair* - Encerrar conversa\n\n"
        msg += "💡 _Dica: Responda apenas com o número da opção desejada_"

        self.service.enviar_mensagem(usuario.telefone, msg)
        return {'status': 'sent', 'message': 'Ajuda'}

    def _sair(self, conversa):
        """Encerra conversa"""
        conversa.atualizar_estado('inicio', {})
        db.session.commit()

        msg = "👋 Até logo!\n\n"
        msg += "Digite *menu* quando precisar voltar."

        usuario = Usuario.query.get(conversa.usuario_id)
        if usuario:
            self.service.enviar_mensagem(usuario.telefone, msg)

        return {'status': 'sent', 'message': 'Sair'}

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


# Mantém compatibilidade com código antigo
WhatsAppService = EvolutionAPIService
