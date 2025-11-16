# 🚀 Testar WhatsApp Bot em Localhost

## Método Simples: localhost.run

### Passo 1: Inicie sua aplicação Flask
```bash
python app.py
# ou
flask run
```

Sua aplicação deve estar rodando em `http://localhost:5000`

### Passo 2: Exponha para internet (1 comando!)
Em outro terminal:
```bash
ssh -R 80:localhost:5000 localhost.run
```

Você verá algo assim:
```
Connect to your tunnel via HTTP or HTTPS:
https://abc123-xyz.localhost.run

This is a custom subdomain for a custom certificate,
running on a shared IP address.
```

**Copie a URL**: `https://abc123-xyz.localhost.run`

### Passo 3: Configure no Twilio

1. Acesse: https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox
2. Em **"When a message comes in"** cole:
   ```
   https://abc123-xyz.localhost.run/whatsapp/webhook
   ```
3. Método: **POST**
4. Salve

### Passo 4: Teste!

1. Envie mensagem no WhatsApp para o número do Twilio Sandbox
2. Primeiro, conecte ao sandbox enviando o código de join
3. Depois envie: `menu`
4. Pronto! O bot deve responder

---

## ⚠️ Observações

- **localhost.run** cria URLs temporárias
- Cada vez que reiniciar o SSH, a URL muda
- É perfeito para testes rápidos
- **Gratuito e sem cadastro!**

---

## Alternativa: localtunnel (também simples)

```bash
# Instala
npm install -g localtunnel

# Executa
lt --port 5000
```

Te dá uma URL tipo: `https://abc-xyz.loca.lt`

---

## 🔍 Verificar se está funcionando

Teste se o túnel está funcionando:
```bash
curl https://SUA-URL.localhost.run/whatsapp/webhook
```

Deve retornar: `Webhook WhatsApp OK`

---

## 🐛 Debug

### Ver logs do Flask em tempo real:
```bash
tail -f logs/app.log
```

### Ver logs do WhatsApp no código:
O arquivo `/home/user/ged/app/routes/routes_whatsapp.py` tem logs em todas as etapas.

### Testar webhook localmente (sem Twilio):
```bash
curl -X POST http://localhost:5000/whatsapp/webhook \
  -d "From=whatsapp:+5585999999999" \
  -d "Body=menu"
```

---

## 📱 Fluxo completo de teste

1. ✅ Flask rodando: `python app.py`
2. ✅ Túnel ativo: `ssh -R 80:localhost:5000 localhost.run`
3. ✅ Webhook configurado no Twilio
4. ✅ Enviar mensagem no WhatsApp
5. ✅ Ver resposta do bot!

---

**Dica**: Mantenha 2 terminais abertos:
- Terminal 1: Flask rodando
- Terminal 2: Túnel localhost.run

Assim você vê os logs em tempo real enquanto testa!
