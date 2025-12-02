# 📖 Guia do Usuário - Sistema GED EBSERH

> **Sistema de Gestão Eletrônica de Documentos para Hospitais da EBSERH**
> Versão 2.0 | Atualizado em: Dezembro 2024

---

## 📋 Índice

1. [O que é o GED EBSERH?](#1-o-que-é-o-ged-ebserh)
2. [Como Acessar o Sistema](#2-como-acessar-o-sistema)
3. [Perfis de Usuário](#3-perfis-de-usuário)
4. [Dashboard Principal](#4-dashboard-principal)
5. [Gestão de Documentos](#5-gestão-de-documentos)
6. [Sistema de Tarefas](#6-sistema-de-tarefas)
7. [Workflow de Aprovação](#7-workflow-de-aprovação)
8. [Notificações](#8-notificações)
9. [WhatsApp e Assinatura Digital](#9-whatsapp-e-assinatura-digital)
10. [Busca e Filtros](#10-busca-e-filtros)
11. [Comentários e Discussões](#11-comentários-e-discussões)
12. [Relatórios e Análises](#12-relatórios-e-análises)
13. [Templates de Documentos](#13-templates-de-documentos)
14. [Perguntas Frequentes](#14-perguntas-frequentes)
15. [Dicas e Boas Práticas](#15-dicas-e-boas-práticas)

---

## 1. O que é o GED EBSERH?

O **GED EBSERH** é um sistema completo de gestão eletrônica de documentos desenvolvido especialmente para hospitais da rede EBSERH. Ele permite:

### 🎯 Principais Objetivos

- **Centralizar** todos os documentos institucionais (POPs, Manuais, Protocolos, Políticas, etc.)
- **Padronizar** o processo de criação e aprovação de documentos
- **Controlar** versões, validades e fluxos de trabalho
- **Facilitar** a busca e consulta de documentos
- **Garantir** rastreabilidade e conformidade normativa

### ✨ Diferenciais

- ✅ **Inteligência Artificial**: Análise automática de documentos
- ✅ **WhatsApp**: Notificações e aprovações direto no celular
- ✅ **Workflow UGQ**: Processo centralizado pela Unidade de Gestão da Qualidade
- ✅ **Assinatura Digital**: Registros auditáveis e seguros
- ✅ **Versionamento**: Controle completo de alterações

---

## 2. Como Acessar o Sistema

### 🌐 Acesso Web

1. Abra seu navegador (Chrome, Firefox, Edge ou Safari)
2. Digite o endereço: `http://[servidor-hospital]:5000`
3. Faça login com seu email e senha
4. Pronto! Você está no sistema

### 📱 Acesso via WhatsApp

Se seu hospital habilitou o WhatsApp:

1. Certifique-se de ter cadastrado seu número no sistema
2. Aguarde a mensagem de boas-vindas
3. Digite **"menu"** para ver suas tarefas pendentes
4. Siga as instruções interativas

> **💡 Dica:** Salve o número do GED nos seus contatos!

### 🔑 Primeiro Acesso

No primeiro acesso, você receberá:
- Email com credenciais temporárias
- Solicitação para alterar a senha
- Tutorial rápido do sistema

---

## 3. Perfis de Usuário

O sistema possui **6 perfis** diferentes, cada um com permissões específicas:

### 👤 1. Usuário Comum

**O que você pode fazer:**
- ✅ Criar novos documentos
- ✅ Fazer upload de arquivos
- ✅ Visualizar seus documentos
- ✅ Executar tarefas atribuídas a você
- ✅ Comentar em documentos
- ✅ Receber notificações

**Limitações:**
- ❌ Não pode aprovar documentos de outros
- ❌ Não pode gerenciar usuários
- ❌ Não pode alterar configurações

---

### 👨‍💼 2. Gerente de Setor

**Tudo que o Usuário Comum faz, MAIS:**
- ✅ Visualizar todos os documentos do setor
- ✅ Atribuir tarefas para sua equipe
- ✅ Aprovar documentos criados no seu setor
- ✅ Acessar relatórios gerenciais do setor
- ✅ Usar recursos de IA para análise de documentos

**Responsabilidades:**
- 📊 Monitorar prazos de documentos
- 👥 Designar responsáveis para tarefas
- ✅ Garantir qualidade das entregas

---

### 🔬 3. Triador UGQ

**Perfil especial da Unidade de Gestão da Qualidade**

**O que você faz:**
- ✅ Recebe documentos novos enviados pelos setores
- ✅ Realiza triagem inicial (3 checkpoints):
  - ✔️ **Checkpoint 1:** Formatação e padronização EBSERH
  - ✔️ **Checkpoint 2:** Completude das informações
  - ✔️ **Checkpoint 3:** Adequação técnica
- ✅ Aprova para próxima etapa OU devolve para correções
- ✅ Adiciona observações e orientações

**Fluxo típico:**
```
Documento Novo → Triador UGQ analisa →
   ↓ (se OK)                ↓ (se precisa correções)
Segue p/ Validação     Volta p/ Autor corrigir
```

---

### 🎯 4. Validador UGQ

**Perfil sênior da Qualidade - maior responsabilidade**

**O que você faz:**
- ✅ Valida tecnicamente documentos triados
- ✅ **Gera código definitivo** (ex: POP-DEF-20241202-0001)
- ✅ Monta **Bloco de Assinatura** com aprovadores
- ✅ Define modo de aprovação:
  - **Sequencial:** Um por vez, em ordem
  - **Concomitante:** Todos ao mesmo tempo
- ✅ Acompanha aprovações
- ✅ **Publica o documento** final após todas as assinaturas
- ✅ Atualiza Lista Mestra

**Responsabilidades críticas:**
- 📝 Codificação correta dos documentos
- 👥 Seleção adequada de aprovadores
- ✅ Garantia de conformidade normativa
- 📋 Manutenção da Lista Mestra

---

### 🏢 5. Responsável Interno

**Perfil para responsáveis de áreas/processos específicos**

**O que você faz:**
- ✅ Gerencia documentos de processos sob sua responsabilidade
- ✅ Aprova documentos relacionados à sua área
- ✅ Monitora validades e atualizações necessárias
- ✅ Solicita revisões e novas versões

**Exemplo de uso:**
- Responsável Técnico de UTI
- Coordenador de Farmácia
- Chefe de CCIH

---

### 👑 6. Administrador

**Controle total do sistema**

**O que você faz:**
- ✅ **Gerenciar usuários**: Criar, editar, desativar
- ✅ **Configurar sistema**: Setores, tipos de documento, abrangências
- ✅ **Visualizar tudo**: Acesso a todos os documentos
- ✅ **Acessar logs**: Auditoria completa
- ✅ **Configurar integrações**: WhatsApp, IA, email
- ✅ **Gerar backups**

**Acessos exclusivos:**
- ⚙️ Painel administrativo
- 📊 Dashboard executivo
- 🔧 Configurações globais
- 📈 Relatórios avançados

---

## 4. Dashboard Principal

Ao fazer login, você verá o **Dashboard Principal** - sua central de controle:

### 📊 Visão Geral

O dashboard mostra informações personalizadas de acordo com seu perfil:

#### Para Usuários Comuns:
```
┌─────────────────────────────────────┐
│  Bem-vindo, João Silva!             │
│  Setor: Enfermagem                  │
├─────────────────────────────────────┤
│  📋 Minhas Tarefas (3)              │
│  ⏰ Tarefas Atrasadas (0)           │
│  📄 Meus Documentos (12)            │
│  🔔 Notificações (2)                │
└─────────────────────────────────────┘
```

#### Para Gerentes:
```
┌─────────────────────────────────────┐
│  Dashboard - Gerência               │
├─────────────────────────────────────┤
│  📊 Estatísticas do Setor           │
│  • Documentos: 45 (3 vencendo)      │
│  • Tarefas Ativas: 12               │
│  • Taxa de Conclusão: 87%           │
│                                     │
│  📋 Minha Equipe                    │
│  • Maria Silva: 2 tarefas           │
│  • Pedro Santos: 1 tarefa atrasada  │
│                                     │
│  📈 Gráficos e Relatórios           │
└─────────────────────────────────────┘
```

#### Para Triador/Validador UGQ:
```
┌─────────────────────────────────────┐
│  Fila da Qualidade                  │
├─────────────────────────────────────┤
│  📥 Em Triagem (8)                  │
│  ✓ Aguardando Validação (5)         │
│  📝 Em Bloco de Assinatura (12)     │
│  ⏰ Documentos Urgentes (2)         │
│                                     │
│  🎯 Ações Rápidas                   │
│  • Próximo documento da fila        │
│  • Publicar aprovados               │
└─────────────────────────────────────┘
```

### 🎯 Ações Rápidas

No topo do dashboard, você sempre tem acesso a:

- 🆕 **Novo Documento**: Criar documento rapidamente
- 📋 **Minhas Tarefas**: Lista completa de tarefas
- 🔍 **Busca Avançada**: Pesquisar documentos
- 🔔 **Notificações**: Ver todas as notificações
- 👤 **Meu Perfil**: Alterar dados e senha

---

## 5. Gestão de Documentos

### 📤 Criando um Novo Documento

#### Passo a Passo:

**1. Acesse "Novo Documento"**
- Clique no botão azul "+ Novo Documento"
- Ou use o menu: `Documentos → Criar Novo`

**2. Preencha as Informações Básicas**

```
┌─────────────────────────────────────────┐
│  Título do Documento *                  │
│  [________________________________]     │
│                                         │
│  Tipo de Documento *                    │
│  [ Selecione ▼ ]                       │
│  • POP - Procedimento Operacional      │
│  • Manual                              │
│  • Protocolo                           │
│  • Política                            │
│  • Regimento                           │
│  • Regulamento                         │
│                                         │
│  Setor *                                │
│  [ Seu Setor ▼ ]                       │
│                                         │
│  Abrangência *                          │
│  [ ] CHUFC                             │
│  [ ] HUWC                              │
│  [ ] MEAC                              │
│  [ ] Complexo (todos)                  │
│                                         │
│  Descrição                              │
│  [________________________________]     │
│  [________________________________]     │
└─────────────────────────────────────────┘
```

**3. Faça Upload do Arquivo**

Formatos aceitos:
- ✅ PDF (.pdf)
- ✅ Word (.doc, .docx)
- ✅ LibreOffice (.odt)

Tamanho máximo: **50MB**

> **⚠️ Importante:** Certifique-se de que o documento está no formato correto da EBSERH antes de enviar!

**4. Aguarde o Processamento da IA**

O sistema automaticamente:
- 🤖 Extrai o texto do documento
- 🏷️ Identifica o tipo e categorias
- 📊 Gera metadados
- 💡 Sugere responsável técnico
- 📝 Cria um resumo

> **⏱️ Tempo médio:** 10-30 segundos

**5. Revise e Confirme**

- Confira as informações extraídas pela IA
- Ajuste se necessário
- Clique em **"Enviar para Triagem"**

**6. Acompanhe o Status**

Seu documento receberá:
- ✅ **Código Único** (permanente): `DOC-20241202-143052-001`
- ✅ **Código Provisório**: `POP-PROV-20241202143052`
- ✅ Status inicial: **"Em Triagem"**

---

### 📋 Tipos de Documento

| Tipo | Sigla | Validade | Descrição |
|------|-------|----------|-----------|
| **POP** | Procedimento Operacional Padrão | 2 anos | Instruções detalhadas de procedimentos |
| **Manual** | MAN | 2 anos | Guia completo de processos |
| **Protocolo** | PROT | 2 anos | Diretrizes clínicas/assistenciais |
| **Política** | POL | 4 anos | Diretrizes institucionais amplas |
| **Regimento** | REG | 4 anos | Normas de funcionamento |
| **Regulamento** | REGUL | 4 anos | Conjunto de regras institucionais |

---

### 🔄 Versionamento de Documentos

Quando um documento publicado precisa ser atualizado:

#### Criando uma Nova Versão:

**1. Acesse o documento publicado**
- Vá em `Meus Documentos` ou use a busca
- Abra o documento

**2. Clique em "Nova Versão"**

**3. O sistema automaticamente:**
- ✅ Copia todas as informações do documento atual
- ✅ Mantém o código definitivo
- ✅ Incrementa a versão (v1.0 → v2.0)
- ✅ Vincula à versão anterior

**4. Faça as alterações necessárias**
- Upload do novo arquivo
- Atualização de informações

**5. Submeta para triagem novamente**

**Histórico de Versões:**
```
v1.0 - 01/01/2024 - Versão original (OBSOLETA)
v2.0 - 15/06/2024 - Atualização de procedimentos (ATIVA)
v3.0 - 02/12/2024 - Revisão completa (EM APROVAÇÃO)
```

---

### 📊 Códigos dos Documentos

Entenda os 3 tipos de códigos:

#### 1️⃣ Código Único (permanente)
```
DOC-20241202-143052-001
│    │        │       │
│    │        │       └─ Sequencial aleatório
│    │        └───────── Hora (14:30:52)
│    └────────────────── Data (2024-12-02)
└─────────────────────── Prefixo fixo
```
**Uso:** Identificação interna permanente

#### 2️⃣ Código Provisório
```
POP-PROV-20241202143052
│    │     │
│    │     └─────────────── Timestamp
│    └───────────────────── Indica provisório
└────────────────────────── Tipo do documento
```
**Uso:** Enquanto documento não está aprovado

#### 3️⃣ Código Definitivo (gerado pela UGQ)
```
POP-DEF-20241202-0001
│    │    │        │
│    │    │        └────── Sequencial do dia
│    │    └─────────────── Data de publicação
│    └──────────────────── Indica definitivo
└───────────────────────── Tipo do documento
```
**Uso:** Código oficial após publicação

> **💡 Dica:** Ao buscar documentos, prefira usar o código definitivo!

---

### 🗑️ Exclusão de Documentos (Soft Delete)

O sistema usa **exclusão suave** (soft delete):

**O que isso significa?**
- Documentos "deletados" não são removidos do banco
- Eles são marcados como deletados
- É possível recuperá-los depois

**Como deletar:**
1. Abra o documento
2. Clique em `⋮ Mais opções`
3. Selecione **"Excluir Documento"**
4. Confirme a ação

**Como recuperar:**
1. Administradores acessam: `Documentos → Lixeira`
2. Selecionam o documento
3. Clicam em **"Restaurar"**

> **🔒 Segurança:** Todas as exclusões e restaurações são registradas em log.

---

## 6. Sistema de Tarefas

### 📋 O que são Tarefas?

Tarefas são **atividades atribuídas a você** relacionadas a documentos. Tipos comuns:

| Tipo | Descrição | Quem recebe |
|------|-----------|-------------|
| **Analisar** | Revisar e dar parecer | Gerentes |
| **Validar Conteúdo** | Validação técnica | Especialistas |
| **Aprovar** | Aprovação final | Bloco de assinatura |
| **Realizar Correção** | Corrigir problemas identificados | Autor do documento |
| **Publicar** | Publicação oficial | Validador UGQ |

---

### ✅ Executando uma Tarefa

#### Passo a Passo:

**1. Acesse "Minhas Tarefas"**
- Dashboard → "Minhas Tarefas"
- Ou clique no ícone 📋 no menu

**2. Selecione a tarefa**
```
┌────────────────────────────────────────────┐
│ 📄 Aprovar e assinar documento             │
│ POP-DEF-20241202-0001                      │
│ Manual de Procedimentos da UTI             │
│                                            │
│ 👤 Solicitado por: Maria Silva (Validador) │
│ ⏰ Prazo: 05/12/2024 17:00                 │
│ ⚠️ Prioridade: Alta                        │
│                                            │
│ [Ver Documento] [Executar Tarefa]         │
└────────────────────────────────────────────┘
```

**3. Visualize o documento**
- Leia com atenção
- Verifique todos os detalhes
- Consulte anexos se houver

**4. Tome uma decisão**

Para tarefas de aprovação:
```
┌────────────────────────────────────────┐
│  Sua Decisão:                          │
│  ( ) ✅ Aprovar                        │
│  ( ) ❌ Reprovar (solicitar correções) │
│                                        │
│  Parecer/Justificativa: *              │
│  [_______________________________]     │
│  [_______________________________]     │
│                                        │
│  🔒 Senha para assinatura digital: *   │
│  [______________]                      │
│                                        │
│  [Confirmar Assinatura]                │
└────────────────────────────────────────┘
```

**5. Confirme com sua senha**
- Digite sua senha de login
- Isso gera uma **assinatura digital** com:
  - Hash SHA-256
  - Timestamp exato
  - Seu IP e navegador
  - Registro auditável

**6. Pronto!**
- Tarefa marcada como concluída
- Documento avança no fluxo
- Próximo responsável é notificado

---

### ⏰ Prazos e Alertas

**Visualização de prazos:**
```
🟢 5 dias ou mais: Verde (tranquilo)
🟡 2-4 dias: Amarelo (atenção)
🔴 1 dia ou menos: Vermelho (urgente)
⚫ Atrasada: Cinza escuro (crítico!)
```

**Notificações automáticas:**
- 📧 Email quando tarefa é atribuída
- 📱 WhatsApp (se habilitado)
- 🔔 Notificação in-app
- ⏰ Lembretes 24h antes do prazo
- ⚠️ Alerta quando atrasa

---

## 7. Workflow de Aprovação

### 🔄 Fluxo Completo do Documento

```
┌──────────────────────────────────────────────────────────┐
│                    FLUXO GED EBSERH                      │
└──────────────────────────────────────────────────────────┘

1️⃣ CRIAÇÃO
   👤 Autor cria documento → Upload de arquivo
   ↓
   🤖 IA processa automaticamente
   ↓
   📤 Enviado para UGQ
   Status: "Novo" → "Em Triagem"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2️⃣ TRIAGEM UGQ (3 Checkpoints)
   🔬 Triador analisa:

   ✓ Checkpoint 1: Formatação EBSERH
   ✓ Checkpoint 2: Completude das informações
   ✓ Checkpoint 3: Adequação técnica

   Decisão:
   • ✅ Aprovado → Segue para Validação
   • ❌ Reprovado → Volta para Autor corrigir

   Status: "Em Triagem" → "Em Validação" (ou "Em Correção")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3️⃣ VALIDAÇÃO UGQ
   🎯 Validador:

   • Valida tecnicamente o conteúdo
   • Gera código definitivo (ex: POP-DEF-20241202-0001)
   • Monta Bloco de Assinatura:
     - Seleciona aprovadores
     - Define ordem (sequencial/concomitante)
     - Envia notificações

   Status: "Em Validação" → "Validado" → "Em Aprovação"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4️⃣ BLOCO DE ASSINATURA

   Modo Sequencial:
   👤 Aprovador 1 → ✅ Assina → Notifica Aprovador 2
   👤 Aprovador 2 → ✅ Assina → Notifica Aprovador 3
   👤 Aprovador 3 → ✅ Assina → Completo!

   Modo Concomitante:
   👤 Aprovadores 1, 2 e 3 → ✅ Assinam em paralelo
   ✓ Todos assinaram → Completo!

   Se alguém reprovar:
   ❌ → Volta para "Em Ajustes" → Autor corrige

   Status: "Em Aprovação" → "Aprovado" (ou "Em Ajustes")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5️⃣ PUBLICAÇÃO
   🎯 Validador UGQ:

   • Gera PDF final codificado
   • Adiciona à Lista Mestra
   • Define data de vencimento (2 ou 4 anos)
   • Publica oficialmente
   • Notifica todos os envolvidos

   Status: "Aprovado" → "Publicado" ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 RESULTADO FINAL

• Documento disponível no Repositório Público
• Código definitivo ativo
• Controle automático de validade
• Histórico completo de aprovações
• Assinaturas digitais registradas
```

---

### 🔀 Situações Especiais

#### Documento Reprovado na Triagem

```
Triador identifica problema
↓
❌ Reprova com justificativa
↓
📧 Autor recebe notificação
↓
👤 Autor corrige o documento
↓
📤 Reenvia para triagem
↓
🔄 Processo recomeça
```

**Motivos comuns de reprovação:**
- Formatação fora do padrão EBSERH
- Informações incompletas
- Qualidade do conteúdo insatisfatória
- Falta de referências/fundamentação

---

#### Documento Reprovado no Bloco de Assinatura

```
Aprovador identifica erro crítico
↓
❌ Reprova com parecer detalhado
↓
⚠️ Bloco é CANCELADO automaticamente
↓
📧 Todos são notificados (autor, validador, outros aprovadores)
↓
Status: "Em Ajustes"
↓
Decisão do Validador:
• Pequena correção → Autor corrige e reenviar
• Grande alteração → Volta para Triagem
```

---

## 8. Notificações

### 🔔 Tipos de Notificação

O sistema envia notificações por **3 canais**:

#### 1️⃣ In-App (dentro do sistema)
- Ícone 🔔 no topo da tela
- Contador de não lidas
- Lista em tempo real

#### 2️⃣ Email
- Enviado para seu email cadastrado
- Inclui link direto para a ação
- Contém todos os detalhes

#### 3️⃣ WhatsApp (se habilitado)
- Mensagem instantânea
- Você pode RESPONDER e ASSINAR direto
- Menu interativo

---

### 📬 Eventos que Geram Notificações

| Evento | O que você recebe |
|--------|-------------------|
| **Tarefa atribuída** | "Você tem uma nova tarefa: Aprovar documento XYZ" |
| **Documento aprovado** | "Seu documento [código] foi aprovado!" |
| **Documento reprovado** | "Seu documento precisa de correções: [motivo]" |
| **Prazo próximo** | "Tarefa vence em 24h: [descrição]" |
| **Documento vencendo** | "Documento [código] vence em 30 dias" |
| **Documento vencido** | "Documento [código] venceu! Atualize urgente" |
| **Menção em comentário** | "@você foi mencionado em [documento]" |
| **Processamento IA concluído** | "IA terminou de analisar [documento]" |

---

### ⚙️ Configurar Preferências

**Acesse:** `Meu Perfil → Notificações`

```
┌─────────────────────────────────────────┐
│  Preferências de Notificações          │
├─────────────────────────────────────────┤
│  Receber notificações por:             │
│  ☑ Email                               │
│  ☑ WhatsApp                            │
│  ☑ In-App (sempre ativo)               │
│                                         │
│  Notificar sobre:                       │
│  ☑ Tarefas atribuídas                  │
│  ☑ Prazos próximos (24h antes)         │
│  ☑ Documentos vencendo (30 dias)       │
│  ☑ Menções em comentários              │
│  ☐ Atualizações do sistema             │
│                                         │
│  Horário de notificações WhatsApp:      │
│  [08:00] até [18:00]                   │
│  ☑ Somente dias úteis                  │
│                                         │
│  [Salvar Preferências]                 │
└─────────────────────────────────────────┘
```

---

## 9. WhatsApp e Assinatura Digital

### 📱 Como Funciona

O GED EBSERH integra com WhatsApp via **Evolution API**, permitindo:

- ✅ Receber notificações instantâneas
- ✅ Ver tarefas pendentes
- ✅ Aprovar documentos
- ✅ Assinar digitalmente
- ✅ Tudo sem sair do WhatsApp!

---

### 🔐 Assinando via WhatsApp

#### Exemplo de Conversa:

```
📱 Sistema GED EBSERH

👋 Olá, Dr. João Silva!

📋 Você tem 2 documentos pendentes de aprovação:

1️⃣ POP-DEF-20241202-0001
   Manual de Procedimentos da UTI
   ⏰ Prazo: Hoje, 17:00

2️⃣ PROT-DEF-20241201-0015
   Protocolo de Sepse
   ⏰ Prazo: 05/12/2024

💬 Digite o número do documento para ver detalhes:
```

**Você digita:** `1`

```
📄 POP-DEF-20241202-0001
Manual de Procedimentos da UTI

👤 Autor: Maria Silva (Enfermagem)
📅 Criado em: 28/11/2024
⏰ Prazo para assinar: Hoje, 17:00
🔗 Ver documento: [link]

💬 O que deseja fazer?

1️⃣ - Aprovar e assinar
2️⃣ - Reprovar (solicitar correções)
3️⃣ - Ver documento completo
4️⃣ - Voltar ao menu
```

**Você digita:** `1`

```
✅ Você selecionou: Aprovar e assinar

📝 Digite seu parecer ou comentário:
(ou digite "ok" para aprovar sem comentário)
```

**Você digita:** `Documento bem elaborado, aprovado.`

```
🔒 Para confirmar sua assinatura digital, digite sua SENHA:

⚠️ Atenção:
• Esta mensagem será apagada automaticamente
• Use a mesma senha do sistema web
• Sua assinatura terá validade jurídica
```

**Você digita:** `sua_senha_aqui`

```
✅ ASSINATURA REGISTRADA COM SUCESSO!

📋 POP-DEF-20241202-0001
   Manual de Procedimentos da UTI

⏰ Data/Hora: 02/12/2024 14:35:27
👤 Assinado por: Dr. João Silva
💬 Parecer: "Documento bem elaborado, aprovado."
🔐 Hash: 8a7f9d2e1b... (SHA-256)

📧 Comprovante enviado para seu email!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Você ainda tem 1 documento pendente.
Digite "menu" para ver.
```

> **🔒 Segurança:** A mensagem com sua senha é deletada automaticamente em 2 segundos!

---

### ⚠️ Segurança no WhatsApp

**Medidas de proteção:**

1. ✅ **Autenticação obrigatória:** Sempre pede senha
2. ✅ **Deleção automática:** Mensagens sensíveis são apagadas
3. ✅ **Timeout de sessão:** Conversa expira após 15 minutos inativa
4. ✅ **Bloqueio por tentativas:** 3 senhas erradas = bloqueio temporário de 30min
5. ✅ **Assinatura auditável:** Registra IP, hora, hash, parecer
6. ✅ **Horário de funcionamento:** Funciona apenas em horário configurado
7. ✅ **Número cadastrado:** Só funciona com números autorizados

**Comandos úteis:**
- `menu` - Ver tarefas pendentes
- `docs` - Ver documentos recentes
- `ajuda` - Ver comandos disponíveis
- `sair` - Encerrar sessão

---

## 10. Busca e Filtros

### 🔍 Busca Avançada

Acesse: `Menu → Buscar Documentos`

#### Filtros Disponíveis:

```
┌──────────────────────────────────────────────┐
│  🔍 Busca Avançada de Documentos             │
├──────────────────────────────────────────────┤
│  Texto Livre:                                │
│  [________________________________]          │
│  (busca em título, código, descrição)        │
│                                              │
│  Tipo de Documento:                          │
│  [ ] POP  [ ] Manual  [ ] Protocolo         │
│  [ ] Política  [ ] Regimento                │
│                                              │
│  Status:                                     │
│  [ ] Publicado  [ ] Em Aprovação            │
│  [ ] Em Triagem  [ ] Novo                   │
│                                              │
│  Setor:                                      │
│  [Todos ▼]                                  │
│                                              │
│  Abrangência:                                │
│  [ ] CHUFC  [ ] HUWC  [ ] MEAC              │
│                                              │
│  Período:                                    │
│  De: [__/__/____] Até: [__/__/____]         │
│                                              │
│  Autor:                                      │
│  [Selecione ▼]                              │
│                                              │
│  Vencimento:                                 │
│  ( ) Todos                                  │
│  ( ) Vence em 30 dias                       │
│  ( ) Vence em 60 dias                       │
│  ( ) Já vencidos                            │
│                                              │
│  [🔍 Buscar]  [🗑️ Limpar Filtros]           │
└──────────────────────────────────────────────┘
```

---

### 💡 Dicas de Busca

**Busca por código:**
```
✅ POP-DEF-20241202-0001     → Encontra exatamente
✅ POP-DEF-20241202          → Encontra todos do dia
✅ POP-DEF                   → Encontra todos os POPs definitivos
```

**Busca por texto:**
```
✅ "manual uti"              → Manual + UTI
✅ procedimento lavagem      → Procedimento E lavagem
✅ protocolo sepse           → Protocolo de sepse
```

**Operadores especiais:**
```
✅ titulo:manual             → Busca só no título
✅ autor:"Maria Silva"       → Documentos da Maria
✅ setor:enfermagem          → Setor específico
```

---

### 📊 Resultados da Busca

```
┌────────────────────────────────────────────────┐
│  Encontrados: 15 documentos                    │
│  Ordenar por: [Mais recentes ▼]               │
├────────────────────────────────────────────────┤
│  📄 POP-DEF-20241202-0001                      │
│  Manual de Procedimentos da UTI                │
│  👤 Maria Silva | 📅 02/12/2024 | ✅ Publicado│
│  [Ver] [Download PDF]                          │
├────────────────────────────────────────────────┤
│  📄 POP-DEF-20241201-0008                      │
│  Protocolo de Higienização Hospitalar         │
│  👤 João Santos | 📅 01/12/2024 | 🟡 Aprovação│
│  [Ver]                                         │
├────────────────────────────────────────────────┤
│  ...                                           │
└────────────────────────────────────────────────┘
```

**Opções de visualização:**
- 📄 Lista (padrão)
- 🎴 Cards
- 📋 Tabela

**Ordenação:**
- Mais recentes
- Mais antigos
- Alfabética (A-Z)
- Prioridade
- Vencimento próximo

---

## 11. Comentários e Discussões

### 💬 Sistema de Comentários

Cada documento tem uma **área de discussão** onde você pode:

- ✅ Adicionar comentários
- ✅ Responder comentários (threads)
- ✅ Mencionar outros usuários (@email)
- ✅ Editar seus comentários
- ✅ Deletar seus comentários

---

### ✍️ Adicionando um Comentário

**1. Abra o documento**

**2. Role até "Comentários e Discussões"**

```
┌──────────────────────────────────────────────┐
│  💬 Comentários (3)                          │
├──────────────────────────────────────────────┤
│  ✍️ Adicionar comentário:                    │
│  [____________________________________]      │
│  [____________________________________]      │
│  [____________________________________]      │
│                                              │
│  💡 Dica: Use @email para mencionar alguém  │
│                                              │
│  [Comentar]  [Cancelar]                     │
└──────────────────────────────────────────────┘
```

**3. Digite seu comentário**

Exemplo:
```
@maria.silva@hospital.com, poderia revisar a seção 3.2?
Acredito que o prazo está incorreto.
```

**4. Publique**

**Resultado:**
- ✅ Comentário aparece na discussão
- ✅ Maria recebe notificação
- ✅ Todos os envolvidos podem ver

---

### 🗣️ Menções e Notificações

Quando você é mencionado:

```
🔔 Notificação

💬 Você foi mencionado em um comentário

📄 POP-DEF-20241202-0001
   Manual de Procedimentos da UTI

👤 João Silva comentou:
"@voce@hospital.com, poderia revisar a seção 3.2?"

[Ver Comentário]
```

---

### 🧵 Threads (Respostas)

Você pode responder comentários específicos:

```
┌──────────────────────────────────────────────┐
│  João Silva - 02/12/2024 14:30              │
│  Encontrei um erro na página 5.              │
│                                              │
│  [Responder] [↓ 2 respostas]                │
│                                              │
│    └─ Maria Silva - 02/12/2024 14:45        │
│       Já corrigi! Obrigada por avisar.      │
│                                              │
│       [Responder]                            │
│                                              │
│         └─ João Silva - 02/12/2024 15:00    │
│            Perfeito! ✅                      │
└──────────────────────────────────────────────┘
```

---

## 12. Relatórios e Análises

### 📊 Tipos de Relatórios

Dependendo do seu perfil, você tem acesso a diferentes relatórios:

#### Para Todos os Usuários:

**1. Meus Documentos**
- Lista de todos os documentos que você criou
- Status de cada um
- Opções de exportação

**2. Minhas Tarefas**
- Tarefas concluídas e pendentes
- Taxa de conclusão
- Tempo médio de resposta

---

#### Para Gerentes:

**3. Relatório do Setor**
```
📊 RELATÓRIO DO SETOR - ENFERMAGEM
Período: 01/11/2024 a 02/12/2024

📄 Documentos:
• Total: 45
• Publicados: 38 (84%)
• Em andamento: 5 (11%)
• Aguardando: 2 (5%)

📋 Tarefas:
• Concluídas: 127
• Pendentes: 8
• Atrasadas: 1 (⚠️)
• Taxa de conclusão: 94%

📅 Vencimentos:
• Vencendo em 30 dias: 3 documentos
• Vencendo em 60 dias: 7 documentos
• Vencidos: 0 ✅

👥 Equipe:
• Mais produtivo: Maria Silva (12 tarefas)
• Com atraso: Pedro Santos (1 tarefa)

[Exportar PDF] [Exportar Excel]
```

**4. Tarefas Atrasadas**
- Lista de todas as tarefas em atraso do setor
- Responsáveis
- Ações recomendadas

**5. Documentos Vencendo**
- Alerta de documentos próximos ao vencimento
- Priorização automática
- Sugestão de responsáveis para revisão

---

#### Para Administradores:

**6. Dashboard Executivo**
```
📊 DASHBOARD EXECUTIVO
Complexo Hospitalar EBSERH

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 DOCUMENTOS
┌─────────────────────────────────┐
│ Total no sistema: 523           │
│ Publicados: 487 (93%)           │
│ Em andamento: 36 (7%)           │
└─────────────────────────────────┘

Por Abrangência:
• CHUFC: 245 (47%)
• HUWC: 189 (36%)
• MEAC: 89 (17%)

Por Tipo:
• POP: 312 (60%)
• Manual: 97 (18%)
• Protocolo: 78 (15%)
• Política: 36 (7%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 TAREFAS
┌─────────────────────────────────┐
│ Ativas: 156                     │
│ Taxa de conclusão: 91% ✅       │
│ Tempo médio: 2,3 dias           │
└─────────────────────────────────┘

⚠️ Alertas:
• Tarefas atrasadas: 7 (4%)
• Documentos vencendo: 23
• Documentos vencidos: 3 (!)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 USUÁRIOS
• Total de usuários: 89
• Ativos hoje: 67
• Média de acessos: 234/dia

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 TENDÊNCIAS (vs. mês anterior)
• Documentos publicados: ↑ 12%
• Taxa de aprovação: ↑ 5%
• Tempo de triagem: ↓ 15% ✅
• Uso de IA: ↑ 34%

[Exportar Relatório Completo]
```

**7. Auditoria e Logs**
- Registro completo de ações
- Filtragem por usuário, data, tipo
- Exportação para compliance

**8. Relatório de IA**
- Estatísticas de uso da IA
- Acurácia das análises
- Tempo de processamento

---

### 📥 Exportando Relatórios

Formatos disponíveis:
- 📄 **PDF**: Formatado, pronto para impressão
- 📊 **Excel**: Dados para análise
- 📋 **CSV**: Dados brutos
- 📧 **Email**: Envio automático agendado

---

## 13. Templates de Documentos

### 📝 O que são Templates?

Templates são **modelos pré-aprovados** de documentos que facilitam a criação seguindo o padrão EBSERH.

**Vantagens:**
- ✅ Formatação correta garantida
- ✅ Seções obrigatórias já incluídas
- ✅ Acelera a criação
- ✅ Reduz erros

---

### 🆕 Usando um Template

**1. Acesse "Novo Documento"**

**2. Clique em "Usar Template"**

```
┌──────────────────────────────────────────┐
│  📚 Templates Disponíveis                │
├──────────────────────────────────────────┤
│  🔍 Filtrar: [____________] 🔍          │
│                                          │
│  📋 POP - Modelo Geral                   │
│  Procedimento Operacional Padrão         │
│  Usado 45 vezes                          │
│  [Usar Template]                         │
├──────────────────────────────────────────┤
│  📘 Manual - Modelo EBSERH               │
│  Manual institucional completo           │
│  Usado 12 vezes                          │
│  [Usar Template]                         │
├──────────────────────────────────────────┤
│  🏥 Protocolo Assistencial              │
│  Protocolo clínico padrão                │
│  Usado 28 vezes                          │
│  [Usar Template]                         │
└──────────────────────────────────────────┘
```

**3. Preencha os campos**

O template já vem com:
- ✅ Formatação EBSERH
- ✅ Cabeçalho e rodapé
- ✅ Seções estruturadas
- ✅ Campos para preencher

**4. Faça download, edite e faça upload**

---

### 👨‍💼 Para Administradores: Criando Templates

**Acesse:** `Administração → Templates`

**Passo a passo:**

1. Clique em "Novo Template"
2. Preencha:
   - Nome do template
   - Descrição
   - Tipo de documento
   - Setor (ou deixe para todos)
3. Faça upload do arquivo modelo (.docx ou .odt)
4. Defina campos variáveis
5. Salve

**Campos variáveis disponíveis:**
```
{{NOME_PROCEDIMENTO}}
{{SETOR}}
{{RESPONSAVEL}}
{{DATA_CRIACAO}}
{{VERSAO}}
{{ABRANGENCIA}}
```

---

## 14. Perguntas Frequentes

### ❓ FAQ - Usuários

**Q: Esqueci minha senha. Como recupero?**
A: Na tela de login, clique em "Esqueci minha senha". Digite seu email e siga as instruções.

---

**Q: Posso editar um documento após enviar?**
A: Depende:
- ✅ Se está em "Novo" ou "Em Análise": Sim, você pode
- ❌ Se já passou para triagem: Não, a menos que seja devolvido para correção
- ✅ Se você receber tarefa de "Realizar Correção": Sim

---

**Q: Como sei se meu documento foi aprovado?**
A: Você receberá notificação por:
- 📧 Email
- 📱 WhatsApp (se configurado)
- 🔔 Notificação in-app

Além disso, o status no sistema mudará para "Aprovado" ou "Publicado".

---

**Q: Quanto tempo demora o processamento da IA?**
A: Em média 10-30 segundos, dependendo do tamanho do arquivo.

---

**Q: Posso deletar um documento publicado?**
A: Não diretamente. Documentos publicados só podem ser:
- Marcados como "Obsoletos" (quando há nova versão)
- "Cancelados" (por administrador, com justificativa)

---

**Q: Minha tarefa está atrasada. E agora?**
A:
1. Execute o mais rápido possível
2. Se não conseguir, comunique seu gerente
3. Se bloqueado, justifique no sistema
4. Gerentes podem estender prazos em casos especiais

---

**Q: Posso assinar via WhatsApp mesmo sem estar no computador?**
A: Sim! Basta ter o WhatsApp e sua senha do sistema.

---

### ❓ FAQ - Gerentes

**Q: Como atribuo uma tarefa para minha equipe?**
A:
1. Abra o documento
2. Clique em "Atribuir Tarefa"
3. Selecione o tipo de tarefa
4. Escolha o responsável
5. Defina prazo e prioridade
6. Clique em "Criar Tarefa"

---

**Q: Posso ver tarefas de todo o meu setor?**
A: Sim! Acesse `Dashboard → Visão do Setor`.

---

**Q: Como gero um relatório do meu setor?**
A: `Relatórios → Relatório do Setor → Selecionar Período → Gerar`.

---

### ❓ FAQ - UGQ (Triadores/Validadores)

**Q: Qual a diferença entre código provisório e definitivo?**
A:
- **Provisório**: Gerado automaticamente na criação (ex: POP-PROV-20241202143052)
- **Definitivo**: Gerado pelo Validador UGQ após aprovação (ex: POP-DEF-20241202-0001)

O definitivo é o código oficial que vai para a Lista Mestra.

---

**Q: Como monto um bloco de assinatura sequencial?**
A:
1. Acesse o documento validado
2. Clique em "Montar Bloco de Assinatura"
3. Selecione "Sequencial"
4. Adicione aprovadores **na ordem desejada**
5. Importante: Ordem 1 assina primeiro, depois 2, depois 3, etc.
6. Confirme

---

**Q: E se um aprovador está de férias?**
A: Você tem 3 opções:
1. Substituir por outro aprovador (antes de enviar)
2. Aguardar o retorno (se não for urgente)
3. Remontar o bloco (se já foi enviado)

---

**Q: Posso publicar antes de todas as assinaturas?**
A: Não. O sistema só permite publicar após **todas** as aprovações do bloco.

---

**Q: Como adiciono um documento à Lista Mestra?**
A: É automático! Quando você publica, o sistema adiciona automaticamente com:
- Código definitivo
- Data de publicação
- Validade calculada
- Status "EM_APROVACAO" → "PUBLICADO"

---

## 15. Dicas e Boas Práticas

### ✅ Criação de Documentos

**DO (Faça):**
- ✅ Use templates quando disponíveis
- ✅ Preencha todas as informações obrigatórias
- ✅ Revise cuidadosamente antes de enviar
- ✅ Siga o padrão EBSERH de formatação
- ✅ Inclua referências bibliográficas

**DON'T (Não faça):**
- ❌ Enviar documentos incompletos
- ❌ Usar formatação personalizada
- ❌ Ignorar feedback da IA
- ❌ Submeter sem revisar
- ❌ Esquecer de salvar localmente uma cópia

---

### ⏰ Gestão de Tarefas

**DO:**
- ✅ Execute tarefas assim que receber
- ✅ Leia o documento completo antes de aprovar
- ✅ Escreva pareceres claros e objetivos
- ✅ Use notificações para não perder prazos
- ✅ Comunique bloqueios imediatamente

**DON'T:**
- ❌ Deixar tarefas para última hora
- ❌ Aprovar sem ler
- ❌ Dar pareceres vagos ("OK", "Aprovado")
- ❌ Ignorar notificações
- ❌ Ficar com tarefas paradas

---

### 🔐 Segurança

**DO:**
- ✅ Use senha forte e única
- ✅ Nunca compartilhe sua senha
- ✅ Faça logout ao sair
- ✅ Verifique o destinatário antes de aprovar
- ✅ Mantenha seu email atualizado

**DON'T:**
- ❌ Usar senha fraca (123456, senha123)
- ❌ Anotar senha em papel
- ❌ Deixar sessão aberta em computador compartilhado
- ❌ Clicar em links suspeitos
- ❌ Assinar sem verificar o documento

---

### 💬 Comunicação

**DO:**
- ✅ Use comentários para discussões
- ✅ Mencione pessoas relevantes (@email)
- ✅ Seja claro e respeitoso
- ✅ Responda comentários direcionados a você
- ✅ Use threads para organizar conversas

**DON'T:**
- ❌ Discutir fora do sistema (perde rastreabilidade)
- ❌ Fazer comentários genéricos
- ❌ Ignorar menções
- ❌ Usar linguagem inadequada

---

### 📊 Organização

**DO:**
- ✅ Mantenha seus documentos organizados
- ✅ Use códigos corretamente
- ✅ Acompanhe vencimentos
- ✅ Atualize documentos regularmente
- ✅ Use filtros e busca avançada

**DON'T:**
- ❌ Criar documentos duplicados
- ❌ Deixar documentos vencerem
- ❌ Ignorar documentos obsoletos
- ❌ Perder controle de versões

---

### 🚀 Produtividade

**Atalhos úteis:**
- `Alt + N`: Novo documento
- `Alt + T`: Minhas tarefas
- `Alt + B`: Busca avançada
- `Alt + D`: Dashboard

**Automações:**
- Configure notificações inteligentes
- Use filtros salvos para buscas frequentes
- Crie templates para documentos recorrentes
- Agende relatórios periódicos

---

## 📞 Precisa de Ajuda?

### 🆘 Suporte Técnico

**Problemas no sistema:**
- 📧 Email: suporte.ged@hospital.ebserh.gov.br
- 📱 WhatsApp: (85) 9999-9999
- 🌐 Portal: http://suporte.ged.hospital

**Horário de atendimento:**
- Segunda a Sexta: 8h às 18h
- Urgências: 24/7 (telefone de plantão)

---

### 📚 Documentação Técnica

Para documentação técnica detalhada (administradores/desenvolvedores):
- Ver `README.md`
- Ver `SECURITY.md`
- Ver `docs/` (documentos técnicos)

---

### 🎓 Treinamento

**Vídeos tutoriais disponíveis:**
- Como criar seu primeiro documento
- Assinando via WhatsApp
- Gerenciando tarefas
- Busca avançada de documentos

**Acesse:** `Menu → Ajuda → Tutoriais`

---

## 🎉 Conclusão

O **GED EBSERH** foi desenvolvido para tornar a gestão de documentos **simples, segura e eficiente**.

**Lembre-se:**
- ✅ Use o sistema regularmente
- ✅ Mantenha suas informações atualizadas
- ✅ Siga o workflow estabelecido
- ✅ Comunique-se através do sistema
- ✅ Respeite prazos e responsabilidades

**Sua colaboração é fundamental para o sucesso do sistema! 🚀**

---

*Última atualização: Dezembro 2024*
*Versão do documento: 2.0*
*Sistema GED EBSERH - Gestão Eletrônica de Documentos*
