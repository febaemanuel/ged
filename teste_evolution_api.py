#!/usr/bin/env python3
"""
Script Simples - Teste Evolution API
"""

import requests
import json

# Configurações (altere conforme necessário)
EVOLUTION_API_URL = "http://192.168.18.6:8080"
INSTANCE_NAME = "principal12"
API_KEY = "12345678"  # Altere para a sua API Key

def teste_evolution_api():
    print("=" * 80)
    print("TESTE RÁPIDO - EVOLUTION API")
    print("=" * 80)
    print()

    # 1. Testa conexão básica (com e sem API Key)
    print("1. Testando conexão com Evolution API...")
    print(f"   URL: {EVOLUTION_API_URL}")

    # Tenta primeiro sem API Key
    try:
        response = requests.get(f"{EVOLUTION_API_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Conectado (sem API Key)!")
            print(f"   - Versão: {data.get('version')}")
            print(f"   - Client: {data.get('clientName')}")
        elif response.status_code == 403:
            print(f"   ⚠️  API requer autenticação (403)")
            print(f"   - Tentando com API Key...")

            # Tenta com API Key
            headers_auth = {'apikey': API_KEY}
            response = requests.get(f"{EVOLUTION_API_URL}/", headers=headers_auth, timeout=5)

            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Conectado (com API Key)!")
                print(f"   - Versão: {data.get('version')}")
                print(f"   - Client: {data.get('clientName')}")
            else:
                print(f"   ❌ Erro mesmo com API Key: Status {response.status_code}")
                print(f"   - Resposta: {response.text[:200]}")
                return
        else:
            print(f"   ❌ Erro: Status {response.status_code}")
            print(f"   - Resposta: {response.text[:200]}")
            return
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
        return

    print()

    # 2. Testa API Key
    print("2. Testando API Key...")
    print(f"   API Key: {API_KEY}")

    headers = {'apikey': API_KEY}

    try:
        response = requests.get(
            f"{EVOLUTION_API_URL}/instance/fetchInstances",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            print(f"   ✓ API Key válida!")
            instances = response.json()
            print(f"   - Instâncias: {len(instances)}")

            if isinstance(instances, list):
                for inst in instances:
                    name = inst.get('instance', {}).get('instanceName', 'N/A')
                    state = inst.get('instance', {}).get('state', 'N/A')
                    print(f"     • {name}: {state}")
            else:
                print(f"   - Resposta: {instances}")

        elif response.status_code in [401, 403]:
            print(f"   ❌ API Key inválida!")
            print(f"   👉 Verifique o valor de AUTHENTICATION_API_KEY no .env da Evolution API")
            return
        else:
            print(f"   ❌ Erro {response.status_code}: {response.text}")
            return

    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
        return

    print()

    # 3. Testa instância específica
    print(f"3. Verificando instância '{INSTANCE_NAME}'...")

    instance_exists = False
    instance_state = None

    if isinstance(instances, list):
        for inst in instances:
            if inst.get('instance', {}).get('instanceName') == INSTANCE_NAME:
                instance_exists = True
                instance_state = inst.get('instance', {}).get('state')
                break

    if instance_exists:
        print(f"   ✓ Instância encontrada!")
        print(f"   - Estado: {instance_state}")
    else:
        print(f"   ⚠️  Instância não existe (será criada ao clicar em 'Obter QR Code')")

    print()

    # 4. Tenta obter QR Code
    if not instance_exists or instance_state != 'open':
        print("4. Tentando obter QR Code...")

        try:
            response = requests.get(
                f"{EVOLUTION_API_URL}/instance/connect/{INSTANCE_NAME}",
                headers=headers,
                timeout=15
            )

            print(f"   - Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Requisição bem-sucedida!")

                # Procura QR Code
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
                    print(f"   ✓ QR Code obtido! ({len(qrcode)} caracteres)")
                    print(f"   👉 Acesse a página do GED e clique em 'Obter QR Code'")
                else:
                    if data.get('instance', {}).get('state') == 'open':
                        print(f"   ✓ WhatsApp já conectado!")
                    else:
                        print(f"   ⚠️  QR Code não encontrado")
                        print(f"   - Resposta completa:")
                        print(json.dumps(data, indent=2)[:500])

            elif response.status_code == 404:
                print(f"   ⚠️  Instância não existe, criando...")

                # Cria instância
                response_create = requests.post(
                    f"{EVOLUTION_API_URL}/instance/create",
                    headers={'Content-Type': 'application/json', 'apikey': API_KEY},
                    json={
                        'instanceName': INSTANCE_NAME,
                        'token': API_KEY,
                        'qrcode': True,
                        'integration': 'WHATSAPP-BAILEYS'
                    },
                    timeout=15
                )

                if response_create.status_code in [200, 201]:
                    print(f"   ✓ Instância criada!")
                    print(f"   👉 Agora clique em 'Obter QR Code' na página do GED")
                else:
                    print(f"   ❌ Erro ao criar: {response_create.status_code}")
                    print(f"   - {response_create.text[:200]}")

            else:
                print(f"   ❌ Erro {response.status_code}")
                print(f"   - {response.text[:200]}")

        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")

    print()
    print("=" * 80)
    print("CONCLUSÃO")
    print("=" * 80)
    print()
    print("Se tudo acima passou, você pode:")
    print("1. Acessar http://127.0.0.1:5000/admin/whatsapp")
    print("2. Verificar se as credenciais estão salvas")
    print("3. Clicar em 'Obter QR Code'")
    print("4. Escanear o QR Code com seu WhatsApp")
    print()

if __name__ == '__main__':
    try:
        teste_evolution_api()
    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro fatal: {str(e)}")
        import traceback
        traceback.print_exc()
