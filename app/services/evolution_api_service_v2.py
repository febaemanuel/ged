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
            # LÓGICA DO CHATBOT (MENU)
            # ============================================================
            texto_lower = texto.lower()

            if texto_lower in ['menu', 'oi', 'olá', 'ola', 'inicio', 'start', 'ajuda', 'm']:
                self._enviar_menu_principal(usuario, remote_jid) # Responde onde a msg veio
            
            elif texto_lower in ['tarefas', '1', 'um']:
                self._listar_tarefas(usuario, remote_jid)
            
            elif texto_lower in ['documentos', '2', 'dois']:
                self.api.enviar_mensagem(remote_jid, "📂 *Meus Documentos*\n\nEsta funcionalidade estará disponível em breve.")

            else:
                self._enviar_menu_principal(usuario, remote_jid)

            return {'status': 'success'}

        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}", exc_info=True)
            return {'status': 'error', 'message': str(e)}

    def _enviar_menu_principal(self, usuario, remote_jid):
        """Envia o menu principal"""
        total_tarefas = Tarefa.query.filter_by(
            responsavel_id=usuario.id, 
            data_conclusao=None
        ).count()

        templates = self.config.get_templates()
        texto_base = templates.get('menu_principal', '📋 *Olá, {nome}*').replace('{total}', str(total_tarefas)).replace('{nome}', usuario.nome)

        msg_menu = f"{texto_base}\n\n1️⃣ Ver Tarefas Pendentes ({total_tarefas})\n2️⃣ Meus Documentos\n\n_Responda com o número da opção._"

        self.api.enviar_mensagem(remote_jid, msg_menu)

    def _listar_tarefas(self, usuario, remote_jid):
        """Lista tarefas"""
        tarefas = Tarefa.query.filter_by(
            responsavel_id=usuario.id, 
            data_conclusao=None
        ).order_by(Tarefa.prazo.asc()).limit(5).all()

        if not tarefas:
            self.api.enviar_mensagem(remote_jid, "✅ *Tudo limpo!* Você não possui tarefas pendentes.")
            return

        msg = "📋 *Suas Tarefas Pendentes:*\n"
        for t in tarefas:
            prazo = t.prazo.strftime('%d/%m') if t.prazo else 'S/ Prazo'
            codigo = t.documento.codigo_definitivo or t.documento.codigo_provisorio or f"#{t.documento.id}"
            msg += f"\n🔹 *{codigo}* - {t.tipo_tarefa}\n   📅 Prazo: {prazo}\n"
        
        msg += "\n_Acesse o sistema para ver detalhes._"
        self.api.enviar_mensagem(remote_jid, msg)
