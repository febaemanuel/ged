# 📚 Referência Rápida - Evolution API v2.x

> Documentação baseada na Evolution API v2.1.1+ (compatível com v2.2.2)

## 🔧 Configuração Básica

### URL Base
```
http://host.docker.internal:8080
```

### Autenticação
Todas as requisições requerem o header:
```
apikey: <SUA_API_KEY>
```

---

## 📋 Endpoints Principais

### 1️⃣ **Criar Instância**

```http
POST /instance/create
Content-Type: application/json
apikey: <API_KEY>

{
  "instanceName": "nome_da_instancia",
  "token": "<API_KEY>",
  "qrcode": true,
  "integration": "WHATSAPP-BAILEYS"
}
```

**Resposta (201):**
```json
{
  "instance": {
    "instanceName": "nome_da_instancia",
    "status": "created"
  },
  "hash": {
    "apikey": "<API_KEY>"
  },
  "qrcode": {
    "code": "...",
    "base64": "data:image/png;base64,..."
  }
}
```

---

### 2️⃣ **Listar Instâncias**

```http
GET /instance/fetchInstances
apikey: <API_KEY>
```

**Resposta (200):**
```json
[
  {
    "instance": {
      "instanceName": "principal12",
      "owner": "evolution_ged",
      "profileName": "GED EBSERH",
      "profilePictureUrl": "...",
      "integration": "WHATSAPP-BAILEYS",
      "serverUrl": "http://host.docker.internal:8080",
      "apikey": "***",
      "status": "open"
    },
    "state": "open"
  }
]
```

---

### 3️⃣ **Verificar Status da Conexão**

```http
GET /instance/connectionState/{instanceName}
apikey: <API_KEY>
```

**Resposta (200):**
```json
{
  "instance": {
    "instanceName": "principal12",
    "state": "open"
  }
}
```

**Estados possíveis:**
- `open` - Conectado
- `close` - Desconectado
- `connecting` - Conectando

---

### 4️⃣ **Conectar/Obter QR Code**

```http
GET /instance/connect/{instanceName}
apikey: <API_KEY>
```

**Resposta quando desconectado (200):**
```json
{
  "code": "TEXTO_DO_QR_CODE",
  "base64": "data:image/png;base64,iVBORw0KGg...",
  "count": 1
}
```

**Resposta quando já conectado (200):**
```json
{
  "instance": {
    "instanceName": "principal12",
    "state": "open"
  }
}
```

---

### 5️⃣ **Enviar Mensagem de Texto**

```http
POST /message/sendText/{instanceName}
Content-Type: application/json
apikey: <API_KEY>

{
  "number": "5585999999999@s.whatsapp.net",
  "text": "Olá! Esta é uma mensagem de teste.",
  "delay": 1000
}
```

**Formato do número:**
- Com sufixo: `5585999999999@s.whatsapp.net`
- Sem prefixo: `5585999999999`

**Resposta (200):**
```json
{
  "key": {
    "remoteJid": "5585999999999@s.whatsapp.net",
    "fromMe": true,
    "id": "BAE5F4F5D5E5F4F5D5E5F4F5"
  },
  "message": {
    "conversation": "Olá! Esta é uma mensagem de teste."
  },
  "messageTimestamp": "1700000000",
  "status": "PENDING"
}
```

---

### 6️⃣ **Enviar Mensagem com Mídia**

```http
POST /message/sendMedia/{instanceName}
Content-Type: application/json
apikey: <API_KEY>

{
  "number": "5585999999999@s.whatsapp.net",
  "mediatype": "image",
  "media": "https://exemplo.com/imagem.jpg",
  "caption": "Legenda da imagem",
  "delay": 1000
}
```

**Tipos de mídia:**
- `image` - Imagem
- `video` - Vídeo
- `audio` - Áudio
- `document` - Documento

---

### 7️⃣ **Deletar Instância**

```http
DELETE /instance/delete/{instanceName}
apikey: <API_KEY>
```

**Resposta (200):**
```json
{
  "status": "deleted",
  "instanceName": "principal12"
}
```

---

## 🎣 Webhooks

### Configurar Webhook via API

```http
POST /webhook/set/{instanceName}
Content-Type: application/json
apikey: <API_KEY>

{
  "url": "http://127.0.0.1:5000/whatsapp/webhook",
  "webhook_by_events": false,
  "webhook_base64": false,
  "events": [
    "QRCODE_UPDATED",
    "CONNECTION",
    "MESSAGES_UPSERT",
    "MESSAGES_UPDATE",
    "SEND_MESSAGE"
  ]
}
```

### Formato do Webhook Recebido

```json
{
  "event": "messages.upsert",
  "instance": "principal12",
  "data": {
    "key": {
      "remoteJid": "5585999999999@s.whatsapp.net",
      "fromMe": false,
      "id": "MESSAGE_ID"
    },
    "message": {
      "conversation": "Texto da mensagem"
    },
    "messageTimestamp": "1700000000",
    "pushName": "Nome do Usuário"
  }
}
```

---

## ⚠️ Erros Comuns

### 403 - Forbidden
```json
{
  "error": "Access denied"
}
```
**Causa:** API Key inválida ou não enviada

**Solução:** Verifique se o header `apikey` está correto

---

### 404 - Not Found
```json
{
  "error": "Instance not found"
}
```
**Causa:** Instância não existe

**Solução:** Crie a instância com POST `/instance/create`

---

### 500 - Internal Server Error
```json
{
  "error": "Internal server error"
}
```
**Causa:** Erro no servidor ou banco de dados

**Solução:** Verifique os logs do Docker: `docker logs evolution_api`

---

## 🧪 Testando a API

### 1. Verificar se está online

```bash
curl http://host.docker.internal:8080/
```

### 2. Listar instâncias

```bash
curl -X GET "http://host.docker.internal:8080/instance/fetchInstances" \
  -H "apikey: SUA_API_KEY"
```

### 3. Criar instância

```bash
curl -X POST "http://host.docker.internal:8080/instance/create" \
  -H "Content-Type: application/json" \
  -H "apikey: SUA_API_KEY" \
  -d '{
    "instanceName": "teste",
    "token": "SUA_API_KEY",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
  }'
```

### 4. Obter QR Code

```bash
curl -X GET "http://host.docker.internal:8080/instance/connect/teste" \
  -H "apikey: SUA_API_KEY"
```

---

## 📝 Notas Importantes

1. **API Key:** Configurada no `.env` como `AUTHENTICATION_API_KEY`
2. **Formato de número:** Sempre use `@s.whatsapp.net` ou deixe a API adicionar
3. **QR Code expira em ~30 segundos:** Implemente auto-refresh
4. **Estado `open`:** Significa que WhatsApp está conectado
5. **Webhooks:** Configure para receber mensagens automaticamente

---

**Versão:** Evolution API v2.2.2
**Atualizado em:** 21/11/2024
