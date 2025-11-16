# 📱 WhatsApp Chatbot - Guia Completo

Sistema de assinatura de documentos via WhatsApp integrado ao GED EBSERH.

---

## 📋 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Configuração Inicial](#configuração-inicial)
3. [Painel Administrativo](#painel-administrativo)
4. [Como Funciona](#como-funciona)
5. [Comandos do Chatbot](#comandos-do-chatbot)
6. [Segurança](#segurança)
7. [Troubleshooting](#troubleshooting)

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

## 🚀 CONFIGURAÇÃO INICIAL

### Passo 1: Criar Conta Twilio

1. Acesse: https://www.twilio.com/try-twilio
2. Cadastre-se (conta trial gratuita)
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
cd /home/user/ged
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

### Passo 5: Configurar Webhook no Twilio

1. Acesse: https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox
2. Em **"When a message comes in"**, cole:
   ```
   https://SEU_DOMINIO.com/whatsapp/webhook
   ```
   **IMPORTANTE:** Substitua `SEU_DOMINIO.com` pelo domínio real!

3. Método: **POST**
4. Salve

### Passo 6: Testar Envio

1. No painel `/admin/whatsapp`
2. No card **"Testar Envio"**
3. Digite seu número: `+5585999999999`
4. Clique em **Enviar Teste**
5. Você receberá mensagem de teste no WhatsApp!

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

### ❌ Erro: "WhatsApp não configurado"

**Causa:** Credenciais Twilio não preenchidas ou WhatsApp desativado.

**Solução:**
1. Acesse `/admin/whatsapp`
2. Verifique se toggle **"WhatsApp ATIVADO"** está marcado
3. Preencha Account SID, Auth Token, Número
4. Salve

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

### ❌ Erro: "Fora do horário de atendimento"

**Causa:** Chatbot configurado para responder apenas em horários específicos.

**Solução:**
1. Acesse `/admin/whatsapp`
2. Vá em **"Horários de Funcionamento"**
3. Ajuste horário de início/término
4. Marque dias da semana
5. Salve

---

### ❌ Erro: "Sessão expirada"

**Causa:** Usuário ficou mais de 15 minutos sem enviar mensagem.

**Solução:**
- Digite `menu` para recomeçar
- Para aumentar timeout:
  1. `/admin/whatsapp`
  2. **"Timeout de Sessão"**
  3. Aumente para 30 ou 60 minutos

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

### Filtros Disponíveis
- Por direção
- Por status
- Por data
- Por usuário

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

4. ✅ **Personalize templates**
   - Linguagem profissional
   - Clara e objetiva
   - Tom amigável

5. ✅ **Teste regularmente**
   - Envie mensagens de teste
   - Valide webhook funcionando
   - Teste assinatura completa

### Para Usuários

1. ✅ **Mantenha telefone atualizado**
   - Informe mudanças de número
   - Ative WhatsApp no perfil

2. ✅ **Use senhas fortes**
   - Mínimo 8 caracteres
   - Não compartilhe

3. ✅ **Não compartilhe conversas**
   - Contém dados sensíveis
   - Validade jurídica

4. ✅ **Responda prontamente**
   - Sessão expira em 15 minutos
   - Verificar pendências regularmente

---

## 📞 SUPORTE

### Documentação Twilio
- https://www.twilio.com/docs/whatsapp
- https://support.twilio.com/

### Sistema GED
- Email: suporte@ged.hospital.br
- Issues: https://github.com/seu-repo/ged/issues

---

## 📝 CHANGELOG

### v1.0.0 (16/11/2025)
- ✨ Implementação inicial do chatbot
- ✅ Assinatura direto no WhatsApp
- ✅ Painel administrativo completo
- ✅ Integração com workflow UGQ
- ✅ Auditoria e logs
- ✅ Templates personalizáveis
- ✅ Segurança com hash SHA-256

---

## 📄 LICENÇA

Este módulo faz parte do Sistema GED EBSERH.
© 2025 EBSERH - Todos os direitos reservados.
