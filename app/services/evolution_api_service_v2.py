"""
Serviço de Integração com Evolution API v2.x
Refatorado completamente baseado na documentação oficial

Evolution API Version: 2.2.2
Data: 21/11/2024
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

logger = logging.getLogger(__name__)


class EvolutionAPIv2:
    """
    Cliente para Evolution API v2.x

    Baseado na documentação oficial da Evolution API v2.2.2
    Implementa retry automático, logging detalhado e tratamento de erros
    """

    def __init__(self):
        """Inicializa o cliente com configurações do banco de dados"""
        self.config = ConfiguracaoWhatsApp.get_config()

        # Configurações da Evolution API
        self.base_url = self.config.evolution_api_url
        self.instance_name = self.config.evolution_instance_name
        self.api_key = self.config.evolution_api_key

        # Configurações de retry
        self.max_retries = 3
        self.timeout = 30
        self.retry_delay = 2

    # ========================================================================
    # MÉTODOS AUXILIARES
    # ========================================================================

    def esta_ativo(self) -> bool:
        """Verifica se WhatsApp está ativo e configurado"""
        return bool(
            self.config.ativo and
            self.base_url and
            self.instance_name and
            self.api_key
        )

    def _get_headers(self, content_type: str = None) -> Dict[str, str]:
        """Retorna headers padrão para requisições"""
        headers = {'apikey': self.api_key}

        if content_type:
            headers['Content-Type'] = content_type

        return headers

    def _request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> requests.Response:
        """
        Executa requisição HTTP com retry automático

        Args:
            method: Método HTTP (GET, POST, DELETE)
            url: URL completa
            **kwargs: Argumentos adicionais (headers, json, timeout)

        Returns:
            Response object

        Raises:
            requests.exceptions.RequestException: Se todas as tentativas falharem
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"[Attempt {attempt + 1}/{self.max_retries}] {method} {url}")

                response = requests.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    **kwargs
                )

                logger.debug(f"Response: {response.status_code}")
                return response

            except requests.exceptions.Timeout as e:
                last_exception = e
                logger.warning(f"Timeout na tentativa {attempt + 1}/{self.max_retries}")

                if attempt < self.max_retries - 1:
                    sleep_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.debug(f"Aguardando {sleep_time}s antes de retry...")
                    time.sleep(sleep_time)
                continue

            except requests.exceptions.ConnectionError as e:
                last_exception = e
                logger.warning(f"Erro de conexão na tentativa {attempt + 1}/{self.max_retries}")

                if attempt < self.max_retries - 1:
                    sleep_time = self.retry_delay * (2 ** attempt)
                    time.sleep(sleep_time)
                continue

            except requests.exceptions.RequestException as e:
                logger.error(f"Erro não recuperável: {str(e)}")
                raise

        # Todas as tentativas falharam
        logger.error(f"Falha após {self.max_retries} tentativas")
        raise last_exception

    def _format_number(self, numero: str) -> str:
            """
            Formata número para Evolution API (Apenas dígitos para V2)
            Args:
                numero: +5585999999999 ou 5585999999999
            Returns:
                5585999999999
            """
            # Remove tudo que não for dígito
            if not numero:
                return ""
                
            # Remove sufixos e prefixos comuns
            numero_limpo = str(numero).replace('whatsapp:', '').replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
            numero_limpo = numero_limpo.replace('@s.whatsapp.net', '').strip()

            return numero_limpo

    # ========================================================================
    # GESTÃO DE INSTÂNCIAS
    # ========================================================================

    def criar_instancia(self) -> Tuple[bool, str]:
        """
        Cria nova instância na Evolution API

        Returns:
            (sucesso, mensagem)
        """
        if not self.esta_ativo():
            return False, "WhatsApp não configurado"

        try:
            url = f"{self.base_url}/instance/create"
            headers = self._get_headers('application/json')

            payload = {
                'instanceName': self.instance_name,
                'token': self.api_key,
                'qrcode': True,
                'integration': 'WHATSAPP-BAILEYS'
            }

            logger.info(f"Criando instância: {self.instance_name}")

            response = self._request_with_retry('POST', url, headers=headers, json=payload)

            if response.status_code in [200, 201]:
                data = response.json()
                logger.info(f"✓ Instância criada: {self.instance_name}")
                return True, "Instância criada com sucesso"

            elif response.status_code == 409:
                logger.info(f"Instância já existe: {self.instance_name}")
                return True, "Instância já existe"

            elif response.status_code == 403:
                # Verifica se o erro é por instância já existir
                response_text = response.text.lower()
                if "already in use" in response_text or "já existe" in response_text:
                    logger.info(f"Instância já existe (403): {self.instance_name}")
                    return True, "Instância já existe"
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                    logger.error(f"Erro de permissão ao criar instância: {error_msg}")
                    return False, error_msg

            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                logger.error(f"Erro ao criar instância: {error_msg}")
                return False, error_msg

        except Exception as e:
            logger.error(f"Exceção ao criar instância: {str(e)}", exc_info=True)
            return False, str(e)

    def listar_instancias(self) -> Tuple[bool, Any]:
        """
        Lista todas as instâncias

        Returns:
            (sucesso, lista ou erro)
        """
        if not self.esta_ativo():
            return False, "WhatsApp não configurado"

        try:
            url = f"{self.base_url}/instance/fetchInstances"
            headers = self._get_headers()

            logger.debug(f"Listando instâncias")

            response = self._request_with_retry('GET', url, headers=headers)

            if response.status_code == 200:
                instances = response.json()
                logger.info(f"✓ {len(instances) if isinstance(instances, list) else 0} instância(s) encontrada(s)")
                return True, instances
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                logger.error(f"Erro ao listar instâncias: {error_msg}")
                return False, error_msg

        except Exception as e:
            logger.error(f"Exceção ao listar instâncias: {str(e)}")
            return False, str(e)

    def verificar_conexao(self) -> Tuple[bool, str]:
        """
        Verifica status da conexão WhatsApp

        Returns:
            (conectado, informação)
        """
        if not self.esta_ativo():
            return False, "WhatsApp não configurado"

        try:
            url = f"{self.base_url}/instance/connectionState/{self.instance_name}"
            headers = self._get_headers()

            logger.debug(f"Verificando status da instância: {self.instance_name}")

            response = self._request_with_retry('GET', url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                state = data.get('instance', {}).get('state', 'unknown')

                logger.info(f"Status da instância: {state}")

                if state == 'open':
                    return True, "Conectado"
                elif state == 'close':
                    return False, "Desconectado"
                elif state == 'connecting':
                    return False, "Conectando..."
                else:
                    return False, f"Estado desconhecido: {state}"

            elif response.status_code == 404:
                logger.warning("Instância não encontrada")
                return False, "Instância não existe"

            else:
                error_msg = f"HTTP {response.status_code}"
                logger.error(f"Erro ao verificar conexão: {error_msg}")
                return False, error_msg

        except Exception as e:
            logger.error(f"Exceção ao verificar conexão: {str(e)}")
            return False, str(e)

    def obter_qrcode(self) -> Tuple[bool, str]:
        """
        Obtém QR Code para conectar WhatsApp

        Fluxo:
        1. Verifica se instância existe
        2. Se não existe, cria automaticamente
        3. Conecta e obtém QR Code
        4. Retorna QR Code em base64 ou mensagem de erro

        Returns:
            (sucesso, qrcode_base64 ou erro)
        """
        if not self.esta_ativo():
            return False, "WhatsApp não configurado. Preencha URL, Nome da Instância e API Key."

        try:
            logger.info(f"=== OBTENDO QR CODE ===")
            logger.info(f"Instância: {self.instance_name}")
            logger.info(f"URL: {self.base_url}")

            # Passo 1: Verifica se instância existe
            sucesso, instances = self.listar_instancias()

            if not sucesso:
                if "403" in str(instances) or "Access denied" in str(instances):
                    return False, "API Key inválida. Verifique se a API Key está correta no arquivo .env da Evolution API."
                return False, f"Erro ao verificar instâncias: {instances}"

            # Verifica se nossa instância existe
            instance_exists = False
            if isinstance(instances, list):
                for inst in instances:
                    if inst.get('instance', {}).get('instanceName') == self.instance_name:
                        instance_exists = True
                        state = inst.get('instance', {}).get('status') or inst.get('state')
                        logger.info(f"✓ Instância encontrada - Estado: {state}")

                        # Se já está conectada
                        if state == 'open':
                            return False, "WhatsApp já está conectado!"
                        break

            # Passo 2: Se não existe, cria
            if not instance_exists:
                logger.info("Instância não existe, criando...")
                sucesso, msg = self.criar_instancia()

                if not sucesso:
                    return False, f"Erro ao criar instância: {msg}"

                logger.info("✓ Instância criada, aguardando 3s...")
                time.sleep(3)

            # Passo 3: Conecta e obtém QR Code
            url = f"{self.base_url}/instance/connect/{self.instance_name}"
            headers = self._get_headers()

            logger.info(f"Solicitando QR Code: GET {url}")

            response = self._request_with_retry('GET', url, headers=headers)

            logger.info(f"Response Status: {response.status_code}")
            logger.debug(f"Response Body (primeiros 500 chars): {response.text[:500]}")

            # Passo 4: Processa resposta
            if response.status_code == 200:
                data = response.json()

                # Tenta extrair QR Code de diferentes formatos
                qrcode = None

                # Formato 1: { "base64": "data:image..." }
                if 'base64' in data:
                    qrcode = data['base64']
                    logger.info("✓ QR Code encontrado (formato: base64 direto)")

                # Formato 2: { "qrcode": { "base64": "..." } }
                elif 'qrcode' in data:
                    qr_obj = data['qrcode']
                    if isinstance(qr_obj, dict):
                        qrcode = qr_obj.get('base64') or qr_obj.get('code')
                        logger.info("✓ QR Code encontrado (formato: qrcode.base64)")
                    elif isinstance(qr_obj, str):
                        qrcode = qr_obj
                        logger.info("✓ QR Code encontrado (formato: qrcode string)")

                # Formato 3: { "code": "..." }
                elif 'code' in data:
                    qrcode = data['code']
                    logger.info("✓ QR Code encontrado (formato: code)")

                # Formato 4: Pairing code (não é QR Code)
                elif 'pairingCode' in data:
                    pairing_code = data['pairingCode']
                    logger.warning(f"Pairing code recebido: {pairing_code}")
                    return False, f"Instância requer pairing code: {pairing_code}"

                # Formato 5: Já conectado
                elif data.get('instance', {}).get('state') == 'open':
                    logger.info("WhatsApp já conectado")
                    return False, "WhatsApp já está conectado!"

                if qrcode:
                    # Garante prefixo data:image
                    if not qrcode.startswith('data:image'):
                        qrcode = f"data:image/png;base64,{qrcode}"

                    logger.info(f"✓ QR Code retornado ({len(qrcode)} chars)")
                    return True, qrcode
                else:
                    logger.warning(f"QR Code não encontrado na resposta")
                    logger.debug(f"Resposta completa: {json.dumps(data, indent=2)[:1000]}")
                    return False, "QR Code não disponível na resposta da API. A instância pode já estar conectada."

            elif response.status_code == 404:
                logger.error("Instância não encontrada (404)")
                return False, "Instância não encontrada. Tente novamente."

            elif response.status_code in [401, 403]:
                logger.error("Erro de autenticação (401/403)")
                return False, "API Key inválida. Verifique a configuração."

            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                logger.error(f"Erro inesperado: {error_msg}")
                return False, error_msg

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Erro de conexão: {str(e)}")
            return False, f"Não foi possível conectar em {self.base_url}. Verifique se a Evolution API está rodando."

        except requests.exceptions.Timeout:
            logger.error("Timeout na requisição")
            return False, f"Timeout ao conectar (30s). Verifique a URL: {self.base_url}"

        except Exception as e:
            logger.error(f"Exceção ao obter QR Code: {str(e)}", exc_info=True)
            return False, f"Erro inesperado: {str(e)}"

    def deletar_instancia(self) -> Tuple[bool, str]:
        """
        Deleta a instância

        Returns:
            (sucesso, mensagem)
        """
        if not self.esta_ativo():
            return False, "WhatsApp não configurado"

        try:
            url = f"{self.base_url}/instance/delete/{self.instance_name}"
            headers = self._get_headers()

            logger.info(f"Deletando instância: {self.instance_name}")

            response = self._request_with_retry('DELETE', url, headers=headers)

            if response.status_code == 200:
                logger.info(f"✓ Instância deletada")
                return True, "Instância deletada com sucesso"
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                logger.error(f"Erro ao deletar: {error_msg}")
                return False, error_msg

        except Exception as e:
            logger.error(f"Exceção ao deletar instância: {str(e)}")
            return False, str(e)

    # ========================================================================
    # ENVIO DE MENSAGENS
    # ========================================================================

    def enviar_mensagem(
        self,
        para_numero: str,
        mensagem: str,
        documento_id: Optional[int] = None,
        tarefa_id: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Envia mensagem de texto via WhatsApp

        Args:
            para_numero: +5585999999999 ou 5585999999999
            mensagem: Texto da mensagem
            documento_id: ID do documento (opcional)
            tarefa_id: ID da tarefa (opcional)

        Returns:
            (sucesso, message_id ou erro)
        """
        if not self.esta_ativo():
            logger.warning("WhatsApp não configurado")
            return False, "WhatsApp não configurado"

        try:
            # Formata número
            numero_formatado = self._format_number(para_numero)
            telefone_limpo = para_numero.replace('whatsapp:', '').replace('+', '').strip()

            # Monta requisição
            url = f"{self.base_url}/message/sendText/{self.instance_name}"
            headers = self._get_headers('application/json')

            payload = {
                'number': numero_formatado,
                'text': mensagem,
                'delay': 1000
            }

            logger.info(f"Enviando mensagem para {telefone_limpo}")
            logger.debug(f"Payload: {json.dumps(payload, indent=2)}")

            response = self._request_with_retry('POST', url, headers=headers, json=payload)

            if response.status_code in [200, 201]:
                data = response.json()
                message_id = data.get('key', {}).get('id', 'unknown')

                logger.info(f"✓ Mensagem enviada: {message_id}")

                # Registra log
                usuario = Usuario.query.filter_by(telefone=f"+{telefone_limpo}").first()

                log = LogWhatsApp(
                    usuario_id=usuario.id if usuario else None,
                    telefone=f"+{telefone_limpo}",
                    direcao='enviada',
                    mensagem=mensagem,
                    twilio_sid=message_id,
                    documento_id=documento_id,
                    tarefa_id=tarefa_id,
                    status='enviado'
                )
                db.session.add(log)
                db.session.commit()

                return True, message_id

            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                logger.error(f"Erro ao enviar mensagem: {error_msg}")

                # Registra erro
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
            logger.error(f"Exceção ao enviar mensagem: {error_msg}", exc_info=True)

            # Registra erro
            telefone_limpo = para_numero.replace('whatsapp:', '').replace('+', '').strip()
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

    def enviar_notificacao_tarefa(self, usuario: Usuario, tarefa: Tarefa) -> Tuple[bool, str]:
        """
        Envia notificação de nova tarefa via WhatsApp

        Args:
            usuario: Objeto Usuario
            tarefa: Objeto Tarefa

        Returns:
            (sucesso, mensagem)
        """
        if not self.config.usar_para_notificacoes:
            return False, "Notificações WhatsApp desativadas"

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


# Alias para compatibilidade com código antigo
EvolutionAPIService = EvolutionAPIv2
WhatsAppService = EvolutionAPIv2
class WhatsAppChatbot:
    """
    Classe responsável por processar mensagens recebidas (Webhook)
    e gerenciar o fluxo de conversa (Chatbot)
    """
    def __init__(self):
        self.api = EvolutionAPIv2()
        self.config = ConfiguracaoWhatsApp.get_config()

    def _buscar_usuario_inteligente(self, remote_jid):
        """
        Busca usuário no banco tentando vários formatos de telefone.
        """
        if not remote_jid:
            return None

        # 1. Limpa o JID (remove @s.whatsapp.net, @lid e caracteres não numéricos)
        telefone_limpo = ''.join(filter(str.isdigit, str(remote_jid).split('@')[0]))
        
        # Se o telefone for muito curto (ex: ID técnico estranho), ignora
        if len(telefone_limpo) < 8:
            return None

        # Lista de formatos para tentar buscar no banco
        tentativas = [
            telefone_limpo,              # Ex: 558592231683
            f"+{telefone_limpo}"         # Ex: +558592231683
        ]

        # Lógica do 9º Dígito para Brasil (DDI 55)
        if len(telefone_limpo) == 12 and telefone_limpo.startswith('55'):
            # Tem 12 digitos (sem 9), tenta ADICIONAR o 9
            com_9 = f"{telefone_limpo[:4]}9{telefone_limpo[4:]}"
            tentativas.append(com_9)
            tentativas.append(f"+{com_9}")
        
        elif len(telefone_limpo) == 13 and telefone_limpo.startswith('55'):
            # Tem 13 digitos (com 9), tenta REMOVER o 9 (caso o banco esteja antigo)
            sem_9 = f"{telefone_limpo[:4]}{telefone_limpo[5:]}"
            tentativas.append(sem_9)
            tentativas.append(f"+{sem_9}")

        logger.info(f"Buscando usuário. JID: {remote_jid} | Tentativas: {tentativas}")

        # Tenta encontrar o usuário com qualquer um dos formatos
        for t in tentativas:
            usuario = Usuario.query.filter_by(telefone=t).first()
            if usuario:
                logger.info(f"✓ Usuário encontrado: {usuario.nome} (ID: {usuario.id}) pelo telefone {t}")
                return usuario
        
        logger.warning(f"❌ Usuário não encontrado nas tentativas: {tentativas}")
        return None

    def processar_mensagem_recebida(self, data):
        """
        Processa o webhook recebido da Evolution API
        """
        try:
            # Extrai dados básicos do JSON
            event_type = data.get('event')
            payload = data.get('data')

            if event_type != 'messages.upsert':
                return {'status': 'ignored', 'reason': 'not a message upsert'}

            # Garante que payload é dicionário
            msg_data = payload if isinstance(payload, dict) else {}
            key = msg_data.get('key', {})
            
            # --- CORREÇÃO CRÍTICA PARA LID (WHATSAPP WEB) ---
            remote_jid = key.get('remoteJid')
            remote_jid_alt = key.get('remoteJidAlt') # <--- O NÚMERO REAL ESTÁ AQUI QUANDO USA WEB
            
            # Se existir um ID alternativo e ele for um número de celular padrão (@s.whatsapp.net), usa ele
            jid_para_busca = remote_jid
            if remote_jid_alt and 's.whatsapp.net' in str(remote_jid_alt):
                logger.info(f"Detectado ID de dispositivo vinculado (LID). Trocando {remote_jid} por {remote_jid_alt}")
                jid_para_busca = remote_jid_alt
            # -------------------------------------------------

            from_me = key.get('fromMe', False)
            if from_me:
                return {'status': 'ignored', 'reason': 'from me'}

            # Extrai o texto da mensagem
            message_content = msg_data.get('message', {})
            texto = (
                message_content.get('conversation') or 
                message_content.get('extendedTextMessage', {}).get('text') or
                ''
            ).strip()

            if not texto:
                return {'status': 'ignored', 'reason': 'no text content'}

            logger.info(f"Mensagem recebida de {jid_para_busca}: {texto}")

            # ============================================================
            # BUSCA O USUÁRIO USANDO O JID CORRIGIDO
            # ============================================================
            usuario = self._buscar_usuario_inteligente(jid_para_busca)

            if not usuario:
                # Se não achar, envia aviso para o remetente original
                # msg_erro = "❌ Número não cadastrado no sistema GED."
                # self.api.enviar_mensagem(remote_jid, msg_erro)
                return {'status': 'error', 'message': 'User not found'}

            # Log da mensagem recebida no banco (salva com o telefone do cadastro)
            try:
                log = LogWhatsApp(
                    usuario_id=usuario.id,
                    telefone=usuario.telefone, 
                    direcao='recebida',
                    mensagem=texto,
                    twilio_sid=key.get('id'),
                    status='recebido'
                )
                db.session.add(log)
                db.session.commit()
            except Exception as e:
                logger.error(f"Erro ao salvar log: {e}")
                db.session.rollback()

            # ============================================================
            # GERENCIAMENTO DE SESSÃO/CONVERSAÇÃO
            # ============================================================
            conversacao = self._obter_ou_criar_conversacao(usuario, jid_para_busca)

            # Verifica se sessão expirou
            timeout = self.config.timeout_sessao_minutos or 15
            if conversacao.estado_atual and not conversacao.esta_ativa(timeout):
                conversacao.expirar()
                db.session.commit()

            # Verifica se usuário está bloqueado
            if conversacao.esta_bloqueado():
                self.api.enviar_mensagem(remote_jid, "⏳ *Muitas tentativas incorretas.*\n\nTente novamente em 30 minutos.")
                return {'status': 'blocked'}

            # ============================================================
            # LÓGICA DO CHATBOT COM ESTADOS
            # ============================================================
            texto_lower = texto.lower().strip()
            estado = conversacao.estado_atual or 'menu'

            # Comandos que sempre resetam para o menu
            if texto_lower in ['menu', 'oi', 'olá', 'ola', 'inicio', 'start', 'ajuda', 'm', 'voltar', '0', 'sair']:
                conversacao.atualizar_estado('menu', {})
                db.session.commit()
                self._enviar_menu_principal(usuario, remote_jid)

            # Estado: MENU PRINCIPAL
            elif estado == 'menu':
                if texto_lower in ['tarefas', '1', 'um']:
                    self._listar_tarefas(usuario, remote_jid, conversacao)
                elif texto_lower in ['documentos', '2', 'dois']:
                    self.api.enviar_mensagem(remote_jid, "📂 *Meus Documentos*\n\nEsta funcionalidade estará disponível em breve.\n\n_Responda *menu* para voltar._")
                else:
                    self._enviar_menu_principal(usuario, remote_jid)

            # Estado: AGUARDANDO SELEÇÃO DE TAREFA
            elif estado == 'aguardando_selecao':
                self._processar_selecao_tarefa(usuario, remote_jid, texto, conversacao)

            # Estado: AGUARDANDO AÇÃO NO DOCUMENTO
            elif estado == 'aguardando_acao':
                self._processar_acao_documento(usuario, remote_jid, texto, conversacao)

            # Estado: AGUARDANDO EMAIL PARA CONFIRMAÇÃO
            elif estado == 'aguardando_email':
                self._processar_email(usuario, remote_jid, texto, conversacao)

            # Estado: AGUARDANDO JUSTIFICATIVA DE REPROVAÇÃO
            elif estado == 'aguardando_justificativa':
                self._processar_justificativa(usuario, remote_jid, texto, conversacao)

            # Estado desconhecido - volta ao menu
            else:
                conversacao.atualizar_estado('menu', {})
                db.session.commit()
                self._enviar_menu_principal(usuario, remote_jid)

            return {'status': 'success'}

        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}", exc_info=True)
            return {'status': 'error', 'message': str(e)}

    def _obter_ou_criar_conversacao(self, usuario, telefone_jid):
        """Obtém ou cria uma conversação para o usuário"""
        # Limpa o JID para salvar apenas o número (max 20 chars)
        telefone_limpo = ''.join(filter(str.isdigit, str(telefone_jid).split('@')[0]))[:20]

        conversacao = ConversacaoWhatsApp.query.filter_by(usuario_id=usuario.id).first()

        if not conversacao:
            conversacao = ConversacaoWhatsApp(
                telefone=telefone_limpo,
                usuario_id=usuario.id,
                estado_atual='menu'
            )
            db.session.add(conversacao)
            db.session.commit()
        else:
            # Atualiza telefone caso tenha mudado
            conversacao.telefone = telefone_limpo
            conversacao.ultima_mensagem_em = datetime.utcnow()
            db.session.commit()

        return conversacao

    def _enviar_menu_principal(self, usuario, remote_jid):
        """Envia o menu principal"""
        total_tarefas = Tarefa.query.filter_by(
            responsavel_id=usuario.id,
            data_conclusao=None
        ).count()

        msg_menu = f"📋 *Olá, {usuario.nome}!*\n\n"
        msg_menu += f"Você tem *{total_tarefas}* tarefa(s) pendente(s).\n\n"
        msg_menu += "1️⃣ Ver Tarefas Pendentes\n"
        msg_menu += "2️⃣ Meus Documentos\n\n"
        msg_menu += "_Responda com o número da opção._"

        self.api.enviar_mensagem(remote_jid, msg_menu)

    def _listar_tarefas(self, usuario, remote_jid, conversacao):
        """Lista tarefas com numeração para seleção"""
        tarefas = Tarefa.query.filter_by(
            responsavel_id=usuario.id,
            data_conclusao=None
        ).order_by(Tarefa.prazo.asc()).limit(10).all()

        if not tarefas:
            self.api.enviar_mensagem(remote_jid, "✅ *Tudo limpo!*\n\nVocê não possui tarefas pendentes.\n\n_Responda *menu* para voltar._")
            conversacao.atualizar_estado('menu', {})
            db.session.commit()
            return

        # Guarda lista de tarefas no contexto
        tarefas_ids = [t.id for t in tarefas]
        conversacao.atualizar_estado('aguardando_selecao', {'tarefas_ids': tarefas_ids})
        db.session.commit()

        msg = "📋 *Suas Tarefas Pendentes:*\n\n"
        for idx, t in enumerate(tarefas, 1):
            prazo = t.prazo.strftime('%d/%m') if t.prazo else 'S/ Prazo'
            doc = t.documento
            codigo = doc.codigo_definitivo or doc.codigo_provisorio or f"Doc #{doc.id}"
            # Título formatado: CODIGO - TITULO
            titulo_formatado = f"{codigo} - {doc.titulo}" if doc.titulo else codigo
            bloco_info = ""
            metadata = t.get_metadata()
            if metadata.get('bloco_id'):
                bloco_info = f" [Bloco #{metadata.get('bloco_id')}]"
            msg += f"*{idx}.* {titulo_formatado}{bloco_info}\n"
            msg += f"    📋 {t.tipo_tarefa} | 📅 Prazo: {prazo}\n\n"

        msg += "💬 *Responda o número da tarefa* para ver detalhes e assinar.\n"
        msg += "_Ou responda *0* para voltar ao menu._"
        self.api.enviar_mensagem(remote_jid, msg)

    def _processar_selecao_tarefa(self, usuario, remote_jid, texto, conversacao):
        """Processa a seleção de uma tarefa pelo número"""
        contexto = conversacao.get_contexto()
        tarefas_ids = contexto.get('tarefas_ids', [])

        try:
            numero = int(texto.strip())
            if numero < 1 or numero > len(tarefas_ids):
                self.api.enviar_mensagem(remote_jid, f"❌ Opção inválida. Digite um número de 1 a {len(tarefas_ids)}.\n\n_Ou responda *0* para voltar._")
                return

            tarefa_id = tarefas_ids[numero - 1]
            tarefa = Tarefa.query.get(tarefa_id)

            if not tarefa:
                self.api.enviar_mensagem(remote_jid, "❌ Tarefa não encontrada.\n\n_Responda *menu* para voltar._")
                conversacao.atualizar_estado('menu', {})
                db.session.commit()
                return

            self._mostrar_detalhes_tarefa(usuario, remote_jid, tarefa, conversacao)

        except ValueError:
            self.api.enviar_mensagem(remote_jid, "❌ Por favor, digite apenas o *número* da tarefa.\n\n_Ou responda *0* para voltar._")

    def _mostrar_detalhes_tarefa(self, usuario, remote_jid, tarefa, conversacao):
        """Mostra detalhes da tarefa e opções de ação"""
        doc = tarefa.documento
        codigo = doc.codigo_definitivo or doc.codigo_provisorio or f"Doc #{doc.id}"
        prazo = tarefa.prazo.strftime('%d/%m/%Y') if tarefa.prazo else 'Sem prazo'
        autor = doc.criador.nome if doc.criador else 'N/A'

        # Título formatado: CODIGO - TITULO
        titulo_formatado = f"{codigo} - {doc.titulo}" if doc.titulo else codigo

        # Atualiza contexto com a tarefa selecionada
        conversacao.atualizar_estado('aguardando_acao', {
            'tarefa_id': tarefa.id,
            'documento_id': doc.id,
            'tipo_tarefa': tarefa.tipo_tarefa
        })
        db.session.commit()

        msg = f"📄 *{titulo_formatado}*\n\n"
        msg += f"👤 *Autor:* {autor}\n"
        msg += f"📋 *Tarefa:* {tarefa.tipo_tarefa}\n"
        msg += f"⏰ *Prazo:* {prazo}\n\n"

        msg += "━━━━━━━━━━━━━━━━━━━━━\n"
        msg += "*O que deseja fazer?*\n\n"

        # Opções baseadas no tipo de tarefa
        if 'Assinar Documento' in tarefa.tipo_tarefa:
            # Tarefas de assinatura
            msg += "1️⃣ *Aprovar e Assinar*\n"
            msg += "2️⃣ *Reprovar*\n"
            msg += "3️⃣ *Ver Resumo do Documento*\n"
        elif tarefa.tipo_tarefa == 'Validar e Codificar Documento':
            # Tarefas de validação/codificação
            msg += "1️⃣ *Validar e Prosseguir* (usar código atual)\n"
            msg += "2️⃣ *Devolver para Correção*\n"
            msg += "3️⃣ *Ver Resumo do Documento*\n"
        elif tarefa.tipo_tarefa == 'Publicar Documento Aprovado':
            # Tarefas de publicação
            msg += "1️⃣ *Publicar Documento* ✅\n"
            msg += "2️⃣ *Devolver para Revisão*\n"
            msg += "3️⃣ *Ver Resumo do Documento*\n"
        else:
            # Outras tarefas (genérico)
            msg += "1️⃣ *Concluir Tarefa*\n"
            msg += "2️⃣ *Ver Resumo do Documento*\n"

        msg += "4️⃣ *Voltar às tarefas*\n"
        msg += "0️⃣ *Menu principal*\n\n"
        msg += "_Responda com o número da opção._"

        self.api.enviar_mensagem(remote_jid, msg)

    def _processar_acao_documento(self, usuario, remote_jid, texto, conversacao):
        """Processa a ação escolhida para o documento"""
        contexto = conversacao.get_contexto()
        tarefa_id = contexto.get('tarefa_id')
        tipo_tarefa = contexto.get('tipo_tarefa', '')

        texto_limpo = texto.strip().lower()

        # Opções comuns
        if texto_limpo in ['4', 'voltar']:
            self._listar_tarefas(usuario, remote_jid, conversacao)
            return

        # Roteamento baseado no tipo de tarefa
        if 'Assinar Documento' in tipo_tarefa:
            # FLUXO DE ASSINATURA
            if texto_limpo in ['1', 'aprovar', 'assinar']:
                self._iniciar_confirmacao_email(usuario, remote_jid, tarefa_id, 'aprovar', conversacao)
            elif texto_limpo in ['2', 'reprovar']:
                self._iniciar_justificativa(usuario, remote_jid, tarefa_id, conversacao)
            elif texto_limpo in ['3', 'resumo']:
                self._mostrar_resumo_documento(usuario, remote_jid, tarefa_id, conversacao)
            else:
                self.api.enviar_mensagem(remote_jid, "❌ Opção inválida.\n\nEscolha: *1* (Aprovar), *2* (Reprovar), *3* (Resumo), *4* (Voltar) ou *0* (Menu)")

        elif tipo_tarefa == 'Validar e Codificar Documento':
            # FLUXO DE VALIDAÇÃO/CODIFICAÇÃO
            if texto_limpo in ['1', 'validar']:
                self._iniciar_confirmacao_email(usuario, remote_jid, tarefa_id, 'validar', conversacao)
            elif texto_limpo in ['2', 'devolver']:
                self._iniciar_justificativa_devolucao(usuario, remote_jid, tarefa_id, conversacao)
            elif texto_limpo in ['3', 'resumo']:
                self._mostrar_resumo_documento(usuario, remote_jid, tarefa_id, conversacao)
            else:
                self.api.enviar_mensagem(remote_jid, "❌ Opção inválida.\n\nEscolha: *1* (Validar), *2* (Devolver), *3* (Resumo), *4* (Voltar) ou *0* (Menu)")

        elif tipo_tarefa == 'Publicar Documento Aprovado':
            # FLUXO DE PUBLICAÇÃO
            if texto_limpo in ['1', 'publicar']:
                self._iniciar_confirmacao_email(usuario, remote_jid, tarefa_id, 'publicar', conversacao)
            elif texto_limpo in ['2', 'devolver']:
                self._iniciar_justificativa_devolucao(usuario, remote_jid, tarefa_id, conversacao)
            elif texto_limpo in ['3', 'resumo']:
                self._mostrar_resumo_documento(usuario, remote_jid, tarefa_id, conversacao)
            else:
                self.api.enviar_mensagem(remote_jid, "❌ Opção inválida.\n\nEscolha: *1* (Publicar), *2* (Devolver), *3* (Resumo), *4* (Voltar) ou *0* (Menu)")

        else:
            # FLUXO GENÉRICO
            if texto_limpo in ['1', 'concluir']:
                self._iniciar_confirmacao_email(usuario, remote_jid, tarefa_id, 'concluir', conversacao)
            elif texto_limpo in ['2', 'resumo']:
                self._mostrar_resumo_documento(usuario, remote_jid, tarefa_id, conversacao)
            else:
                self.api.enviar_mensagem(remote_jid, "❌ Opção inválida.\n\nEscolha: *1* (Concluir), *2* (Resumo), *4* (Voltar) ou *0* (Menu)")

    def _iniciar_confirmacao_email(self, usuario, remote_jid, tarefa_id, acao, conversacao):
        """Inicia fluxo de confirmação por email"""
        conversacao.atualizar_estado('aguardando_email', {
            'tarefa_id': tarefa_id,
            'acao': acao
        })
        db.session.commit()

        email_dica = self._ocultar_email(usuario.email)
        acao_texto = {
            'aprovar': 'Assinatura',
            'validar': 'Validação',
            'publicar': 'Publicação',
            'concluir': 'Conclusão'
        }.get(acao, 'Ação')

        msg = f"🔒 *Confirmação de {acao_texto}*\n\n"
        msg += f"Para confirmar, digite seu *email cadastrado*.\n"
        msg += f"💡 Dica: {email_dica}\n\n"
        msg += "_Responda *0* para cancelar._"
        self.api.enviar_mensagem(remote_jid, msg)

    def _iniciar_justificativa(self, usuario, remote_jid, tarefa_id, conversacao):
        """Inicia fluxo de justificativa para reprovação"""
        conversacao.atualizar_estado('aguardando_justificativa', {
            'tarefa_id': tarefa_id,
            'acao': 'reprovar'
        })
        db.session.commit()

        msg = "📝 *Reprovação de Documento*\n\n"
        msg += "Por favor, digite o *motivo da reprovação*.\n\n"
        msg += "_Responda *0* para cancelar._"
        self.api.enviar_mensagem(remote_jid, msg)

    def _iniciar_justificativa_devolucao(self, usuario, remote_jid, tarefa_id, conversacao):
        """Inicia fluxo de justificativa para devolução"""
        conversacao.atualizar_estado('aguardando_justificativa', {
            'tarefa_id': tarefa_id,
            'acao': 'devolver'
        })
        db.session.commit()

        msg = "📝 *Devolução de Documento*\n\n"
        msg += "Por favor, digite o *motivo da devolução*.\n\n"
        msg += "_Responda *0* para cancelar._"
        self.api.enviar_mensagem(remote_jid, msg)

    def _ocultar_email(self, email):
        """Oculta parte do email para mostrar como dica"""
        if not email or '@' not in email:
            return '***@***.***'

        partes = email.split('@')
        usuario = partes[0]
        dominio = partes[1]

        # Mostra primeiros 2 chars e últimos 2 do usuário
        if len(usuario) > 4:
            usuario_oculto = usuario[:2] + '*' * (len(usuario) - 4) + usuario[-2:]
        else:
            usuario_oculto = usuario[0] + '*' * (len(usuario) - 1)

        return f"{usuario_oculto}@{dominio}"

    def _mostrar_resumo_documento(self, usuario, remote_jid, tarefa_id, conversacao):
        """Mostra o resumo do documento gerado pela IA"""
        tarefa = Tarefa.query.get(tarefa_id)
        if not tarefa:
            self.api.enviar_mensagem(remote_jid, "❌ Tarefa não encontrada.\n\n_Responda *menu* para voltar._")
            return

        doc = tarefa.documento
        codigo = doc.codigo_definitivo or doc.codigo_provisorio or f"Doc #{doc.id}"
        titulo_formatado = f"{codigo} - {doc.titulo}" if doc.titulo else codigo

        # Obtém metadados do documento (resumo da IA)
        metadados = doc.get_metadados()
        resumo_obj = metadados.get('resumo', '')

        # O resumo pode ser um objeto ou string direta
        if isinstance(resumo_obj, dict):
            resumo_texto = resumo_obj.get('resumo', '')
            palavras_chave = resumo_obj.get('palavras_chave', [])
            topicos = resumo_obj.get('topicos_principais', [])
        else:
            resumo_texto = resumo_obj if isinstance(resumo_obj, str) else ''
            palavras_chave = metadados.get('palavras_chave', [])
            topicos = metadados.get('topicos_principais', [])

        msg = f"📄 *{titulo_formatado}*\n\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━\n"
        msg += "🤖 *Resumo (IA):*\n\n"

        if resumo_texto:
            # Limita o resumo para não ficar muito longo no WhatsApp
            resumo_limitado = resumo_texto[:800] + '...' if len(resumo_texto) > 800 else resumo_texto
            msg += f"{resumo_limitado}\n\n"
        else:
            msg += "_Resumo não disponível para este documento._\n\n"

        if palavras_chave:
            if isinstance(palavras_chave, list):
                msg += f"🏷️ *Palavras-chave:* {', '.join(palavras_chave[:5])}\n\n"
            else:
                msg += f"🏷️ *Palavras-chave:* {palavras_chave}\n\n"

        if topicos:
            if isinstance(topicos, list):
                msg += f"📋 *Tópicos:* {', '.join(topicos[:3])}\n\n"

        msg += "━━━━━━━━━━━━━━━━━━━━━\n"
        msg += "_Responda *4* para voltar às opções ou *0* para o menu._"

        self.api.enviar_mensagem(remote_jid, msg)

    def _processar_email(self, usuario, remote_jid, texto, conversacao):
        """Processa o email para confirmação de assinatura ou reprovação"""
        contexto = conversacao.get_contexto()
        tarefa_id = contexto.get('tarefa_id')
        acao = contexto.get('acao', 'aprovar')
        justificativa = contexto.get('justificativa', '')

        # Valida email do usuário (case insensitive)
        email_digitado = texto.strip().lower()
        email_cadastrado = (usuario.email or '').lower()

        if email_digitado != email_cadastrado:
            conversacao.incrementar_tentativa_senha()
            db.session.commit()

            if conversacao.esta_bloqueado():
                self.api.enviar_mensagem(remote_jid, "🚫 *Conta temporariamente bloqueada*\n\nMuitas tentativas incorretas. Tente novamente em 30 minutos.")
                return

            tentativas_restantes = 3 - conversacao.tentativas_senha
            email_dica = self._ocultar_email(usuario.email)
            self.api.enviar_mensagem(remote_jid, f"❌ *Email incorreto!*\n\n💡 Dica: {email_dica}\nTentativas restantes: {tentativas_restantes}\n\n_Responda *0* para cancelar._")
            return

        # Email correto - processa ação
        conversacao.resetar_tentativas()

        tarefa = Tarefa.query.get(tarefa_id)
        if not tarefa:
            self.api.enviar_mensagem(remote_jid, "❌ Tarefa não encontrada.\n\n_Responda *menu* para voltar._")
            conversacao.atualizar_estado('menu', {})
            db.session.commit()
            return

        doc = tarefa.documento
        codigo = doc.codigo_definitivo or doc.codigo_provisorio or f"Doc #{doc.id}"
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')

        if acao == 'aprovar':
            # Executa a assinatura (aprovação)
            sucesso, mensagem = self._executar_assinatura(usuario, tarefa, 'Aprovado via WhatsApp')

            if sucesso:
                hash_confirmacao = hashlib.sha256(f"{usuario.id}{tarefa.id}{timestamp}".encode()).hexdigest()[:12].upper()

                msg = "✅ *Assinatura Registrada com Sucesso!*\n\n"
                msg += f"📄 *Documento:* {codigo}\n"
                msg += f"⏰ *Data/Hora:* {timestamp}\n"
                msg += f"🔐 *Hash:* {hash_confirmacao}\n\n"
                msg += "_Responda *menu* para voltar ao início._"
                self.api.enviar_mensagem(remote_jid, msg)
            else:
                self.api.enviar_mensagem(remote_jid, f"❌ *Erro ao assinar:* {mensagem}\n\n_Responda *menu* para voltar._")

        elif acao == 'reprovar':
            # Executa a reprovação
            sucesso, mensagem = self._executar_reprovacao(usuario, tarefa, justificativa)

            if sucesso:
                msg = "❌ *Documento Reprovado*\n\n"
                msg += f"📄 *Documento:* {codigo}\n"
                msg += f"📝 *Motivo:* {justificativa}\n"
                msg += f"⏰ *Data/Hora:* {timestamp}\n\n"
                msg += "_Responda *menu* para voltar ao início._"
                self.api.enviar_mensagem(remote_jid, msg)
            else:
                self.api.enviar_mensagem(remote_jid, f"❌ *Erro ao reprovar:* {mensagem}\n\n_Responda *menu* para voltar._")

        elif acao == 'validar':
            # Executa a validação/codificação
            sucesso, mensagem = self._executar_validacao(usuario, tarefa)

            if sucesso:
                hash_confirmacao = hashlib.sha256(f"{usuario.id}{tarefa.id}{timestamp}".encode()).hexdigest()[:12].upper()

                msg = "✅ *Documento Validado com Sucesso!*\n\n"
                msg += f"📄 *Documento:* {codigo}\n"
                msg += f"⏰ *Data/Hora:* {timestamp}\n"
                msg += f"🔐 *Hash:* {hash_confirmacao}\n\n"
                msg += "📝 O documento seguirá para assinatura.\n\n"
                msg += "_Responda *menu* para voltar ao início._"
                self.api.enviar_mensagem(remote_jid, msg)
            else:
                self.api.enviar_mensagem(remote_jid, f"❌ *Erro ao validar:* {mensagem}\n\n_Responda *menu* para voltar._")

        elif acao == 'publicar':
            # Executa a publicação
            sucesso, mensagem = self._executar_publicacao(usuario, tarefa)

            if sucesso:
                hash_confirmacao = hashlib.sha256(f"{usuario.id}{tarefa.id}{timestamp}".encode()).hexdigest()[:12].upper()

                msg = "🎉 *Documento Publicado com Sucesso!*\n\n"
                msg += f"📄 *Documento:* {codigo}\n"
                msg += f"⏰ *Data/Hora:* {timestamp}\n"
                msg += f"🔐 *Hash:* {hash_confirmacao}\n\n"
                msg += "📊 Status: VIGENTE na Lista Mestra\n\n"
                msg += "_Responda *menu* para voltar ao início._"
                self.api.enviar_mensagem(remote_jid, msg)
            else:
                self.api.enviar_mensagem(remote_jid, f"❌ *Erro ao publicar:* {mensagem}\n\n_Responda *menu* para voltar._")

        elif acao == 'devolver':
            # Executa a devolução
            sucesso, mensagem = self._executar_devolucao(usuario, tarefa, justificativa)

            if sucesso:
                msg = "🔙 *Documento Devolvido*\n\n"
                msg += f"📄 *Documento:* {codigo}\n"
                msg += f"📝 *Motivo:* {justificativa}\n"
                msg += f"⏰ *Data/Hora:* {timestamp}\n\n"
                msg += "_Responda *menu* para voltar ao início._"
                self.api.enviar_mensagem(remote_jid, msg)
            else:
                self.api.enviar_mensagem(remote_jid, f"❌ *Erro ao devolver:* {mensagem}\n\n_Responda *menu* para voltar._")

        conversacao.atualizar_estado('menu', {})
        db.session.commit()

    def _processar_justificativa(self, usuario, remote_jid, texto, conversacao):
        """Processa justificativa de reprovação ou devolução"""
        contexto = conversacao.get_contexto()
        tarefa_id = contexto.get('tarefa_id')
        acao = contexto.get('acao', 'reprovar')

        if len(texto.strip()) < 10:
            self.api.enviar_mensagem(remote_jid, "❌ A justificativa deve ter pelo menos 10 caracteres.\n\n_Digite o motivo ou responda *0* para cancelar._")
            return

        tarefa = Tarefa.query.get(tarefa_id)
        if not tarefa:
            self.api.enviar_mensagem(remote_jid, "❌ Tarefa não encontrada.\n\n_Responda *menu* para voltar._")
            conversacao.atualizar_estado('menu', {})
            db.session.commit()
            return

        # Pede email para confirmar
        conversacao.atualizar_estado('aguardando_email', {
            'tarefa_id': tarefa_id,
            'acao': acao,
            'justificativa': texto.strip()
        })
        db.session.commit()

        email_dica = self._ocultar_email(usuario.email)
        acao_texto = 'Devolução' if acao == 'devolver' else 'Reprovação'

        msg = f"🔒 *Confirmação de {acao_texto}*\n\n"
        msg += f"📝 *Motivo:* {texto.strip()}\n\n"
        msg += f"Digite seu *email cadastrado* para confirmar.\n"
        msg += f"💡 Dica: {email_dica}\n\n"
        msg += "_Responda *0* para cancelar._"
        self.api.enviar_mensagem(remote_jid, msg)

    def _executar_assinatura(self, usuario, tarefa, parecer):
        """Executa a assinatura do documento"""
        try:
            metadata = tarefa.get_metadata()
            bloco_id = metadata.get('bloco_id')
            item_id = metadata.get('item_id')

            if not bloco_id or not item_id:
                # Tenta encontrar o item de assinatura pelo responsável
                item = ItemBlocoAssinatura.query.join(BlocoAssinatura).filter(
                    BlocoAssinatura.documento_id == tarefa.documento_id,
                    ItemBlocoAssinatura.aprovador_id == usuario.id,
                    ItemBlocoAssinatura.status == 'Pendente'
                ).first()

                if not item:
                    return False, "Item de assinatura não encontrado"
            else:
                item = ItemBlocoAssinatura.query.get(item_id)
                if not item or item.aprovador_id != usuario.id:
                    return False, "Item de assinatura inválido"

            # Gera hash da assinatura
            timestamp = datetime.now().isoformat()
            assinatura_hash = hashlib.sha256(
                f"{usuario.id}:{tarefa.id}:{timestamp}:{parecer}".encode()
            ).hexdigest()

            # Aprova o item
            item.aprovar(
                parecer=parecer,
                senha_hash=assinatura_hash,
                ip_address='WhatsApp',
                user_agent='WhatsApp Chatbot'
            )

            # Conclui a tarefa
            tarefa.concluir(parecer=parecer, aprovado=True)

            # Verifica se todos aprovaram para finalizar o bloco e criar tarefa de publicação
            bloco = item.bloco
            if bloco.todos_aprovaram():
                # Usa o workflow oficial para finalizar e criar tarefa de publicação
                try:
                    from app.services.workflow import WorkflowUGQ
                    doc = bloco.documento
                    WorkflowUGQ._finalizar_bloco_assinatura(bloco, doc)
                    logger.info(f"Bloco finalizado e tarefa de publicação criada via WhatsApp")
                except Exception as e:
                    logger.error(f"Erro ao finalizar bloco via workflow: {str(e)}")
                    # Fallback: atualiza manualmente
                    bloco.status = 'Aprovado'
                    bloco.data_conclusao = datetime.utcnow()
                    doc = bloco.documento
                    doc.status = 'Aprovado'

            db.session.commit()
            logger.info(f"Assinatura via WhatsApp: Usuario {usuario.id} assinou tarefa {tarefa.id}")
            return True, "Assinatura registrada com sucesso"

        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao executar assinatura via WhatsApp: {str(e)}", exc_info=True)
            return False, str(e)

    def _executar_reprovacao(self, usuario, tarefa, justificativa):
        """Executa a reprovação do documento"""
        try:
            metadata = tarefa.get_metadata()
            bloco_id = metadata.get('bloco_id')
            item_id = metadata.get('item_id')

            if not bloco_id or not item_id:
                # Tenta encontrar o item de assinatura pelo responsável
                item = ItemBlocoAssinatura.query.join(BlocoAssinatura).filter(
                    BlocoAssinatura.documento_id == tarefa.documento_id,
                    ItemBlocoAssinatura.aprovador_id == usuario.id,
                    ItemBlocoAssinatura.status == 'Pendente'
                ).first()

                if not item:
                    return False, "Item de assinatura não encontrado"
            else:
                item = ItemBlocoAssinatura.query.get(item_id)
                if not item or item.aprovador_id != usuario.id:
                    return False, "Item de assinatura inválido"

            # Gera hash da reprovação
            timestamp = datetime.now().isoformat()
            reprovacao_hash = hashlib.sha256(
                f"{usuario.id}:{tarefa.id}:{timestamp}:{justificativa}".encode()
            ).hexdigest()

            # Reprova o item
            item.reprovar(
                parecer=f"Reprovado via WhatsApp: {justificativa}",
                senha_hash=reprovacao_hash,
                ip_address='WhatsApp',
                user_agent='WhatsApp Chatbot'
            )

            # Conclui a tarefa como reprovada
            tarefa.concluir(parecer=justificativa, aprovado=False)

            # Atualiza status do bloco
            bloco = item.bloco
            if bloco.algum_reprovou():
                bloco.status = 'Reprovado'
                bloco.data_conclusao = datetime.utcnow()

                # Atualiza status do documento
                doc = bloco.documento
                if doc.status == 'Em Assinatura':
                    doc.status = 'Em Ajustes'

            db.session.commit()
            logger.info(f"Reprovação via WhatsApp: Usuario {usuario.id} reprovou tarefa {tarefa.id}")
            return True, "Reprovação registrada com sucesso"

        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao executar reprovação via WhatsApp: {str(e)}", exc_info=True)
            return False, str(e)

    def _executar_validacao(self, usuario, tarefa):
        """Executa a validação/codificação do documento via WhatsApp"""
        try:
            from app.services.workflow import WorkflowUGQ

            doc = tarefa.documento

            # Verifica se o documento já tem código definitivo
            if not doc.codigo_definitivo:
                # Gera código automático se não tiver
                # Usa abrangência padrão CHUFC
                tipo = doc.tipo_documento or 'POP'
                setor = doc.setor or 'Geral'

                # Gera código usando o workflow
                try:
                    codigo = WorkflowUGQ._gerar_codigo_definitivo(tipo, setor, 'CHUFC')
                    doc.codigo_definitivo = codigo
                    logger.info(f"[WHATSAPP] Código gerado automaticamente: {codigo}")
                except Exception as e:
                    logger.warning(f"Erro ao gerar código automático: {e}")
                    # Usa código provisório como fallback
                    if doc.codigo_provisorio:
                        doc.codigo_definitivo = doc.codigo_provisorio.replace('PROV-', 'DEF-')

            # Se não tiver versão, define como v1.0
            if not doc.versao:
                doc.versao = 'v1.0'

            # Chama o workflow para codificar
            WorkflowUGQ.validador_codifica_documento(tarefa, doc.codigo_definitivo, doc.versao)

            db.session.commit()
            logger.info(f"Validação via WhatsApp: Usuario {usuario.id} validou documento {doc.id}")
            return True, "Documento validado com sucesso"

        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao executar validação via WhatsApp: {str(e)}", exc_info=True)
            return False, str(e)

    def _executar_publicacao(self, usuario, tarefa):
        """Executa a publicação do documento via WhatsApp"""
        try:
            from app.services.workflow import WorkflowUGQ

            doc = tarefa.documento

            # Usa o workflow oficial para publicar
            WorkflowUGQ.validador_publica_documento(tarefa)

            logger.info(f"Publicação via WhatsApp: Usuario {usuario.id} publicou documento {doc.id}")
            return True, "Documento publicado com sucesso"

        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao executar publicação via WhatsApp: {str(e)}", exc_info=True)
            return False, str(e)

    def _executar_devolucao(self, usuario, tarefa, justificativa):
        """Executa a devolução do documento via WhatsApp"""
        try:
            doc = tarefa.documento

            # Conclui a tarefa como não aprovada
            tarefa.concluir(parecer=f"Devolvido via WhatsApp: {justificativa}", aprovado=False)

            # Atualiza status do documento para Em Ajustes
            if doc.status in ['Em Validação', 'Em Assinatura', 'Aprovado']:
                doc.status = 'Em Ajustes'

            # Cria tarefa de correção para o autor
            nova_tarefa = Tarefa(
                tipo_tarefa='Realizar Correção',
                documento_id=doc.id,
                responsavel_id=doc.criador_id,
                criador_id=usuario.id,
                prazo=datetime.utcnow() + timedelta(days=5),
                descricao=f"Correções solicitadas via WhatsApp: {justificativa}"
            )
            db.session.add(nova_tarefa)

            db.session.commit()
            logger.info(f"Devolução via WhatsApp: Usuario {usuario.id} devolveu documento {doc.id}")
            return True, "Documento devolvido com sucesso"

        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao executar devolução via WhatsApp: {str(e)}", exc_info=True)
            return False, str(e)
