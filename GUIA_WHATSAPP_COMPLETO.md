# 📱 WhatsApp Chatbot - Guia Completo

Sistema de assinatura de documentos via WhatsApp integrado ao GED EBSERH.

---

## 📋 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Instalação e Dependências](#instalação-e-dependências)
3. [Configuração Inicial](#configuração-inicial)
4. [Testar em Localhost](#testar-em-localhost)
5. [Painel Administrativo](#painel-administrativo)
6. [Como Funciona](#como-funciona)
7. [Comandos do Chatbot](#comandos-do-chatbot)
8. [Segurança](#segurança)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 VISÃO GERAL

O WhatsApp Chatbot permite que usuários:
- ✅ Recebam notificações de tarefas pendentes
- ✅ Visualizem documentos para assinar
- ✅ **Assinem documentos direto no WhatsApp**
- ✅ Reprovem documentos com justificativa
- ✅ Consultem histórico de assinaturas

**Validação Jurídica:** Todas as assinaturas incluem:
- Hash SHA-256 único
- IP de origem
- Timestamp preciso
- Validação de senha
- Registro em banco de dados

---

## 📦 INSTALAÇÃO E DEPENDÊNCIAS

### ⚠️ IMPORTANTE: twilio vs twilio-cli

**❌ ERRO COMUM:**
```bash
pip install twilio-cli  # ❌ ERRO! Não existe como pacote Python
```

**✅ CORRETO:**
```bash
pip install twilio>=8.10.0  # ✅ Python SDK do Twilio
```

### Por quê?

| Pacote | Tipo | Instalação | Necessário? |
|--------|------|------------|-------------|
| `twilio` | Python SDK | `pip install twilio` | ✅ SIM |
| `twilio-cli` | Node.js CLI | `npm install -g twilio-cli` | ❌ NÃO |

- `twilio-cli` é uma ferramenta **Node.js**, não Python
- É instalada via npm, não pip
- **Você NÃO precisa dela para este projeto!**

### Instalação Correta

**Método 1: Instalar todas as dependências (recomendado)**
```bash
# Ativar ambiente virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar tudo
pip install -r requirements.txt
```

**Método 2: Instalar apenas o Twilio**
```bash
pip install twilio>=8.10.0
```

**Verificar instalação:**
```bash
pip show twilio
```

Deve mostrar:
```
Name: twilio
Version: 8.10.0 (ou superior)
Summary: Twilio API client and TwiML generator
```

---

## 🚀 CONFIGURAÇÃO INICIAL

### Passo 1: Criar Conta Twilio

1. Acesse: https://www.twilio.com/try-twilio
2. Cadastre-se (conta trial gratuita com $15)
3. Copie as credenciais:
   - **Account SID** (ex: ACxxxxxxxxxxxxx)
   - **Auth Token** (ex: 1234567890abcdef)

### Passo 2: Ativar WhatsApp Sandbox

1. Acesse: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. Siga instruções para ativar WhatsApp Sandbox
3. Envie mensagem para o número do Twilio (ex: `join <codigo>`)
4. Copie o **número WhatsApp** (ex: +14155238886)

### Passo 3: Executar Migration

```bash
cd /caminho/do/projeto
python migrations/add_whatsapp_tables.py
```

Isso cria as tabelas:
- `configuracao_whatsapp`
- `conversacoes_whatsapp`
- `logs_whatsapp`

### Passo 4: Configurar no Sistema

1. Faça login como **administrador**
2. Acesse: `/admin/whatsapp`
3. Preencha:
   - ✅ Ative o WhatsApp (toggle)
   - Account SID
   - Auth Token
   - Número WhatsApp
4. Clique em **Salvar Configurações**

---

## 🏠 TESTAR EM LOCALHOST

### ✅ Sim, funciona no localhost! Mas precisa de um túnel

**O Problema:**
- Seu Flask roda em `http://localhost:5000` (só você vê)
- O Twilio (servidores externos) precisa enviar mensagens para seu webhook
- **O Twilio não consegue acessar `localhost:5000` do seu computador!**

**A Solução: Túnel para Internet**

### Método Simples: localhost.run

**Terminal 1: Rodar Flask**
```bash
python app.py
```

Deve mostrar:
```
* Running on http://127.0.0.1:5000
```

**Terminal 2: Criar Túnel**
```bash
ssh -R 80:localhost:5000 localhost.run
```

Você verá:
```
Connect to your tunnel via HTTPS:
https://abc-123-xyz.localhost.run

This URL will forward all traffic to localhost:5000
```

**⚠️ COPIE ESSA URL!** (ex: `https://abc-123-xyz.localhost.run`)

### Configurar Webhook no Twilio

1. Acesse: https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox
2. Em **"When a message comes in"**, cole:
   ```
   https://abc-123-xyz.localhost.run/whatsapp/webhook
   ```
3. Método: **POST**
4. Clique **Save**

### Testar!

**No WhatsApp do seu celular:**

1. Adicione o número do Twilio nos contatos
2. Envie mensagem: `join <codigo>` (código aparece no Twilio Sandbox)
3. Aguarde confirmação
4. Envie: `menu`

**O bot deve responder!** 🎉

### Alternativas ao localhost.run

**Opção 2: localtunnel**
```bash
npm install -g localtunnel
lt --port 5000
```

**Opção 3: ngrok (URLs fixas com plano pago)**
```bash
ngrok http 5000
```

### Fluxo Completo

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

### Dicas para Localhost

- Mantenha 2 terminais abertos (Flask + Túnel)
- URL muda a cada restart do túnel (atualize no Twilio)
- Use `localhost.run` (grátis, sem cadastro)
- Para produção, hospede em servidor real (Heroku, AWS, etc.)

---

## ⚙️ PAINEL ADMINISTRATIVO

### Acesso

**URL:** `/admin/whatsapp`
**Permissão:** Apenas administradores

### Funcionalidades

#### 📊 Estatísticas
- Total de mensagens
- Mensagens enviadas/recebidas
- Falhas de envio
- Usuários com WhatsApp ativo

#### 🔑 Credenciais Twilio
- Account SID
- Auth Token (oculto)
- Número WhatsApp Business

#### ⚙️ Funcionalidades
- **Notificações de Tarefas:** Envia WhatsApp quando tarefa é atribuída
- **Assinaturas via WhatsApp:** Permite assinar pelo chatbot
- **Lembretes de Prazo:** Envia lembretes antes do vencimento

#### 🔒 Segurança
- **2FA:** Exige código SMS além da senha
- **Timeout de Sessão:** Expira conversa após X minutos
- **Deletar Mensagens Sensíveis:** Apaga mensagens com senhas

#### 🕐 Horários de Funcionamento
- **Horário de Início/Término:** Define quando chatbot responde
- **Dias da Semana:** Escolha dias ativos
- Fora do horário, informa usuário

#### 📝 Templates de Mensagens
- Personalize textos das mensagens
- Variáveis: `{nome}`, `{codigo}`, `{prazo}`, etc.
- Acesse: `/admin/whatsapp/templates`

#### 📋 Logs
- Visualize todas mensagens enviadas/recebidas
- Filtre por direção, status, data
- Acesse: `/admin/whatsapp/logs`

---

## 💬 COMO FUNCIONA

### Fluxo Completo de Assinatura

```
1. VALIDADOR UGQ cria Bloco de Assinatura
   ↓
2. SISTEMA envia WhatsApp para Aprovador 1:
   "📲 Você tem 1 documento para assinar: POP-001"
   ↓
3. APROVADOR 1 abre WhatsApp e digita: "menu"
   ↓
4. CHATBOT lista documentos pendentes:
   "1️⃣ POP-DEF-20251116-0001
    2️⃣ MANUAL-DEF-20251116-0002"
   ↓
5. APROVADOR 1 digita: "1"
   ↓
6. CHATBOT mostra detalhes:
   "📄 POP-DEF-20251116-0001
    Higienização de Equipamentos

    O que deseja fazer?
    1️⃣ - Aprovar e assinar
    2️⃣ - Reprovar"
   ↓
7. APROVADOR 1 digita: "1"
   ↓
8. CHATBOT pede senha:
   "🔒 Digite sua senha para confirmar:"
   ↓
9. APROVADOR 1 digita: "minhasenha123"
   ↓
10. SISTEMA:
    - Valida senha
    - Gera hash SHA-256
    - Registra IP, timestamp
    - Marca tarefa como concluída
    - Atualiza bloco de assinatura
    ↓
11. CHATBOT confirma:
    "✅ ASSINATURA REGISTRADA!
     🔐 Hash: a3f7e8c9d2...
     📧 Comprovante enviado para seu email"
    ↓
12. SISTEMA envia WhatsApp para Aprovador 2
    (Repete processo...)
```

---

## 🤖 COMANDOS DO CHATBOT

### Comandos Globais

| Comando | Descrição |
|---------|-----------|
| `menu` | Exibe documentos pendentes |
| `ajuda` | Lista comandos disponíveis |
| `sair` | Encerra conversa |
| `oi`, `olá` | Inicia conversa |

### Fluxo de Navegação

```
menu
 ├─ 1, 2, 3... (escolhe documento)
 │   ├─ 1 (aprovar e assinar)
 │   │   └─ <senha> (confirma assinatura)
 │   ├─ 2 (reprovar)
 │   │   └─ <justificativa> (mínimo 20 caracteres)
 │   ├─ 3 (ver documento completo)
 │   │   └─ Envia link
 │   └─ 4 (voltar ao menu)
 └─ ajuda / sair
```

---

## 🔐 SEGURANÇA

### Medidas Implementadas

#### ✅ Validação de Senha
- Senha do sistema GED validada
- Após 3 tentativas erradas: bloqueio de 30 minutos
- Bloqueio registrado em banco de dados

#### ✅ Hash de Assinatura
```python
hash = SHA256(usuario_id + tarefa_id + timestamp + senha)
```
- Hash armazenado em `ItemBlocoAssinatura`
- Não reversível
- Válido juridicamente

#### ✅ Auditoria Completa
Cada assinatura registra:
- **IP de Origem** (via Twilio headers)
- **User-Agent:** "WhatsApp-Chatbot"
- **Timestamp** (UTC com precisão de segundos)
- **Hash da Assinatura**
- **Parecer** (se reprovado)

#### ✅ Timeout de Sessão
- Padrão: 15 minutos
- Após timeout, conversa expira
- Usuário precisa digitar `menu` novamente

#### ✅ Horário de Funcionamento
- Chatbot só responde em horário configurado
- Fora do horário, informa quando volta
- Previne spam e uso indevido

#### ✅ Deleção de Mensagens Sensíveis
- Mensagens com senhas são deletadas automaticamente
- Reduz risco de exposição
- Configurável no painel admin

### Conformidade LGPD

#### ✅ Consentimento
- Campo `whatsapp_ativo` no usuário
- Usuário pode desativar a qualquer momento
- Opt-out respeitado

#### ✅ Transparência
- Logs de todas mensagens
- Usuário informado sobre coleta de dados
- Finalidade clara (assinatura de documentos)

#### ✅ Segurança de Dados
- Senhas não armazenadas em logs
- Hash unidirecional
- Criptografia em trânsito (Twilio TLS)

---

## 🔧 TROUBLESHOOTING

### 🔍 Verificação Rápida do Sistema

Use o script de verificação para diagnosticar problemas:

```bash
python3 verificar_whatsapp.py
```

**O script verifica:**
- ✅ Conexão com PostgreSQL
- ✅ Existência das tabelas WhatsApp
- ✅ Estado da configuração (ativo/inativo)
- ✅ Credenciais Twilio configuradas
- ✅ Estatísticas de uso (mensagens enviadas/recebidas)
- ✅ Usuários com WhatsApp ativo

---

### ❌ Botão Ativar/Desativar não funciona

**Sintoma:** Botão parece não mudar o estado ou sempre desativa

**Diagnóstico:**
1. Abra DevTools do navegador (F12) → Console
2. Clique no checkbox de ativar/desativar
3. Você deve ver logs:
   ```
   WhatsApp checkbox MARCADO - Será enviado como ativo=on
   ```
   ou
   ```
   WhatsApp checkbox DESMARCADO - Não será enviado (ativo=False no backend)
   ```

4. Clique em "Salvar Configurações"
5. Veja a mensagem flash: "Status: ATIVADO" ou "Status: DESATIVADO"

**Causas Comuns:**
- PostgreSQL não está rodando
- Erro no commit do banco de dados
- JavaScript desabilitado no navegador

**Solução:**
```bash
# 1. Verificar PostgreSQL
sudo service postgresql start
pg_isready -h localhost -p 5432

# 2. Verificar sistema
python3 verificar_whatsapp.py

# 3. Ver logs do servidor
# Ao salvar configuração, deve aparecer:
# INFO - Estado anterior WhatsApp ativo: False
# INFO - WhatsApp False -> True
# INFO - Configuração salva com sucesso por usuário Admin
```

---

### ❌ Erro: "Could not find a version that satisfies the requirement twilio-cli"

**Causa:** Você tentou `pip install twilio-cli`

**Solução:**
```bash
# ❌ Errado
pip install twilio-cli

# ✅ Correto
pip install twilio>=8.10.0
```

---

### ❌ Erro: "No module named 'twilio'"

**Causa:** Pacote `twilio` não instalado

**Solução:**
```bash
pip install twilio>=8.10.0
```

---

### ❌ Erro: "WhatsApp não configurado"

**Causa:** Credenciais Twilio não preenchidas ou WhatsApp desativado.

**Solução:**
1. Acesse `/admin/whatsapp`
2. Verifique se toggle **"WhatsApp ATIVADO"** está marcado (deve ficar verde)
3. Preencha Account SID, Auth Token, Número
4. Clique em "Salvar Configurações"
5. Veja mensagem: "Configurações do WhatsApp salvas com sucesso! Status: ATIVADO"

---

### ❌ Erro: "Número não cadastrado no sistema GED"

**Causa:** Usuário não tem telefone cadastrado ou formato incorreto.

**Solução:**
1. Acesse cadastro de usuários
2. Adicione telefone no formato: `+5585999999999`
   - **+55** (código do país)
   - **85** (DDD)
   - **999999999** (número)
3. Marque checkbox **"Aceita WhatsApp"**

---

### ❌ Erro: "Webhook não recebe mensagens"

**Causa:** URL do webhook não configurada no Twilio.

**Solução:**
1. Acesse: https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox
2. Verifique **"When a message comes in"**
3. Deve ter: `https://SEU_DOMINIO.com/whatsapp/webhook`
4. Método: **POST**
5. Salve e teste enviando "menu" para o WhatsApp

---

### ❌ Erro: "Tunnel URL mudou"

**Causa:** Toda vez que reiniciar o SSH (localhost.run), a URL muda

**Solução:**
1. Copie a nova URL do terminal
2. Atualize no Twilio Webhook
3. Salve

---

### ❌ Mensagem de teste não chega

**Causas Possíveis:**
1. **Número não ativado no Sandbox**
   - Envie `join <codigo>` para o número do Twilio
2. **Formato de número errado**
   - Use: `+5585999999999` (com código do país)
3. **Créditos Twilio esgotados**
   - Conta trial tem $15 grátis
   - Verifique em: https://console.twilio.com/

---

### ❌ Erro: "ssh: connect to host localhost.run port 22: Connection refused"

**Solução:** Use alternativa:

```bash
# Opção 1: localtunnel
npm install -g localtunnel
lt --port 5000

# Opção 2: ngrok
ngrok http 5000
```

---

## 🧪 TESTAR INSTALAÇÃO

### Teste 0: Verificação Completa do Sistema
```bash
python3 verificar_whatsapp.py
```

**Saída esperada:**
```
[1/6] Importando módulos...
✓ Módulos importados com sucesso

[2/6] Criando contexto da aplicação...
✓ Aplicação criada: app

[3/6] Verificando conexão com banco de dados...
✓ Conexão com PostgreSQL estabelecida

[4/6] Verificando tabelas do WhatsApp...
✓ Tabela 'configuracao_whatsapp' existe (13 colunas)
✓ Tabela 'conversacoes_whatsapp' existe (8 colunas)
✓ Tabela 'logs_whatsapp' existe (9 colunas)

[5/6] Verificando configuração do WhatsApp...
  Status: 🟢 ATIVADO / 🔴 DESATIVADO
  Twilio Account SID: ✓ Configurado
  ...

[6/6] Estatísticas de uso...
  Total de mensagens: 0
  Usuários com WhatsApp: 0
```

### Teste 1: Verificar Twilio instalado
```bash
pip show twilio
```

### Teste 2: Testar importação
```python
from twilio.rest import Client
print("✅ Twilio instalado corretamente!")
```

### Teste 3: Testar botão de ativar/desativar
1. Acesse `/admin/whatsapp`
2. Desmarque o checkbox → Veja mudar para amarelo "DESATIVADO"
3. Clique em "Salvar Configurações"
4. Veja mensagem: "Status: DESATIVADO"
5. Marque o checkbox → Veja mudar para verde "ATIVADO"
6. Clique em "Salvar Configurações"
7. Veja mensagem: "Status: ATIVADO"

### Teste 4: Testar webhook localmente
```bash
curl -X POST http://localhost:5000/whatsapp/webhook \
  -d "From=whatsapp:+5585999999999" \
  -d "Body=menu"
```

### Teste 5: Verificar túnel
```bash
curl https://SUA-URL.localhost.run/whatsapp/webhook
```

Deve retornar: `Webhook WhatsApp OK`

---

## 📊 LOGS E MONITORAMENTO

### Visualizar Logs

**URL:** `/admin/whatsapp/logs`

**Informações:**
- Direção (enviada/recebida)
- Telefone
- Mensagem
- Status (enviado, entregue, falhou)
- Data/hora
- Documento/Tarefa relacionada

### Ver logs em tempo real

```bash
# Logs Flask
tail -f logs/app.log

# Logs Twilio (online)
# https://console.twilio.com/us1/monitor/logs/debugger
```

---

## 💡 BOAS PRÁTICAS

### Para Administradores

1. ✅ **Mantenha credenciais seguras**
   - Nunca compartilhe Auth Token
   - Use variáveis de ambiente em produção

2. ✅ **Configure horários adequados**
   - Evite notificações à noite
   - Respeite horário comercial

3. ✅ **Monitore logs regularmente**
   - Verifique falhas de envio
   - Identifique problemas cedo

4. ✅ **Teste regularmente**
   - Envie mensagens de teste
   - Valide webhook funcionando

### Para Usuários

1. ✅ **Mantenha telefone atualizado**
   - Informe mudanças de número
   - Ative WhatsApp no perfil

2. ✅ **Use senhas fortes**
   - Mínimo 8 caracteres
   - Não compartilhe

3. ✅ **Responda prontamente**
   - Sessão expira em 15 minutos
   - Verificar pendências regularmente

---

## ✅ CHECKLIST DE INSTALAÇÃO

- [ ] PostgreSQL rodando (`sudo service postgresql start`)
- [ ] Ambiente virtual criado e ativado
- [ ] `pip install -r requirements.txt` executado com sucesso
- [ ] `pip show twilio` mostra versão >= 8.10.0
- [ ] Migration executada (`python migrations/add_whatsapp_tables.py`)
- [ ] `python3 verificar_whatsapp.py` sem erros
- [ ] Conta Twilio criada
- [ ] WhatsApp Sandbox ativado
- [ ] Credenciais configuradas em `/admin/whatsapp`
- [ ] Botão "WhatsApp ATIVADO" marcado e verde
- [ ] Webhook configurado no Twilio (produção) ou túnel (localhost)
- [ ] Teste de envio realizado com sucesso
- [ ] Logs do servidor mostram mensagens sem erros

---

## 📞 SUPORTE

### Documentação Twilio
- https://www.twilio.com/docs/whatsapp
- https://support.twilio.com/

### Logs de Debug
```bash
# Ver logs Flask
tail -f logs/app.log

# Ver logs Twilio
# Acesse: https://console.twilio.com/us1/monitor/logs/debugger

# Testar webhook
curl -X POST http://localhost:5000/whatsapp/webhook \
  -d "From=whatsapp:+5585999999999" \
  -d "Body=menu"
```

---

## 🎯 RESUMO: 3 Passos para Começar

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Rodar migration
python migrations/add_whatsapp_tables.py

# 3. Configurar em /admin/whatsapp
# - Credenciais Twilio
# - Ativar WhatsApp
# - Configurar webhook
```

**Pronto! Seu bot está funcionando!** 🚀

---

## 📄 LICENÇA

Este módulo faz parte do Sistema GED EBSERH.
© 2025 EBSERH - Todos os direitos reservados.
