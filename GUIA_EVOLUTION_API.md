# 📱 Guia Completo: Integração com Evolution API

**Sistema GED EBSERH - WhatsApp via Evolution API**

---

## 📋 Índice

1. [Introdução](#introdução)
2. [Por que Evolution API?](#por-que-evolution-api)
3. [Instalação da Evolution API](#instalação-da-evolution-api)
4. [Configuração no Sistema GED](#configuração-no-sistema-ged)
5. [Conexão do WhatsApp](#conexão-do-whatsapp)
6. [Testes e Validação](#testes-e-validação)
7. [Troubleshooting](#troubleshooting)
8. [Migração do Twilio](#migração-do-twilio)

---

## 🎯 Introdução

A **Evolution API** é uma API open-source para integração com WhatsApp que substituiu o Twilio neste projeto. Oferece todas as funcionalidades necessárias sem custos por mensagem e sem burocracia.

### Funcionalidades Suportadas

✅ **Envio de mensagens** de texto
✅ **Recebimento de mensagens** via webhook
✅ **Chatbot conversacional** com estados
✅ **Assinatura digital** de documentos via WhatsApp
✅ **Notificações** de tarefas
✅ **Multi-instâncias** (vários números WhatsApp)
✅ **QR Code** para conexão fácil

---

## 🏆 Por que Evolution API?

| Critério | Evolution API | Twilio |
|----------|---------------|--------|
| **Custo** | ✅ Gratuita | ❌ Pago por mensagem |
| **Burocracia** | ✅ Zero | ❌ Aprovação, documentos |
| **Hospedagem** | ✅ Própria | ❌ Terceiros |
| **Código** | ✅ Open Source | ❌ Proprietário |
| **Multi-instância** | ✅ Ilimitadas | ❌ Pago por número |
| **Controle** | ✅ Total | ❌ Limitado |

---

## 🚀 Instalação da Evolution API

### Opção 1: Docker (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/EvolutionAPI/evolution-api.git
cd evolution-api

# Copie o arquivo de exemplo
cp .env.example .env

# Edite as configurações
nano .env

# Inicie com Docker Compose
docker-compose up -d
```

**Configurações mínimas no `.env`:**

```bash
# Servidor
SERVER_URL=http://seu-servidor.com
PORT=8080

# API Key (gere uma chave aleatória)
AUTHENTICATION_API_KEY=sua-chave-super-secreta-aqui

# Banco de dados (opcional, mas recomendado)
DATABASE_ENABLED=true
DATABASE_CONNECTION_URI=postgresql://user:pass@localhost:5432/evolution

# Webhook (configuraremos depois)
WEBHOOK_GLOBAL_ENABLED=false
```

**Inicie o servidor:**

```bash
docker-compose up -d
```

**Verifique se está rodando:**

```bash
curl http://localhost:8080/
```

### Opção 2: Instalação Manual (Node.js)

```bash
# Clone o repositório
git clone https://github.com/EvolutionAPI/evolution-api.git
cd evolution-api

# Instale dependências
npm install

# Configure .env
cp .env.example .env
nano .env

# Inicie
npm start
```

### Opção 3: Serviços de Hospedagem

**Railway:**
1. Acesse [railway.app](https://railway.app)
2. Conecte seu GitHub
3. Deploy da Evolution API
4. Configure variáveis de ambiente

**Render:**
1. Acesse [render.com](https://render.com)
2. Novo Web Service
3. Conecte repositório Evolution API
4. Configure env vars

**Heroku, DigitalOcean, AWS, etc:**
Todos suportados! Siga documentação específica de cada plataforma.

---

## ⚙️ Configuração no Sistema GED

### 1. Execute a Migração do Banco de Dados

```bash
cd /home/user/ged
python migrate_to_evolution_api.py
```

**Saída esperada:**

```
============================================================
MIGRAÇÃO: Twilio → Evolution API
============================================================

Conectando ao banco de dados...
Database: localhost:5432/ged_db

Adicionando colunas da Evolution API...
✓ Colunas adicionadas com sucesso!
  - evolution_api_url VARCHAR(200)
  - evolution_instance_name VARCHAR(100)
  - evolution_api_key VARCHAR(200)

✓ Configuração existente encontrada (1 registro)

============================================================
MIGRAÇÃO CONCLUÍDA COM SUCESSO!
============================================================
```

### 2. Configure o Sistema GED

Acesse o painel administrativo:

```
http://localhost:5000/admin/whatsapp
```

**Preencha:**

| Campo | Valor | Exemplo |
|-------|-------|---------|
| **Ativo** | ☑️ Marcado | - |
| **URL Evolution API** | URL completa da API | `http://localhost:8080` |
| **Nome da Instância** | Nome único | `ged_ebserh_production` |
| **API Key** | Chave da Evolution API | `sua-chave-super-secreta-aqui` |

**Funcionalidades:**
- ☑️ Usar para notificações
- ☑️ Usar para assinaturas
- ☑️ Usar para lembretes

**Segurança:**
- Timeout de sessão: `15` minutos
- Horário de funcionamento: `08:00` às `18:00`
- Dias da semana: Seg-Sex

**Salve as configurações.**

---

## 📱 Conexão do WhatsApp

### Método 1: Via Painel Admin (Recomendado)

1. Acesse `/admin/whatsapp`
2. Clique em **"Obter QR Code"**
3. Escaneie com WhatsApp do celular:
   - Abra WhatsApp
   - Vá em **Configurações** > **Aparelhos conectados**
   - Toque em **"Conectar um aparelho"**
   - Escaneie o QR Code exibido

4. Aguarde confirmação de conexão
5. Teste o envio de mensagem

### Método 2: Via API Evolution

```bash
# 1. Crie uma instância
curl -X POST http://localhost:8080/instance/create \
  -H "Content-Type: application/json" \
  -H "apikey: sua-chave-super-secreta-aqui" \
  -d '{
    "instanceName": "ged_ebserh_production",
    "qrcode": true
  }'

# 2. Obtenha o QR Code
curl -X GET http://localhost:8080/instance/qrcode/ged_ebserh_production \
  -H "apikey: sua-chave-super-secreta-aqui"

# Resposta conterá QR Code em Base64
# Cole em um decodificador online ou use uma ferramenta para exibir
```

### Verificar Status da Conexão

```bash
curl -X GET http://localhost:8080/instance/connectionState/ged_ebserh_production \
  -H "apikey: sua-chave-super-secreta-aqui"
```

**Resposta esperada:**

```json
{
  "instance": {
    "instanceName": "ged_ebserh_production",
    "state": "open"
  }
}
```

---

## 🧪 Testes e Validação

### 1. Teste de Envio via Painel Admin

1. Acesse `/admin/whatsapp`
2. Role até **"Testar Envio"**
3. Digite seu número: `+5585999999999`
4. Clique em **"Enviar Teste"**

**Mensagem esperada no WhatsApp:**

```
🧪 Mensagem de Teste - Sistema GED

Olá! Esta é uma mensagem de teste do sistema GED EBSERH.

✅ Configuração do WhatsApp está funcionando corretamente!

📱 Responda menu para ver suas tarefas pendentes.

Teste realizado por: Admin
Data/Hora: 20/11/2025 14:30:00
```

### 2. Teste do Chatbot

Envie mensagem para o número conectado:

```
menu
```

**Resposta esperada:**

```
📋 Documentos Pendentes de Assinatura (3)

1️⃣ 📄 POP.ENFERMAGEM-001
   Procedimento Operacional Padrão - Curativos
   🗓️ Prazo: 25/11

2️⃣ 📄 MAN.ADMIN-005
   Manual Administrativo - RH
   🗓️ Prazo: 30/11

3️⃣ ⏰ PROT.INFEC-010
   Protocolo de Infecção Hospitalar
   🗓️ Prazo: 20/11

💬 Responda o número do documento para ver opções

Digite 'ajuda' para ver comandos disponíveis
```

### 3. Teste de Assinatura Digital

1. Envie `1` (escolhe primeiro documento)
2. Envie `1` (aprova e assina)
3. Digite seu email cadastrado
4. Verifique a confirmação

**Resposta esperada:**

```
✅ ASSINATURA REGISTRADA COM SUCESSO!

📋 Documento: POP.ENFERMAGEM-001
⏰ Data/Hora: 20/11/2025 14:35:42
🔐 Hash: a3f5c9e8b2d1f4a6...
📧 Protocolo: #ASS-123

📧 Comprovante enviado para: seu-email@example.com

Sua assinatura digital foi registrada com validade jurídica.
```

---

## 🔧 Troubleshooting

### Problema: "WhatsApp não está ativo ou não configurado"

**Solução:**

1. Verifique se Evolution API está rodando:
   ```bash
   curl http://localhost:8080/
   ```

2. Verifique configurações em `/admin/whatsapp`:
   - ☑️ Ativo marcado
   - URL correta (sem trailing slash)
   - API Key correta
   - Nome da instância correto

3. Verifique logs:
   ```bash
   tail -f logs/app.log | grep -i whatsapp
   ```

### Problema: "Erro HTTP 404 Not Found"

**Solução:**

- Verifique se a instância existe:
  ```bash
  curl http://localhost:8080/instance/fetchInstances \
    -H "apikey: sua-chave"
  ```

- Crie a instância se não existir:
  ```bash
  curl -X POST http://localhost:8080/instance/create \
    -H "Content-Type: application/json" \
    -H "apikey: sua-chave" \
    -d '{"instanceName": "ged_ebserh_production", "qrcode": true}'
  ```

### Problema: "QR Code não aparece"

**Solução:**

- WhatsApp já está conectado! Verifique status:
  ```bash
  curl http://localhost:8080/instance/connectionState/ged_ebserh_production \
    -H "apikey: sua-chave"
  ```

- Se `state: "close"`, desconecte e reconecte:
  ```bash
  curl -X DELETE http://localhost:8080/instance/logout/ged_ebserh_production \
    -H "apikey: sua-chave"
  ```

### Problema: Mensagens não são recebidas

**Solução:**

1. Configure webhook na Evolution API:
   ```bash
   curl -X POST http://localhost:8080/webhook/set/ged_ebserh_production \
     -H "Content-Type: application/json" \
     -H "apikey: sua-chave" \
     -d '{
       "url": "https://seu-dominio.com/whatsapp/webhook",
       "events": ["messages.upsert"]
     }'
   ```

2. Verifique se webhook está acessível:
   ```bash
   curl https://seu-dominio.com/whatsapp/webhook
   ```

3. Verifique logs do webhook na Evolution API

### Problema: Timeout ao enviar mensagens

**Solução:**

- Aumente timeout no código (padrão: 30s):
  ```python
  # app/services/evolution_api_service.py
  response = requests.post(url, headers=headers, json=payload, timeout=60)
  ```

- Verifique latência de rede:
  ```bash
  ping seu-servidor-evolution-api.com
  ```

---

## 🔄 Migração do Twilio

Se você estava usando Twilio anteriormente:

### 1. Backup dos Dados

```bash
# Backup do banco de dados
pg_dump ged_db > backup_antes_migracao.sql

# Backup das configurações
cp .env .env.backup.twilio
```

### 2. Execute a Migração

```bash
python migrate_to_evolution_api.py
```

### 3. Reconfigure WhatsApp

1. Acesse `/admin/whatsapp`
2. Preencha campos da Evolution API
3. Deixe campos Twilio em branco (serão ignorados)
4. Salve e teste

### 4. Desinstale Twilio (Opcional)

```bash
pip uninstall twilio
```

### 5. Rollback (Se Necessário)

Se precisar voltar para Twilio:

```bash
# Restaure backup
psql ged_db < backup_antes_migracao.sql

# Restaure .env
cp .env.backup.twilio .env

# Reinstale Twilio
pip install twilio

# Renomeie serviço antigo
mv app/services/evolution_api_service.py app/services/evolution_api_service.py.bak
mv app/services/whatsapp_service.py.old app/services/whatsapp_service.py
```

---

## 📊 Estatísticas e Monitoramento

### Visualizar Logs de Mensagens

Acesse: `/admin/whatsapp/logs`

- Mensagens enviadas
- Mensagens recebidas
- Taxa de sucesso
- Erros

### Métricas Importantes

| Métrica | Descrição | Onde Ver |
|---------|-----------|----------|
| **Total de Mensagens** | Enviadas + recebidas | Dashboard Admin |
| **Taxa de Falha** | % de mensagens que falharam | Logs |
| **Tempo Médio** | Resposta do chatbot | Logs detalhados |
| **Assinaturas via WhatsApp** | Total de documentos assinados | Relatórios |

---

## 🔒 Segurança

### Boas Práticas

✅ **API Key forte**: Mínimo 32 caracteres aleatórios
✅ **HTTPS**: Sempre use HTTPS em produção
✅ **Firewall**: Restrinja acesso à porta 8080 (Evolution API)
✅ **Backup**: Faça backup regular do banco de dados
✅ **Logs**: Monitore logs de acesso e erros
✅ **Timeout**: Configure timeout adequado (15 min padrão)
✅ **Horários**: Restrinja funcionamento a horário comercial

### Webhook Seguro

Configure validação de webhook:

```python
# app/routes/routes_whatsapp.py
@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    # Valida API Key do webhook
    api_key_header = request.headers.get('apikey')
    if api_key_header != current_app.config['EVOLUTION_API_KEY']:
        return jsonify({'error': 'Unauthorized'}), 401

    # Processa normalmente
    ...
```

---

## 📚 Recursos Adicionais

- **Documentação Evolution API**: https://doc.evolution-api.com
- **GitHub**: https://github.com/EvolutionAPI/evolution-api
- **Comunidade**: Discord, Telegram (veja GitHub)
- **Issues**: Reporte bugs no GitHub

---

## ✅ Checklist de Instalação

Use este checklist para garantir que tudo está configurado:

- [ ] Evolution API instalada e rodando
- [ ] Instância criada
- [ ] Migração do banco executada (`migrate_to_evolution_api.py`)
- [ ] Configurações preenchidas em `/admin/whatsapp`
- [ ] WhatsApp conectado via QR Code
- [ ] Teste de envio bem-sucedido
- [ ] Teste do chatbot (`menu`) funcionando
- [ ] Webhook configurado
- [ ] Teste de assinatura digital funcionando
- [ ] Logs de mensagens aparecendo
- [ ] HTTPS configurado (produção)
- [ ] Backup do banco de dados configurado

---

## 🎉 Conclusão

Parabéns! Você migrou com sucesso para a **Evolution API**!

**Vantagens conquistadas:**
- ✅ Zero custos por mensagem
- ✅ Controle total da infraestrutura
- ✅ Sem aprovações ou burocracias
- ✅ Múltiplas instâncias gratuitas
- ✅ Open source e customizável

**Dúvidas?** Consulte a seção de Troubleshooting ou abra uma issue no GitHub do projeto.

---

**Desenvolvido para Sistema GED EBSERH**
**Versão Evolution API:** 2.x
**Data:** Novembro 2025
