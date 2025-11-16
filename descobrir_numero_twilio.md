# 🔍 Como Descobrir o Número WhatsApp do Twilio

## Método 1: Via Console Twilio

1. **Acesse:** https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn

2. Procure por uma seção que mostra:
   - **"Sandbox Number"** ou
   - **"From Number"** ou
   - **"Your Twilio WhatsApp Number"**

3. O número geralmente é: **+14155238886** (EUA - California)

## Método 2: Via Twilio Sandbox Settings

1. **Acesse:** https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox

2. No topo da página, você verá:
   ```
   Sandbox participants can send messages to:
   +1 415 523 8886
   ```

3. **Este é o número!** Use no formato: `+14155238886`

## Método 3: Verificar Números Ativos

1. **Acesse:** https://console.twilio.com/us1/develop/phone-numbers/manage/incoming

2. Veja se você tem algum número WhatsApp ativado aqui
   - Se tiver, use esse número
   - Se NÃO tiver, use o Sandbox: `+14155238886`

## ⚠️ IMPORTANTE

### Conta Trial (Gratuita)
- Você NÃO tem um número próprio
- Você usa o **Sandbox Number do Twilio**: `+14155238886`
- Este número é COMPARTILHADO com outros usuários trial
- Por isso você precisa enviar `join <código>` para "entrar na fila"

### Conta Paga
- Você pode comprar um número próprio
- Esse número é exclusivo seu
- Não precisa do Sandbox

## 📋 Formato Correto

**NO SISTEMA GED, use SEM "whatsapp:"**
```
✅ CORRETO:   +14155238886
❌ ERRADO:    whatsapp:+14155238886
❌ ERRADO:    +1 415 523 8886 (com espaços)
❌ ERRADO:    14155238886 (sem +)
```

## 🧪 Como Testar se está correto

Use este código Python para testar:

```python
from twilio.rest import Client

# Suas credenciais (pegue em https://console.twilio.com/)
account_sid = 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
auth_token = 'your_auth_token_here'

client = Client(account_sid, auth_token)

# Testa envio
message = client.messages.create(
    from_='whatsapp:+14155238886',  # Número do Twilio
    to='whatsapp:+5585999999999',    # SEU número (que enviou join)
    body='Teste do Twilio'
)

print(f"✅ Mensagem enviada! SID: {message.sid}")
```

Se funcionar = número está correto!
