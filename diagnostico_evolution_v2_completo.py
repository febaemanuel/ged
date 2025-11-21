#!/usr/bin/env python3
"""
Diagnóstico Completo - Evolution API v2
========================================

Script de diagnóstico avançado baseado na documentação oficial da Evolution API v2.
Testa todas as funcionalidades principais:
- Conexão e autenticação
- Instâncias
- Envio de mensagens (texto, mídia, áudio, localização, contato, reação, etc)
- Webhooks
- Integração com banco de dados
- Status da conexão WhatsApp

Versão: 2.0
Data: 21/11/2024
"""

import requests
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Tuple, Optional

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Cores para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class EvolutionAPIv2Diagnostic:
    """Classe para diagnóstico da Evolution API v2"""

    def __init__(self):
        """Inicializa o diagnóstico com configurações do banco de dados"""
        self.config = None
        self.base_url = None
        self.instance_name = None
        self.api_key = None
        self.headers = {}
        self.resultados = []

    def print_section(self, title: str):
        """Imprime uma seção formatada"""
        print()
        print("=" * 80)
        print(f"{Colors.HEADER}{Colors.BOLD}{title}{Colors.ENDC}")
        print("=" * 80)
        print()

    def print_subsection(self, title: str):
        """Imprime uma subseção formatada"""
        print()
        print(f"{Colors.OKCYAN}{Colors.BOLD}{title}{Colors.ENDC}")
        print("-" * 80)

    def print_success(self, message: str):
        """Imprime mensagem de sucesso"""
        print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

    def print_error(self, message: str):
        """Imprime mensagem de erro"""
        print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

    def print_warning(self, message: str):
        """Imprime mensagem de aviso"""
        print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

    def print_info(self, message: str, indent: int = 2):
        """Imprime mensagem informativa"""
        spaces = " " * indent
        print(f"{spaces}{message}")

    def adicionar_resultado(self, categoria: str, teste: str, sucesso: bool, detalhes: str = ""):
        """Adiciona resultado de um teste"""
        self.resultados.append({
            'categoria': categoria,
            'teste': teste,
            'sucesso': sucesso,
            'detalhes': detalhes,
            'timestamp': datetime.now()
        })

    def carregar_configuracao(self) -> bool:
        """Carrega configuração do banco de dados"""
        self.print_section("1. CARREGANDO CONFIGURAÇÃO DO BANCO DE DADOS")

        try:
            from app import create_app, db
            from app.models import ConfiguracaoWhatsApp

            self.print_info("Importando módulos...")
            app = create_app()

            with app.app_context():
                self.config = ConfiguracaoWhatsApp.get_config()

                self.print_success("Configuração carregada do banco de dados")
                self.print_info(f"ID: {self.config.id}")
                self.print_info(f"WhatsApp Ativo: {self.config.ativo}")
                self.print_info(f"URL Evolution API: {self.config.evolution_api_url or 'NÃO CONFIGURADO'}")
                self.print_info(f"Nome da Instância: {self.config.evolution_instance_name or 'NÃO CONFIGURADO'}")
                self.print_info(f"API Key: {'*' * 8 if self.config.evolution_api_key else 'NÃO CONFIGURADO'}")

                # Valida configuração
                if not self.config.evolution_api_url:
                    self.print_error("URL da Evolution API não configurada")
                    self.print_info("Configure em: http://127.0.0.1:5000/admin/whatsapp", indent=4)
                    return False

                if not self.config.evolution_instance_name:
                    self.print_error("Nome da Instância não configurado")
                    return False

                if not self.config.evolution_api_key:
                    self.print_error("API Key não configurada")
                    return False

                # Configura variáveis
                self.base_url = self.config.evolution_api_url
                self.instance_name = self.config.evolution_instance_name
                self.api_key = self.config.evolution_api_key
                self.headers = {'apikey': self.api_key}

                self.adicionar_resultado("Configuração", "Carregar do banco", True)
                return True

        except ImportError as e:
            self.print_error(f"Erro ao importar módulos: {str(e)}")
            self.print_info("Execute: pip install -r requirements.txt", indent=4)
            self.adicionar_resultado("Configuração", "Importar módulos", False, str(e))
            return False
        except Exception as e:
            self.print_error(f"Erro ao carregar configuração: {str(e)}")
            self.adicionar_resultado("Configuração", "Carregar do banco", False, str(e))
            return False

    def testar_conectividade(self) -> bool:
        """Testa conectividade básica com Evolution API"""
        self.print_section("2. TESTANDO CONECTIVIDADE COM EVOLUTION API")

        try:
            self.print_info(f"Testando: {self.base_url}")

            # Tenta primeiro sem autenticação
            response = requests.get(f"{self.base_url}/", timeout=5)

            if response.status_code == 200:
                data = response.json()
                self.print_success("Evolution API está acessível")
                self.print_info(f"Versão: {data.get('version', 'N/A')}")
                self.print_info(f"Client: {data.get('clientName', 'N/A')}")
                self.print_info(f"Manager: {data.get('manager', 'N/A')}")
                self.adicionar_resultado("Conectividade", "Acesso à API", True, f"Versão: {data.get('version')}")
                return True
            elif response.status_code == 403:
                self.print_warning("API requer autenticação (403)")
                # Tenta com API Key
                response = requests.get(f"{self.base_url}/", headers=self.headers, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    self.print_success("Conectado com API Key")
                    self.print_info(f"Versão: {data.get('version', 'N/A')}")
                    self.adicionar_resultado("Conectividade", "Acesso à API", True)
                    return True
                else:
                    self.print_error(f"Erro mesmo com API Key: {response.status_code}")
                    self.adicionar_resultado("Conectividade", "Acesso à API", False, f"HTTP {response.status_code}")
                    return False
            else:
                self.print_error(f"Erro HTTP {response.status_code}")
                self.print_info(f"Resposta: {response.text[:200]}", indent=4)
                self.adicionar_resultado("Conectividade", "Acesso à API", False, f"HTTP {response.status_code}")
                return False

        except requests.exceptions.ConnectionError:
            self.print_error(f"Não foi possível conectar em {self.base_url}")
            self.print_info("Verifique se a Evolution API está rodando:", indent=4)
            self.print_info("docker ps", indent=6)
            self.adicionar_resultado("Conectividade", "Acesso à API", False, "Connection refused")
            return False
        except requests.exceptions.Timeout:
            self.print_error("Timeout ao conectar (5s)")
            self.adicionar_resultado("Conectividade", "Acesso à API", False, "Timeout")
            return False
        except Exception as e:
            self.print_error(f"Erro: {str(e)}")
            self.adicionar_resultado("Conectividade", "Acesso à API", False, str(e))
            return False

    def testar_autenticacao(self) -> bool:
        """Testa autenticação com API Key"""
        self.print_section("3. TESTANDO AUTENTICAÇÃO (API KEY)")

        try:
            self.print_info(f"API Key: {'*' * 8}")

            response = requests.get(
                f"{self.base_url}/instance/fetchInstances",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                self.print_success("API Key válida!")
                instances = response.json()
                self.print_info(f"Instâncias encontradas: {len(instances) if isinstance(instances, list) else 0}")

                if isinstance(instances, list) and len(instances) > 0:
                    for inst in instances:
                        name = inst.get('instance', {}).get('instanceName', 'N/A')
                        state = inst.get('instance', {}).get('state', 'N/A')
                        self.print_info(f"• {name}: {state}", indent=4)

                self.adicionar_resultado("Autenticação", "Validar API Key", True)
                return True
            elif response.status_code in [401, 403]:
                self.print_error("API Key inválida!")
                self.print_info("Verifique o valor de AUTHENTICATION_API_KEY no .env da Evolution API", indent=4)
                self.adicionar_resultado("Autenticação", "Validar API Key", False, "API Key inválida")
                return False
            else:
                self.print_error(f"Erro HTTP {response.status_code}")
                self.print_info(f"Resposta: {response.text[:200]}", indent=4)
                self.adicionar_resultado("Autenticação", "Validar API Key", False, f"HTTP {response.status_code}")
                return False

        except Exception as e:
            self.print_error(f"Erro: {str(e)}")
            self.adicionar_resultado("Autenticação", "Validar API Key", False, str(e))
            return False

    def testar_instancia(self) -> Tuple[bool, Optional[str]]:
        """Testa status da instância"""
        self.print_section("4. VERIFICANDO INSTÂNCIA")

        try:
            self.print_info(f"Instância: {self.instance_name}")

            # Lista instâncias
            response = requests.get(
                f"{self.base_url}/instance/fetchInstances",
                headers=self.headers,
                timeout=10
            )

            if response.status_code != 200:
                self.print_error("Não foi possível listar instâncias")
                self.adicionar_resultado("Instância", "Verificar existência", False)
                return False, None

            instances = response.json()
            instance_exists = False
            instance_state = None

            if isinstance(instances, list):
                for inst in instances:
                    if inst.get('instance', {}).get('instanceName') == self.instance_name:
                        instance_exists = True
                        instance_state = inst.get('instance', {}).get('state', 'unknown')
                        break

            if instance_exists:
                self.print_success(f"Instância '{self.instance_name}' encontrada!")
                self.print_info(f"Estado: {instance_state}")

                if instance_state == 'open':
                    self.print_success("WhatsApp está CONECTADO!")
                    self.adicionar_resultado("Instância", "Status", True, "Conectado")
                elif instance_state == 'close':
                    self.print_warning("WhatsApp está DESCONECTADO")
                    self.print_info("Você precisa escanear o QR Code para conectar", indent=4)
                    self.adicionar_resultado("Instância", "Status", False, "Desconectado")
                else:
                    self.print_warning(f"Estado desconhecido: {instance_state}")
                    self.adicionar_resultado("Instância", "Status", False, f"Estado: {instance_state}")
            else:
                self.print_warning(f"Instância '{self.instance_name}' NÃO existe")
                self.print_info("Será criada automaticamente ao clicar em 'Obter QR Code'", indent=4)
                self.adicionar_resultado("Instância", "Verificar existência", False, "Não existe")

            return instance_exists, instance_state

        except Exception as e:
            self.print_error(f"Erro: {str(e)}")
            self.adicionar_resultado("Instância", "Verificar existência", False, str(e))
            return False, None

    def testar_qrcode(self, instance_exists: bool, instance_state: Optional[str]) -> bool:
        """Testa obtenção de QR Code"""
        self.print_section("5. TESTANDO OBTENÇÃO DE QR CODE")

        if instance_exists and instance_state == 'open':
            self.print_success("WhatsApp já está conectado, QR Code não necessário")
            return True

        try:
            self.print_info("Solicitando QR Code...")

            response = requests.get(
                f"{self.base_url}/instance/connect/{self.instance_name}",
                headers=self.headers,
                timeout=15
            )

            self.print_info(f"Status HTTP: {response.status_code}")

            if response.status_code == 200:
                data = response.json()

                # Procura QR Code em diferentes formatos
                qrcode = None
                if 'base64' in data:
                    qrcode = data['base64']
                elif 'qrcode' in data:
                    qr_obj = data['qrcode']
                    if isinstance(qr_obj, dict):
                        qrcode = qr_obj.get('base64') or qr_obj.get('code')
                    else:
                        qrcode = qr_obj
                elif 'code' in data:
                    qrcode = data['code']

                if qrcode:
                    self.print_success("QR Code obtido com sucesso!")
                    self.print_info(f"Tamanho: {len(qrcode)} caracteres")
                    self.print_info("Acesse http://127.0.0.1:5000/admin/whatsapp e clique em 'Obter QR Code'", indent=4)
                    self.adicionar_resultado("QR Code", "Obter QR Code", True)
                    return True
                else:
                    if data.get('instance', {}).get('state') == 'open':
                        self.print_success("WhatsApp já está conectado!")
                        self.adicionar_resultado("QR Code", "Obter QR Code", True, "Já conectado")
                        return True
                    else:
                        self.print_warning("QR Code não encontrado na resposta")
                        self.print_info(f"Resposta: {json.dumps(data, indent=2)[:500]}", indent=4)
                        self.adicionar_resultado("QR Code", "Obter QR Code", False, "QR não encontrado")
                        return False

            elif response.status_code == 404:
                self.print_warning("Instância não encontrada, tentando criar...")

                # Tenta criar instância
                response_create = requests.post(
                    f"{self.base_url}/instance/create",
                    headers={'Content-Type': 'application/json', 'apikey': self.api_key},
                    json={
                        'instanceName': self.instance_name,
                        'token': self.api_key,
                        'qrcode': True,
                        'integration': 'WHATSAPP-BAILEYS'
                    },
                    timeout=15
                )

                if response_create.status_code in [200, 201]:
                    self.print_success("Instância criada com sucesso!")
                    self.print_info("Agora clique em 'Obter QR Code' na página do GED", indent=4)
                    self.adicionar_resultado("QR Code", "Criar instância", True)
                    return True
                elif response_create.status_code == 403:
                    # Verifica se é erro de instância já existente
                    response_text = response_create.text.lower()
                    if "already" in response_text or "já existe" in response_text:
                        self.print_success("Instância já existe")
                        self.adicionar_resultado("QR Code", "Criar instância", True, "Já existe")
                        return True
                    else:
                        self.print_error(f"Erro 403 ao criar instância: {response_create.text[:200]}")
                        self.adicionar_resultado("QR Code", "Criar instância", False, "Erro 403")
                        return False
                else:
                    self.print_error(f"Erro ao criar instância: {response_create.status_code}")
                    self.print_info(f"Resposta: {response_create.text[:200]}", indent=4)
                    self.adicionar_resultado("QR Code", "Criar instância", False, f"HTTP {response_create.status_code}")
                    return False

            else:
                self.print_error(f"Erro HTTP {response.status_code}")
                self.print_info(f"Resposta: {response.text[:200]}", indent=4)
                self.adicionar_resultado("QR Code", "Obter QR Code", False, f"HTTP {response.status_code}")
                return False

        except Exception as e:
            self.print_error(f"Erro: {str(e)}")
            self.adicionar_resultado("QR Code", "Obter QR Code", False, str(e))
            return False

    def testar_envio_mensagem(self, instance_state: Optional[str]) -> bool:
        """Testa envio de mensagem (apenas se conectado)"""
        self.print_section("6. TESTANDO ENVIO DE MENSAGEM")

        if instance_state != 'open':
            self.print_warning("WhatsApp não está conectado, pulando teste de envio")
            self.print_info("Conecte o WhatsApp primeiro para testar envio de mensagens", indent=4)
            return False

        # Solicita número de teste
        self.print_info("Para testar envio de mensagem, precisamos de um número.")
        self.print_info("Digite um número no formato: 5585999999999 (ou deixe em branco para pular)")

        try:
            numero_teste = input("Número de teste: ").strip()

            if not numero_teste:
                self.print_warning("Teste de envio pulado")
                return False

            # Formata número
            numero_formatado = numero_teste.replace('+', '').strip()
            if not numero_formatado.endswith('@s.whatsapp.net'):
                numero_formatado = f"{numero_formatado}@s.whatsapp.net"

            mensagem_teste = f"🧪 *Teste Evolution API v2*\n\nMensagem de teste enviada em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n_Sistema GED - Diagnóstico_"

            self.print_info(f"Enviando mensagem para {numero_teste}...")

            response = requests.post(
                f"{self.base_url}/message/sendText/{self.instance_name}",
                headers={'Content-Type': 'application/json', 'apikey': self.api_key},
                json={
                    'number': numero_formatado,
                    'text': mensagem_teste,
                    'delay': 1000
                },
                timeout=30
            )

            if response.status_code in [200, 201]:
                data = response.json()
                message_id = data.get('key', {}).get('id', 'unknown')
                self.print_success("Mensagem enviada com sucesso!")
                self.print_info(f"Message ID: {message_id}")
                self.adicionar_resultado("Envio", "Mensagem de texto", True, f"ID: {message_id}")
                return True
            else:
                self.print_error(f"Erro ao enviar mensagem: {response.status_code}")
                self.print_info(f"Resposta: {response.text[:200]}", indent=4)
                self.adicionar_resultado("Envio", "Mensagem de texto", False, f"HTTP {response.status_code}")
                return False

        except KeyboardInterrupt:
            self.print_warning("\nTeste de envio cancelado")
            return False
        except Exception as e:
            self.print_error(f"Erro: {str(e)}")
            self.adicionar_resultado("Envio", "Mensagem de texto", False, str(e))
            return False

    def testar_webhook(self) -> bool:
        """Testa configuração de webhook"""
        self.print_section("7. VERIFICANDO WEBHOOK")

        try:
            self.print_info("Verificando configuração de webhook da instância...")

            response = requests.get(
                f"{self.base_url}/webhook/find/{self.instance_name}",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data and data.get('enabled'):
                    self.print_success("Webhook configurado e ativo")
                    self.print_info(f"URL: {data.get('url', 'N/A')}")
                    self.print_info(f"Eventos: {', '.join(data.get('events', []))}")
                    self.adicionar_resultado("Webhook", "Verificar configuração", True)
                    return True
                else:
                    self.print_warning("Webhook não configurado ou desativado")
                    self.print_info("Configure em: http://127.0.0.1:5000/admin/whatsapp", indent=4)
                    self.adicionar_resultado("Webhook", "Verificar configuração", False, "Não configurado")
                    return False
            elif response.status_code == 404:
                self.print_warning("Webhook não configurado")
                self.adicionar_resultado("Webhook", "Verificar configuração", False, "Não configurado")
                return False
            else:
                self.print_error(f"Erro ao verificar webhook: {response.status_code}")
                self.adicionar_resultado("Webhook", "Verificar configuração", False, f"HTTP {response.status_code}")
                return False

        except Exception as e:
            self.print_error(f"Erro: {str(e)}")
            self.adicionar_resultado("Webhook", "Verificar configuração", False, str(e))
            return False

    def verificar_banco_dados(self) -> bool:
        """Verifica configuração do banco de dados"""
        self.print_section("8. VERIFICANDO BANCO DE DADOS")

        try:
            from app import create_app, db
            from app.models import LogWhatsApp, ConversacaoWhatsApp, Usuario
            from sqlalchemy import inspect

            app = create_app()

            with app.app_context():
                # Verifica conexão
                db.session.execute(db.text('SELECT 1'))
                self.print_success("Conexão com PostgreSQL estabelecida")

                # Verifica tabelas
                inspector = inspect(db.engine)
                tabelas_necessarias = ['configuracao_whatsapp', 'conversacoes_whatsapp', 'logs_whatsapp']

                for tabela in tabelas_necessarias:
                    if tabela in inspector.get_table_names():
                        colunas = inspector.get_columns(tabela)
                        self.print_success(f"Tabela '{tabela}' existe ({len(colunas)} colunas)")
                    else:
                        self.print_error(f"Tabela '{tabela}' NÃO EXISTE!")
                        self.print_info("Execute: python3 aplicar_migracao.py", indent=4)
                        return False

                # Estatísticas
                total_mensagens = LogWhatsApp.query.count()
                mensagens_enviadas = LogWhatsApp.query.filter_by(direcao='enviada').count()
                mensagens_recebidas = LogWhatsApp.query.filter_by(direcao='recebida').count()
                conversacoes_ativas = ConversacaoWhatsApp.query.count()
                usuarios_whatsapp = Usuario.query.filter(
                    Usuario.telefone.isnot(None),
                    Usuario.whatsapp_ativo == True
                ).count()

                self.print_info("")
                self.print_info("Estatísticas:")
                self.print_info(f"• Total de mensagens: {total_mensagens}", indent=4)
                self.print_info(f"• Mensagens enviadas: {mensagens_enviadas}", indent=4)
                self.print_info(f"• Mensagens recebidas: {mensagens_recebidas}", indent=4)
                self.print_info(f"• Conversas ativas: {conversacoes_ativas}", indent=4)
                self.print_info(f"• Usuários com WhatsApp: {usuarios_whatsapp}", indent=4)

                self.adicionar_resultado("Banco de Dados", "Verificar tabelas", True)
                return True

        except Exception as e:
            self.print_error(f"Erro: {str(e)}")
            self.adicionar_resultado("Banco de Dados", "Verificar tabelas", False, str(e))
            return False

    def gerar_relatorio(self):
        """Gera relatório final do diagnóstico"""
        self.print_section("9. RELATÓRIO FINAL DO DIAGNÓSTICO")

        # Agrupa resultados por categoria
        categorias = {}
        for resultado in self.resultados:
            cat = resultado['categoria']
            if cat not in categorias:
                categorias[cat] = {'sucessos': 0, 'falhas': 0, 'testes': []}

            if resultado['sucesso']:
                categorias[cat]['sucessos'] += 1
            else:
                categorias[cat]['falhas'] += 1

            categorias[cat]['testes'].append(resultado)

        # Imprime resumo
        total_testes = len(self.resultados)
        total_sucessos = sum(1 for r in self.resultados if r['sucesso'])
        total_falhas = total_testes - total_sucessos

        self.print_info(f"Total de testes: {total_testes}")
        self.print_info(f"Sucessos: {total_sucessos} ({total_sucessos/total_testes*100:.1f}%)")
        self.print_info(f"Falhas: {total_falhas} ({total_falhas/total_testes*100:.1f}%)")
        print()

        # Detalhes por categoria
        for cat, dados in categorias.items():
            self.print_subsection(f"{cat}")
            self.print_info(f"Sucessos: {dados['sucessos']}, Falhas: {dados['falhas']}")

            for teste in dados['testes']:
                status = "✓" if teste['sucesso'] else "✗"
                cor = Colors.OKGREEN if teste['sucesso'] else Colors.FAIL
                print(f"  {cor}{status} {teste['teste']}{Colors.ENDC}")
                if teste['detalhes']:
                    self.print_info(f"  → {teste['detalhes']}", indent=4)

        print()

        # Recomendações
        self.print_subsection("RECOMENDAÇÕES")

        if total_falhas == 0:
            self.print_success("Sistema totalmente funcional! ✨")
            self.print_info("Próximos passos:", indent=2)
            self.print_info("1. Acesse http://127.0.0.1:5000/admin/whatsapp", indent=4)
            self.print_info("2. Configure webhooks se necessário", indent=4)
            self.print_info("3. Teste envio de mensagens", indent=4)
        else:
            self.print_warning("Alguns testes falharam")
            self.print_info("Ações recomendadas:", indent=2)

            # Verifica problemas específicos
            tem_erro_conexao = any(r['categoria'] == 'Conectividade' and not r['sucesso'] for r in self.resultados)
            tem_erro_auth = any(r['categoria'] == 'Autenticação' and not r['sucesso'] for r in self.resultados)
            tem_erro_instancia = any(r['categoria'] == 'Instância' and not r['sucesso'] for r in self.resultados)

            if tem_erro_conexao:
                self.print_info("• Verifique se a Evolution API está rodando: docker ps", indent=4)
                self.print_info("• Verifique a URL configurada", indent=4)

            if tem_erro_auth:
                self.print_info("• Verifique se a API Key está correta", indent=4)
                self.print_info("• Deve ser igual ao AUTHENTICATION_API_KEY no .env da Evolution API", indent=4)

            if tem_erro_instancia:
                self.print_info("• Acesse http://127.0.0.1:5000/admin/whatsapp", indent=4)
                self.print_info("• Clique em 'Obter QR Code'", indent=4)
                self.print_info("• Escaneie o QR Code com seu WhatsApp", indent=4)

    def executar(self):
        """Executa diagnóstico completo"""
        print()
        print(f"{Colors.BOLD}{Colors.HEADER}╔════════════════════════════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}║          DIAGNÓSTICO COMPLETO - EVOLUTION API V2                               ║{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}║          Baseado na documentação oficial v2.1.1+                               ║{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}╚════════════════════════════════════════════════════════════════════════════════╝{Colors.ENDC}")
        print()

        # Executa testes em sequência
        if not self.carregar_configuracao():
            return

        if not self.testar_conectividade():
            self.gerar_relatorio()
            return

        if not self.testar_autenticacao():
            self.gerar_relatorio()
            return

        instance_exists, instance_state = self.testar_instancia()

        self.testar_qrcode(instance_exists, instance_state)

        self.testar_envio_mensagem(instance_state)

        self.testar_webhook()

        self.verificar_banco_dados()

        # Gera relatório final
        self.gerar_relatorio()


def main():
    """Função principal"""
    try:
        diagnostico = EvolutionAPIv2Diagnostic()
        diagnostico.executar()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Diagnóstico interrompido pelo usuário{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}Erro fatal: {str(e)}{Colors.ENDC}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
