#!/usr/bin/env python3
"""
Script de Diagnóstico - Integração WhatsApp Evolution API
"""

import requests
import sys
import os

# Adiciona o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import ConfiguracaoWhatsApp

def diagnostico_evolution_api():
    """Executa diagnóstico completo da integração Evolution API"""

    print("=" * 80)
    print("DIAGNÓSTICO - INTEGRAÇÃO EVOLUTION API")
    print("=" * 80)
    print()

    # 1. Verifica configuração no banco de dados
    print("1. VERIFICANDO CONFIGURAÇÃO NO BANCO DE DADOS")
    print("-" * 80)

    app = create_app()
    with app.app_context():
        config = ConfiguracaoWhatsApp.get_config()

        print(f"   ✓ Configuração encontrada no banco")
        print(f"   - WhatsApp Ativo: {config.ativo}")
        print(f"   - URL Evolution API: {config.evolution_api_url or 'NÃO CONFIGURADO'}")
        print(f"   - Nome da Instância: {config.evolution_instance_name or 'NÃO CONFIGURADO'}")
        print(f"   - API Key: {'*' * len(config.evolution_api_key) if config.evolution_api_key else 'NÃO CONFIGURADO'}")
        print()

        if not config.evolution_api_url or not config.evolution_instance_name or not config.evolution_api_key:
            print("   ❌ ERRO: Credenciais incompletas!")
            print("   👉 Preencha todos os campos na página de configuração e clique em 'Salvar'")
            return

        # 2. Testa conectividade com Evolution API
        print("2. TESTANDO CONECTIVIDADE COM EVOLUTION API")
        print("-" * 80)

        try:
            response = requests.get(f"{config.evolution_api_url}/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Evolution API está acessível")
                print(f"   - Versão: {data.get('version', 'N/A')}")
                print(f"   - Client Name: {data.get('clientName', 'N/A')}")
                print(f"   - Manager: {data.get('manager', 'N/A')}")
            else:
                print(f"   ❌ Evolution API retornou status {response.status_code}")
                return
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Não foi possível conectar em {config.evolution_api_url}")
            print(f"   👉 Verifique se a Evolution API está rodando: docker ps")
            return
        except Exception as e:
            print(f"   ❌ Erro ao conectar: {str(e)}")
            return

        print()

        # 3. Verifica autenticação (API Key)
        print("3. VERIFICANDO AUTENTICAÇÃO (API KEY)")
        print("-" * 80)

        headers = {'apikey': config.evolution_api_key}

        try:
            response = requests.get(
                f"{config.evolution_api_url}/instance/fetchInstances",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                print(f"   ✓ API Key está correta!")
                instances = response.json()
                print(f"   - Instâncias encontradas: {len(instances)}")

                if isinstance(instances, list):
                    for inst in instances:
                        instance_name = inst.get('instance', {}).get('instanceName', 'N/A')
                        state = inst.get('instance', {}).get('state', 'N/A')
                        print(f"     • {instance_name} - Estado: {state}")

            elif response.status_code == 401 or response.status_code == 403:
                print(f"   ❌ API Key inválida!")
                print(f"   👉 Verifique se a API Key está correta no arquivo .env da Evolution API")
                print(f"   👉 Deve ser igual ao valor de AUTHENTICATION_API_KEY")
                return

            else:
                print(f"   ❌ Erro HTTP {response.status_code}: {response.text}")
                return

        except Exception as e:
            print(f"   ❌ Erro ao verificar API Key: {str(e)}")
            return

        print()

        # 4. Verifica se a instância existe
        print("4. VERIFICANDO INSTÂNCIA")
        print("-" * 80)

        instance_exists = False
        instance_state = None

        if isinstance(instances, list):
            for inst in instances:
                if inst.get('instance', {}).get('instanceName') == config.evolution_instance_name:
                    instance_exists = True
                    instance_state = inst.get('instance', {}).get('state')
                    break

        if instance_exists:
            print(f"   ✓ Instância '{config.evolution_instance_name}' encontrada!")
            print(f"   - Estado: {instance_state}")

            if instance_state == 'open':
                print(f"   ✓ WhatsApp está CONECTADO!")
            elif instance_state == 'close':
                print(f"   ⚠️  WhatsApp está DESCONECTADO")
                print(f"   👉 Você precisa escanear o QR Code para conectar")
            else:
                print(f"   ⚠️  Estado desconhecido: {instance_state}")
        else:
            print(f"   ⚠️  Instância '{config.evolution_instance_name}' NÃO existe")
            print(f"   👉 Será criada automaticamente quando você clicar em 'Obter QR Code'")

        print()

        # 5. Testa obtenção de QR Code (se não estiver conectado)
        if not instance_exists or instance_state != 'open':
            print("5. TESTANDO OBTENÇÃO DE QR CODE")
            print("-" * 80)

            try:
                # Primeiro tenta criar/conectar a instância
                response_connect = requests.get(
                    f"{config.evolution_api_url}/instance/connect/{config.evolution_instance_name}",
                    headers=headers,
                    timeout=15
                )

                if response_connect.status_code == 200:
                    data = response_connect.json()
                    print(f"   ✓ Requisição bem-sucedida!")
                    print(f"   - Resposta: {str(data)[:200]}...")

                    # Verifica se tem QR Code
                    qrcode = None
                    if 'base64' in data:
                        qrcode = data['base64']
                    elif 'qrcode' in data:
                        qrcode = data.get('qrcode', {}).get('base64') or data.get('qrcode')
                    elif 'code' in data:
                        qrcode = data['code']

                    if qrcode:
                        print(f"   ✓ QR Code obtido com sucesso!")
                        print(f"   - Tamanho: {len(qrcode)} caracteres")
                        print(f"   👉 Você pode clicar em 'Obter QR Code' na página para ver")
                    else:
                        if data.get('instance', {}).get('state') == 'open':
                            print(f"   ✓ WhatsApp já está conectado!")
                        else:
                            print(f"   ⚠️  QR Code não encontrado na resposta")
                            print(f"   - Dados: {data}")

                elif response_connect.status_code == 404:
                    print(f"   ⚠️  Instância não encontrada (será criada automaticamente)")

                    # Tenta criar instância
                    print(f"   - Tentando criar instância...")
                    response_create = requests.post(
                        f"{config.evolution_api_url}/instance/create",
                        headers={'Content-Type': 'application/json', 'apikey': config.evolution_api_key},
                        json={
                            'instanceName': config.evolution_instance_name,
                            'token': config.evolution_api_key,
                            'qrcode': True,
                            'integration': 'WHATSAPP-BAILEYS'
                        },
                        timeout=15
                    )

                    if response_create.status_code in [200, 201]:
                        print(f"   ✓ Instância criada com sucesso!")
                        print(f"   👉 Clique em 'Obter QR Code' na página agora")
                    elif response_create.status_code == 409:
                        print(f"   ✓ Instância já existe")
                    else:
                        print(f"   ❌ Erro ao criar instância: {response_create.status_code}")
                        print(f"   - Resposta: {response_create.text[:200]}")

                else:
                    print(f"   ❌ Erro HTTP {response_connect.status_code}")
                    print(f"   - Resposta: {response_connect.text[:200]}")

            except Exception as e:
                print(f"   ❌ Erro ao obter QR Code: {str(e)}")

        print()

        # 6. Resumo
        print("=" * 80)
        print("RESUMO DO DIAGNÓSTICO")
        print("=" * 80)

        if config.ativo:
            print("✓ WhatsApp está ATIVADO no sistema")
        else:
            print("⚠️  WhatsApp está DESATIVADO no sistema")
            print("   👉 Marque a opção 'WhatsApp ATIVADO' e salve as configurações")

        print()
        print("PRÓXIMOS PASSOS:")
        print("1. Acesse a página de configuração WhatsApp no GED")
        print("2. Clique no botão 'Obter QR Code'")
        print("3. Escaneie o QR Code com seu WhatsApp")
        print("4. Aguarde a conexão (o status ficará verde)")
        print()

if __name__ == '__main__':
    try:
        diagnostico_evolution_api()
    except Exception as e:
        print(f"❌ Erro durante diagnóstico: {str(e)}")
        import traceback
        traceback.print_exc()
