# 🔑 Como Encontrar a API Key da Evolution API

## Problema Identificado

A Evolution API está retornando **"Access denied"** porque a API Key está incorreta.

---

## 📋 Passos para Encontrar a API Key Correta

### Opção 1: Verificar o arquivo .env da Evolution API

A API Key é definida no arquivo `.env` onde você instalou a Evolution API.

```bash
# 1. Vá até a pasta da Evolution API (onde tem o docker-compose.yml)
cd /caminho/para/evolution-api

# 2. Veja o conteúdo do arquivo .env
cat .env | grep AUTHENTICATION_API_KEY

# Ou se preferir, abra o arquivo:
nano .env
```

Procure pela linha:
```env
AUTHENTICATION_API_KEY=SUA_API_KEY_AQUI
```

**Essa é a API Key que você deve usar no GED!**

---

### Opção 2: Verificar variáveis de ambiente do Docker

Se a Evolution API está rodando em Docker, você pode verificar assim:

```bash
# 1. Liste os containers em execução
docker ps

# 2. Encontre o container da Evolution API (provavelmente evolution_api)
# 3. Veja as variáveis de ambiente
docker inspect evolution_api | grep AUTHENTICATION_API_KEY
```

---

### Opção 3: Verificar logs do container

```bash
# Veja os logs do container da Evolution API
docker logs evolution_api 2>&1 | head -50

# A API Key pode aparecer nos logs de inicialização
```

---

### Opção 4: Criar uma Nova API Key

Se você não encontrar a API Key antiga, pode criar uma nova:

```bash
# 1. Pare a Evolution API
docker-compose down

# 2. Edite o arquivo .env
nano .env

# 3. Modifique ou adicione a linha (use uma senha forte):
AUTHENTICATION_API_KEY=minhasenhaforte123456

# 4. Reinicie a Evolution API
docker-compose up -d

# 5. Verifique os logs
docker-compose logs -f evolution_api
```

---

## ✅ Depois de Encontrar a API Key

1. **Acesse a página de configuração WhatsApp no GED:**
   ```
   http://127.0.0.1:5000/admin/whatsapp
   ```

2. **Preencha os campos:**
   - **URL da Evolution API:** `http://192.168.18.6:8080`
   - **Nome da Instância:** `principal12`
   - **API Key:** A senha que você encontrou no .env

3. **Clique em "Salvar Configurações"**

4. **Clique em "Obter QR Code"**

5. **Escaneie com seu WhatsApp**

---

## 🔍 Testando a API Key

Para testar se a API Key está correta, execute:

```bash
# Substitua YOUR_API_KEY pela API Key do .env
curl -X GET "http://192.168.18.6:8080/instance/fetchInstances" \
  -H "apikey: YOUR_API_KEY"
```

Se retornar uma lista (pode ser vazia `[]`), a API Key está correta!

Se retornar "Access denied", a API Key está incorreta.

---

## 📝 Exemplo do arquivo .env da Evolution API

```env
# ================================
# CONFIGURAÇÃO PRINCIPAL
# ================================
SERVER_TYPE=http
PORT=8080
SERVER_URL=http://192.168.18.6:8080/

# Sua chave de segurança (copie essa para usar no painel do GED depois)
AUTHENTICATION_API_KEY=12345678  # ← ESSA É A SUA API KEY!
AUTHENTICATION_EXPOSE_IN_FETCH_INSTANCES=true

# ================================
# BANCO DE DADOS (Conexão com Windows)
# ================================
DATABASE_ENABLED=true
DATABASE_PROVIDER=postgresql
DATABASE_CONNECTION_URI=postgresql://postgres:1234@host.docker.internal:5432/evolution?schema=public
```

---

## 🆘 Precisa de Ajuda?

Se ainda não conseguir:

1. **Envie o conteúdo do arquivo .env** (REMOVA senhas sensíveis antes!)
2. **Mostre os logs:** `docker logs evolution_api`
3. **Verifique se o container está rodando:** `docker ps | grep evolution`

---

**Última atualização:** 21/11/2024
