#!/usr/bin/env python3
"""
Script para testar configuração do Twilio WhatsApp
Ajuda a descobrir qual é o número correto
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from twilio.rest import Client
    print("✅ Twilio instalado")
except ImportError:
    print("❌ Twilio NÃO instalado!")
    print("   Execute: pip install twilio>=8.10.0")
    sys.exit(1)

# Suas credenciais do Twilio (obtenha em https://console.twilio.com/)
ACCOUNT_SID = input("Digite seu Account SID (do Twilio Console): ").strip()
AUTH_TOKEN = input("Digite seu Auth Token (do Twilio Console): ").strip()

if not AUTH_TOKEN:
    print("❌ Auth Token não pode ser vazio!")
    sys.exit(1)

print("\n" + "="*60)
print("🔍 DESCOBRINDO NÚMERO WHATSAPP DO TWILIO")
print("="*60 + "\n")

# Cria cliente
try:
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    print("✅ Conectado ao Twilio com sucesso!\n")
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")
    sys.exit(1)

# Lista números de telefone da conta
print("📞 Números de telefone na sua conta Twilio:")
print("-" * 60)

try:
    incoming_numbers = client.incoming_phone_numbers.list(limit=20)

    if not incoming_numbers:
        print("⚠️  Você NÃO tem números próprios (conta trial)")
        print("   Use o Sandbox Number: +14155238886")
        numero_whatsapp = "+14155238886"
    else:
        for record in incoming_numbers:
            print(f"   {record.phone_number} - {record.friendly_name}")
            # Se tiver WhatsApp habilitado, seria o número certo
            numero_whatsapp = record.phone_number
        print(f"\n✅ Use este número: {numero_whatsapp}")

except Exception as e:
    print(f"⚠️  Erro ao listar números: {e}")
    print("   Usando número padrão do Sandbox: +14155238886")
    numero_whatsapp = "+14155238886"

print("\n" + "="*60)
print("🧪 TESTANDO ENVIO DE MENSAGEM")
print("="*60 + "\n")

# Pede número do destinatário
print("⚠️  IMPORTANTE: O número precisa ter enviado 'join <código>' antes!")
print("   (Veja em: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)\n")

seu_numero = input("Digite SEU número WhatsApp (+5585999999999): ").strip()

if not seu_numero:
    print("❌ Número não pode ser vazio!")
    sys.exit(1)

# Remove espaços e formata
seu_numero = seu_numero.replace(" ", "").replace("(", "").replace(")", "").replace("-", "")
if not seu_numero.startswith("+"):
    seu_numero = "+" + seu_numero

print(f"\n📤 Enviando mensagem de teste...")
print(f"   De: {numero_whatsapp}")
print(f"   Para: {seu_numero}\n")

try:
    message = client.messages.create(
        from_=f'whatsapp:{numero_whatsapp}',
        to=f'whatsapp:{seu_numero}',
        body='''🧪 TESTE DO TWILIO WHATSAPP

✅ Configuração funcionando!

Seu número WhatsApp correto é:
{numero}

Use este número no sistema GED em:
/admin/whatsapp

_Sistema GED EBSERH_'''.format(numero=numero_whatsapp)
    )

    print("=" * 60)
    print("✅ SUCESSO! MENSAGEM ENVIADA!")
    print("=" * 60)
    print(f"\n📋 Detalhes:")
    print(f"   Message SID: {message.sid}")
    print(f"   Status: {message.status}")
    print(f"   De: {message.from_}")
    print(f"   Para: {message.to}")
    print(f"\n📱 Verifique seu WhatsApp agora!")
    print(f"\n✅ Use este número no GED: {numero_whatsapp}")
    print(f"   (SEM o prefixo 'whatsapp:')")

except Exception as e:
    print("=" * 60)
    print("❌ ERRO AO ENVIAR MENSAGEM")
    print("=" * 60)
    print(f"\n{e}\n")

    # Dicas de erro
    error_str = str(e)

    if "63007" in error_str or "Channel" in error_str:
        print("💡 SOLUÇÃO:")
        print("   1. Verifique se você enviou 'join <código>' no WhatsApp")
        print("   2. Acesse: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn")
        print("   3. Envie a mensagem exata que aparece lá")
        print(f"   4. Aguarde confirmação do Twilio")

    elif "21211" in error_str or "not a valid" in error_str:
        print("💡 SOLUÇÃO:")
        print("   O número de destino está inválido")
        print(f"   Formato correto: +5585999999999 (com código do país)")

    elif "20003" in error_str or "authenticate" in error_str:
        print("💡 SOLUÇÃO:")
        print("   Auth Token está incorreto")
        print("   Copie novamente em: https://console.twilio.com/")

    else:
        print("💡 DICAS:")
        print("   - Verifique suas credenciais Twilio")
        print("   - Verifique se tem créditos (conta trial tem $15)")
        print("   - Acesse: https://www.twilio.com/docs/errors/")

print("\n" + "="*60)
print("📚 LINKS ÚTEIS")
print("="*60)
print("   Console Twilio: https://console.twilio.com/")
print("   WhatsApp Sandbox: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn")
print("   Configurar Webhook: https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox")
print("   Logs Twilio: https://console.twilio.com/us1/monitor/logs/debugger")
print("="*60 + "\n")
