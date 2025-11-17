# Correção do Erro: Twilio Sender ID Inválido

## Problema

Você está recebendo o seguinte erro ao tentar enviar mensagens pelo WhatsApp:

```
HTTP Error POST /Accounts/ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/Messages.json
Unable to create record: The 'From' number wh is not a valid phone number, shortcode, or alphanumeric sender ID.
```

**Erro:** O número do WhatsApp está configurado como `"wh"` ao invés de um número válido como `+14155238886`.

---

## Causa Raiz

O campo `twilio_whatsapp_number` na tabela `configuracao_whatsapp` do banco de dados está com um valor inválido (`"wh"`), o que faz com que a API do Twilio rejeite a mensagem.

Localização do problema no código:
- **Arquivo:** `app/services/whatsapp_service.py:89`
- **Linha:** `from_numero = f"whatsapp:{self.config.twilio_whatsapp_number}"`

---

## Solução Rápida

### Opção 1: Usar o Script de Correção (Recomendado)

Execute o script de correção fornecido:

```bash
# Com número do Twilio Sandbox (ambiente de teste)
python3 fix_whatsapp_sender.py +14155238886

# Com seu número real do WhatsApp Business
python3 fix_whatsapp_sender.py +5585999999999
```

### Opção 2: Corrigir pelo Painel Administrativo

1. Acesse o sistema GED pelo navegador
2. Faça login como administrador
3. Vá para **Menu → Gestão → WhatsApp**
4. No campo "Número WhatsApp", digite o número completo com código do país:
   - Exemplo Twilio Sandbox: `+14155238886`
   - Exemplo Brasil: `+5585999999999`
5. Clique em **Salvar Configurações**

### Opção 3: Corrigir Diretamente no Banco de Dados

**⚠️ USE COM CUIDADO - Apenas para desenvolvedores experientes**

```sql
-- Atualizar número do WhatsApp
UPDATE configuracao_whatsapp
SET twilio_whatsapp_number = '+14155238886'  -- Substitua pelo seu número
WHERE id = 1;
```

---

## Validação da Correção

Após aplicar a correção, verifique se o número foi atualizado:

```bash
python3 verificar_whatsapp.py
```

Você deve ver algo como:

```
[5/6] Verificando configuração do WhatsApp...
  ID: 1
  Status: 🟢 ATIVADO
  Twilio Account SID: ✓ Configurado
  Twilio Auth Token: ✓ Configurado
  Número WhatsApp: +14155238886 ✓
```

---

## Números Válidos do Twilio

### Twilio Sandbox (Ambiente de Teste)
- **Número:** `+14155238886`
- **Formato:** `whatsapp:+14155238886`
- **Uso:** Teste gratuito, requer opt-in com código
- **Como usar:** Envie mensagem para +1 415 523 8886 com o código do sandbox

### Número Real do WhatsApp Business
- **Formato:** `+[código_país][ddd][número]`
- **Exemplos:**
  - Brasil: `+5585999999999`
  - EUA: `+12025551234`
  - Portugal: `+351912345678`

**Importante:** Para usar número real, você precisa:
1. Ter uma conta Twilio com WhatsApp Business aprovado
2. Configurar o número no Twilio Console
3. Aguardar aprovação da Meta (Facebook)

---

## Melhorias Implementadas

Para evitar que esse erro aconteça novamente, foram adicionadas as seguintes validações:

### 1. Validação na API (whatsapp_service.py)

```python
# Valida número do remetente (Twilio WhatsApp)
if not self.config.twilio_whatsapp_number:
    logger.error("Número do WhatsApp não configurado")
    return False, "Número do WhatsApp não configurado. Configure em /admin/whatsapp"

if len(self.config.twilio_whatsapp_number) < 10 or not self.config.twilio_whatsapp_number.startswith('+'):
    logger.error(f"Número do WhatsApp inválido: '{self.config.twilio_whatsapp_number}'")
    return False, f"Número do WhatsApp inválido: '{self.config.twilio_whatsapp_number}'. Deve começar com '+' e ter pelo menos 10 dígitos."
```

### 2. Validação no Painel Admin (routes_whatsapp.py)

```python
# Valida número do WhatsApp
whatsapp_number = request.form.get('twilio_whatsapp_number', '').strip()
if whatsapp_number:
    # Valida formato
    if not whatsapp_number.startswith('+'):
        flash('Número do WhatsApp deve começar com + (código do país). Exemplo: +14155238886', 'danger')
        return redirect(url_for('whatsapp_admin.configuracao'))

    if len(whatsapp_number) < 10:
        flash('Número do WhatsApp muito curto. Exemplo: +14155238886 ou +5585999999999', 'danger')
        return redirect(url_for('whatsapp_admin.configuracao'))

    # Remove caracteres inválidos (aceita apenas números e +)
    if not all(c.isdigit() or c == '+' for c in whatsapp_number):
        flash('Número do WhatsApp deve conter apenas números e + no início. Exemplo: +14155238886', 'danger')
        return redirect(url_for('whatsapp_admin.configuracao'))
```

---

## Próximos Passos

Após corrigir o número do WhatsApp:

1. **Teste o envio** no painel `/admin/whatsapp`
2. **Configure o webhook** no Twilio Console:
   - URL: `https://seu-dominio.com/whatsapp/webhook`
   - Método: POST
3. **Teste recebimento** enviando mensagem para o número do WhatsApp

---

## Recursos Úteis

- **Twilio Console:** https://console.twilio.com
- **Twilio Sandbox Setup:** https://www.twilio.com/console/sms/whatsapp/sandbox
- **Documentação Twilio WhatsApp:** https://www.twilio.com/docs/whatsapp
- **Erros Twilio:** https://www.twilio.com/docs/errors/21212

---

## Suporte

Se o erro persistir após aplicar a correção:

1. Verifique os logs do sistema
2. Confirme que as credenciais Twilio estão corretas
3. Teste a conexão com a API do Twilio
4. Verifique se o número está aprovado no Twilio Console

Para mais ajuda, consulte o arquivo `GUIA_WHATSAPP_COMPLETO.md`.
