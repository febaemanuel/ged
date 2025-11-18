# Correção do Erro: Twilio Sender ID Inválido

## Problema

Erro ao enviar mensagem pelo WhatsApp:

```
HTTP Error POST /Accounts/ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/Messages.json
Unable to create record: The 'From' number wh is not a valid phone number, shortcode, or alphanumeric sender ID.
```

**Causa:** O número do WhatsApp está configurado como `"wh"` ao invés de um número válido como `+14155238886`.

---

## Solução (Simples)

### Opção 1: Corrigir pelo Painel Administrativo (Recomendado)

1. Acesse o sistema GED pelo navegador
2. Faça login como administrador
3. Vá para **Menu → Gestão → WhatsApp**
4. No campo "Número WhatsApp", digite o número completo com código do país:
   - Exemplo Twilio Sandbox: `+14155238886`
   - Exemplo Brasil: `+5585999999999`
5. Clique em **Salvar Configurações**

### Opção 2: Corrigir Diretamente no Banco de Dados

```sql
UPDATE configuracao_whatsapp
SET twilio_whatsapp_number = '+14155238886'
WHERE id = 1;
```

Substitua `+14155238886` pelo seu número real do WhatsApp.

**Exemplos de números válidos:**
- Twilio Sandbox: `+14155238886`
- Brasil: `+5585999999999`
- EUA: `+12025551234`

---

## Proteções Adicionadas

O sistema agora valida automaticamente o número do WhatsApp:

**No painel admin:**
- Rejeita números sem `+` no início
- Rejeita números com menos de 10 dígitos
- Aceita apenas números e `+`
- Exibe mensagem de erro clara

**Na API de envio:**
- Verifica se o número está configurado
- Valida formato antes de enviar
- Retorna erro descritivo se inválido

Essas validações previnem que números inválidos sejam salvos ou usados.

---

## Após Corrigir

1. Teste o envio no painel `/admin/whatsapp`
2. Configure o webhook no Twilio Console
3. Teste o recebimento de mensagens

Se o erro persistir, verifique:
- Credenciais Twilio estão corretas
- Número está aprovado no Twilio Console
- Logs do sistema para mais detalhes
