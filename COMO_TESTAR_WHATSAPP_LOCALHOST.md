# 🚀 Como Testar WhatsApp Bot no Seu Localhost

## ✅ Sim, funciona no localhost! Veja como:

---

## 🎯 Checklist Rápido

- [ ] Python e dependências instaladas (`pip install -r requirements.txt`)
- [ ] Conta Twilio criada (grátis em twilio.com)
- [ ] WhatsApp Sandbox ativado no Twilio
- [ ] 2 terminais abertos (um para Flask, outro para túnel)

---

## 📋 Passo a Passo

### 1️⃣ Instalar Dependências

```bash
# Ativar ambiente virtual (Windows)
venv\Scripts\activate

# Instalar tudo
pip install -r requirements.txt
```

**IMPORTANTE:** Use `pip install twilio`, NÃO `pip install twilio-cli`

---

### 2️⃣ Configurar Twilio (só uma vez)

1. Criar conta: https://www.twilio.com/try-twilio
2. Anotar credenciais:
   - Account SID
   - Auth Token
3. Ativar WhatsApp Sandbox: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
4. Copiar número WhatsApp (ex: `+14155238886`)

---

### 3️⃣ Rodar Migration (só uma vez)

```bash
cd C:\Users\febae\Downloads\ged-claude-clarify-status-difference-01SJh7mZ3ifDdmR1NbwcKWcr
python migrations/add_whatsapp_tables.py
```

---

### 4️⃣ Rodar Flask

**Terminal 1:**
```bash
python app.py
```

Deve mostrar:
```
* Running on http://127.0.0.1:5000
```

---

### 5️⃣ Criar Túnel (expor localhost para internet)

**Terminal 2:**
```bash
ssh -R 80:localhost:5000 localhost.run
```

**Você verá:**
```
Connect to your tunnel via HTTPS:
https://abc-123-xyz.localhost.run

This URL will forward all traffic to localhost:5000
```

**⚠️ COPIE ESSA URL!** (ex: `https://abc-123-xyz.localhost.run`)

---

### 6️⃣ Configurar Webhook no Twilio

1. Acesse: https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox
2. Em **"When a message comes in"**, cole:
   ```
   https://abc-123-xyz.localhost.run/whatsapp/webhook
   ```
3. Método: **POST**
4. Clique **Save**

---

### 7️⃣ Configurar no Sistema GED

1. Abra navegador: `http://localhost:5000`
2. Faça login como admin
3. Vá em: `/admin/whatsapp`
4. Preencha:
   - ✅ Marque "WhatsApp ATIVADO"
   - Account SID (do Twilio)
   - Auth Token (do Twilio)
   - Número WhatsApp (do Twilio Sandbox)
5. **Salvar Configurações**

---

### 8️⃣ Testar!

**No WhatsApp do seu celular:**

1. Adicione o número do Twilio nos contatos (ex: `+1 415 523 8886`)
2. Envie mensagem: `join <codigo>` (o código aparece no Twilio Sandbox)
3. Aguarde confirmação
4. Envie: `menu`

**O bot deve responder!** 🎉

---

## 🔍 Verificar se Está Funcionando

### Testar túnel:
```bash
curl https://SUA-URL.localhost.run/whatsapp/webhook
```

Deve retornar: `Webhook WhatsApp OK`

### Ver logs em tempo real:

**Terminal 1 (Flask):**
Já mostra os logs

**Ou ver arquivo de log:**
```bash
tail -f logs/app.log
```

---

## ⚠️ Problemas Comuns

### ❌ "ssh: connect to host localhost.run port 22: Connection refused"

**Solução:** Use alternativa:

```bash
# Instalar localtunnel
npm install -g localtunnel

# Rodar
lt --port 5000
```

Te dá URL tipo: `https://abc-xyz.loca.lt`

---

### ❌ "Tunnel URL mudou"

**Causa:** Toda vez que reiniciar o SSH, a URL muda

**Solução:**
1. Copie a nova URL
2. Atualize no Twilio Webhook
3. Salve

---

### ❌ "Webhook não recebe mensagens"

**Checklist:**
- [ ] Flask rodando?
- [ ] Túnel ativo?
- [ ] URL correta no Twilio?
- [ ] URL termina com `/whatsapp/webhook`?
- [ ] Método POST selecionado?

---

### ❌ "Cannot import name 'Client' from 'twilio.rest'"

**Solução:**
```bash
pip install --upgrade twilio
```

---

### ❌ "WhatsApp não configurado"

**Solução:**
1. Acesse `/admin/whatsapp`
2. Marque toggle "WhatsApp ATIVADO"
3. Preencha credenciais
4. Salve

---

## 🎯 Fluxo Completo

```
[Seu PC] Flask :5000
    ↓
[Túnel] localhost.run → Internet
    ↓
[Twilio] Recebe mensagem WhatsApp
    ↓
[Twilio] Envia POST para seu webhook
    ↓
[Túnel] Encaminha para localhost:5000
    ↓
[Flask] Processa e responde
    ↓
[Twilio] Envia resposta para WhatsApp
    ↓
[Você] Recebe no celular 🎉
```

---

## 💡 Dicas

### Mantenha 2 terminais abertos:
- **Terminal 1:** `python app.py` (Flask)
- **Terminal 2:** `ssh -R 80:localhost:5000 localhost.run` (Túnel)

### Para desenvolvimento:
- Use `localhost.run` (grátis, sem cadastro)
- URL muda a cada restart (não é problema para testes)

### Para produção:
- Use Ngrok (URLs fixas com plano pago)
- Ou hospede em servidor real (Heroku, AWS, etc.)

---

## 📱 Comandos Úteis

### Reiniciar Flask (se fizer alteração no código):
```bash
# Ctrl+C no Terminal 1
python app.py
```

### Reiniciar túnel (se cair):
```bash
# Ctrl+C no Terminal 2
ssh -R 80:localhost:5000 localhost.run
# Copie nova URL e atualize no Twilio
```

### Ver status do WhatsApp:
```bash
curl http://localhost:5000/admin/whatsapp
```

---

## ✅ Resumo: 3 Passos

```bash
# Terminal 1
python app.py

# Terminal 2
ssh -R 80:localhost:5000 localhost.run
# Copie a URL

# Navegador
1. Configure URL no Twilio Webhook
2. Configure credenciais em /admin/whatsapp
3. Teste enviando "menu" no WhatsApp
```

**Pronto! Seu bot está funcionando no localhost!** 🚀

---

## 📚 Mais Informações

- Guia completo do bot: `WHATSAPP_CHATBOT_GUIA.md`
- Teste localhost: `TESTE_LOCALHOST_WHATSAPP.md`
- Instalação dependências: `INSTALACAO_DEPENDENCIAS_WHATSAPP.md`

---

## 🆘 Ainda com Problemas?

**Debug completo:**

```bash
# Ver logs Flask
tail -f logs/app.log

# Testar webhook localmente (sem Twilio)
curl -X POST http://localhost:5000/whatsapp/webhook \
  -d "From=whatsapp:+5585999999999" \
  -d "Body=menu"

# Ver logs Twilio
https://console.twilio.com/us1/monitor/logs/debugger
```

**Se nada funcionar:**
1. Verifique se porta 5000 está livre: `netstat -ano | findstr :5000`
2. Teste Flask: `curl http://localhost:5000`
3. Verifique firewall
