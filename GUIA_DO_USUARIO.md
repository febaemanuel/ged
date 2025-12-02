# 📖 Guia do Usuário - Sistema GED EBSERH

> **Sistema de Gestão Eletrônica de Documentos para Hospitais da EBSERH**
> Versão 2.1 | Atualizado em: Dezembro 2024

---

## 📋 Índice Rápido

1. [O que é o GED EBSERH?](#1-o-que-é-o-ged-ebserh)
2. [Como Acessar](#2-como-acessar)
3. [Perfis e Permissões](#3-perfis-e-permissões)
4. [Dashboard](#4-dashboard)
5. [Criar Documentos](#5-criar-documentos)
6. [Sistema de Tarefas](#6-sistema-de-tarefas)
7. [Workflow Completo](#7-workflow-completo)
8. [Notificações](#8-notificações)
9. [**WhatsApp e Assinatura** ⭐](#9-whatsapp-e-assinatura-digital)
10. [Buscar Documentos](#10-buscar-documentos)
11. [Comentários](#11-comentários)
12. [Repositório Público](#12-repositório-público)
13. [Templates](#13-templates)
14. [FAQ](#14-perguntas-frequentes)
15. [Dicas](#15-dicas-e-boas-práticas)

---

## 1. O que é o GED EBSERH?

O **GED EBSERH** é o sistema oficial de **Gestão Eletrônica de Documentos** para hospitais da rede EBSERH.

### 🎯 Para que serve?

- ✅ Centralizar todos os documentos institucionais (POPs, Manuais, Protocolos, Políticas, etc.)
- ✅ Padronizar processos de criação e aprovação
- ✅ Controlar versões e validades automaticamente
- ✅ Facilitar busca e consulta
- ✅ Garantir rastreabilidade e conformidade

### ✨ Principais Funcionalidades

- 📱 **WhatsApp**: Notificações e aprovações pelo celular
- 🤖 **Inteligência Artificial**: Análise automática de documentos (DeepSeek AI)
- 🔐 **Assinatura Digital**: Registros auditáveis com hash SHA-256
- 📊 **Dashboard Inteligente**: Métricas e indicadores em tempo real
- 🔄 **Workflow UGQ**: Processo centralizado pela Qualidade
- 📚 **Repositório Público**: Documentos publicados acessíveis a todos

---

## 2. Como Acessar

### 🌐 Acesso Web

1. Abra o navegador (Chrome, Firefox, Edge ou Safari)
2. Acesse: `http://[servidor-do-hospital]:5000`
3. Faça login com seu **email** e **senha**
4. Pronto!

### 📱 Acesso via WhatsApp

Se o WhatsApp estiver habilitado no hospital:

1. Cadastre seu número de celular no sistema (Meu Perfil)
2. Aguarde mensagem de boas-vindas
3. Digite **"menu"** para ver suas tarefas
4. Siga as instruções interativas

> **💡 Dica:** Salve o número do GED nos seus contatos!

### 🔑 Primeiro Acesso

- Você receberá email com credenciais temporárias
- Altere a senha no primeiro login
- Configure seu número de WhatsApp (opcional)

---

## 3. Perfis e Permissões

O sistema possui **6 perfis** com permissões específicas:

### 👤 1. Usuário Comum

**Você pode:**
- ✅ Criar documentos
- ✅ Fazer upload de arquivos (PDF, Word, LibreOffice)
- ✅ Visualizar seus documentos
- ✅ Executar tarefas atribuídas
- ✅ Comentar em documentos
- ✅ Receber notificações

**Limitações:**
- ❌ Não pode aprovar documentos de outros
- ❌ Não pode gerenciar usuários

---

### 👨‍💼 2. Gerente de Setor

**Tudo do Usuário Comum +:**
- ✅ Ver todos documentos do setor
- ✅ Atribuir tarefas para equipe
- ✅ Aprovar documentos do setor
- ✅ Acessar relatórios gerenciais
- ✅ Usar recursos de IA

**Responsabilidades:**
- 📊 Monitorar prazos
- 👥 Designar responsáveis
- ✅ Garantir qualidade

---

### 🔬 3. Triador UGQ

**Perfil da Unidade de Gestão da Qualidade**

**O que faz:**
- ✅ Recebe documentos novos dos setores
- ✅ Realiza triagem com **3 checkpoints**:
  - ✔️ **Checkpoint 1:** Formatação EBSERH
  - ✔️ **Checkpoint 2:** Completude
  - ✔️ **Checkpoint 3:** Adequação técnica
- ✅ Aprova OU devolve para correções
- ✅ Adiciona observações

**Fluxo:**
```
Documento → Triador analisa →
   ↓ OK                  ↓ Problema
Validação            Volta p/ Autor
```

---

### 🎯 4. Validador UGQ

**Perfil sênior da Qualidade**

**O que faz:**
- ✅ Valida tecnicamente documentos
- ✅ **Gera código definitivo** (ex: POP.UGQ-CHUFC.001 v1)
- ✅ Monta **Bloco de Assinatura**
- ✅ Define modo: **Sequencial** ou **Concomitante**
- ✅ Acompanha aprovações
- ✅ **Publica** documento final
- ✅ Atualiza Lista Mestra

**Responsabilidades críticas:**
- 📝 Codificação correta
- 👥 Seleção de aprovadores
- ✅ Conformidade normativa
- 📋 Manutenção da Lista Mestra

---

### 🏢 5. Responsável Interno

**Responsável por processos/áreas específicas**

**O que faz:**
- ✅ Gerencia documentos da sua área
- ✅ Aprova documentos relacionados
- ✅ Monitora validades
- ✅ Solicita revisões

**Exemplos:**
- Responsável Técnico de UTI
- Coordenador de Farmácia
- Chefe de CCIH

---

### 👑 6. Administrador

**Controle total**

**O que faz:**
- ✅ Gerenciar usuários
- ✅ Configurar sistema
- ✅ Visualizar tudo
- ✅ Acessar logs
- ✅ Configurar integrações (WhatsApp, IA, Email)
- ✅ Gerar backups

**Acessos exclusivos:**
- ⚙️ Painel administrativo
- 📊 Dashboard executivo
- 🔧 Configurações globais
- 📈 Relatórios avançados

---

## 4. Dashboard

Ao fazer login, você vê o **Dashboard** - sua central de controle:

### Para Usuários Comuns:

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

### Para Gerentes:

```
┌─────────────────────────────────────┐
│  Dashboard - Gerência               │
├─────────────────────────────────────┤
│  📊 Estatísticas do Setor           │
│  • Documentos: 45 (3 vencendo)      │
│  • Tarefas Ativas: 12               │
│  • Taxa de Conclusão: 87%           │
│                                     │
│  📋 Equipe                          │
│  • Maria: 2 tarefas                 │
│  • Pedro: 1 atrasada ⚠️             │
└─────────────────────────────────────┘
```

### Para UGQ (Triador/Validador):

```
┌─────────────────────────────────────┐
│  Fila da Qualidade                  │
├─────────────────────────────────────┤
│  📥 Em Triagem (8)                  │
│  ✓ Em Validação (5)                 │
│  📝 Em Aprovação (12)               │
│  ⏰ Urgentes (2)                    │
│                                     │
│  🎯 Ações Rápidas                   │
│  • Próximo da fila                  │
│  • Publicar aprovados               │
└─────────────────────────────────────┘
```

### 🎯 Ações Rápidas (topo):

- 🆕 Novo Documento
- 📋 Minhas Tarefas
- 🔍 Busca Avançada
- 🔔 Notificações
- 👤 Meu Perfil

---

## 5. Criar Documentos

### 📤 Passo a Passo

**1. Acesse "Novo Documento"**
- Botão "+ Novo Documento"
- Ou menu: `Documentos → Criar Novo`

**2. Preencha as Informações**

```
┌─────────────────────────────────────────┐
│  Título *                               │
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
│  [ ] CHUFC - Complexo Hospitalar       │
│  [ ] HUWC - Hospital Walter Cantídio   │
│  [ ] MEAC - Maternidade Assis C.       │
│                                         │
│  Descrição                              │
│  [________________________________]     │
└─────────────────────────────────────────┘
```

**3. Faça Upload do Arquivo**

Formatos aceitos:
- ✅ **PDF** (.pdf)
- ✅ **Word** (.doc, .docx)
- ✅ **LibreOffice** (.odt)

Tamanho máximo: **16MB**

> **⚠️ Importante:** Use o formato EBSERH antes de enviar!

**4. Aguarde a IA Processar**

O sistema automaticamente:
- 🤖 Extrai o texto
- 🏷️ Identifica tipo e categorias
- 📊 Gera metadados
- 💡 Sugere responsável
- 📝 Cria resumo

⏱️ Tempo médio: 10-30 segundos

**5. Revise e Envie**

- Confira informações da IA
- Ajuste se necessário
- Clique em **"Enviar para Triagem"**

**6. Acompanhe**

Seu documento recebe:
- ✅ **Código Único**: `DOC-20241202-143052-001` (permanente)
- ✅ **Código Provisório**: `POP-PROV-20241202143052`
- ✅ Status: **"Em Triagem"**

---

### 📋 Tipos de Documento

| Tipo | Sigla | Validade | Descrição |
|------|-------|----------|-----------|
| **POP** | POP | 2 anos | Procedimento Operacional Padrão |
| **Manual** | MAN | 2 anos | Guia completo de processos |
| **Protocolo** | PROT | 2 anos | Diretrizes clínicas/assistenciais |
| **Política** | POL | 4 anos | Diretrizes institucionais |
| **Regimento** | REG | 4 anos | Normas de funcionamento |
| **Regulamento** | REGUL | 4 anos | Conjunto de regras |

---

### 📊 Códigos do Documento

Cada documento tem **3 códigos diferentes**:

#### 1️⃣ Código Único (permanente)
```
DOC-20241202-143052-001
│    │        │       │
│    │        │       └─ Sequencial aleatório
│    │        └───────── Hora (14:30:52)
│    └────────────────── Data (2024-12-02)
└─────────────────────── Prefixo fixo
```
**Uso:** Identificação interna permanente (nunca muda)

#### 2️⃣ Código Provisório
```
POP-PROV-20241202143052
│    │     │
│    │     └─────────────── Timestamp
│    └───────────────────── Indica provisório
└────────────────────────── Tipo
```
**Uso:** Enquanto não está aprovado

#### 3️⃣ Código Definitivo (UGQ gera)
```
POP.UGQ-CHUFC.001 v1
│   │   │     │   │
│   │   │     │   └─── Versão (v1, v2, v3...)
│   │   │     └─────── Sequencial (001, 002...)
│   │   └───────────── Abrangência (CHUFC/HUWC/MEAC)
│   └───────────────── Setor (UGQ, Enfermagem...)
└───────────────────── Tipo (POP, MAN, PROT...)
```

**Exemplos reais:**
- `POP.UGQ-CHUFC.001 v1` - Primeiro POP da UGQ no CHUFC
- `MAN.Enfermagem-HUWC.015 v2` - Manual 15 da Enfermagem, versão 2
- `PROT.CCIH-MEAC.007 v3` - Protocolo 7 da CCIH, versão 3

**Uso:** Código oficial após publicação (Lista Mestra)

> **💡 Dica:** Ao buscar, use o código definitivo!

---

### 🔄 Versionamento

Quando um documento publicado precisa de atualização:

**1. Abra o documento publicado**
**2. Clique em "Nova Versão"**
**3. Sistema automaticamente:**
- ✅ Copia informações
- ✅ Mantém código definitivo
- ✅ Incrementa versão (v1 → v2)
- ✅ Vincula à anterior

**4. Faça alterações**
**5. Submeta para triagem**

**Histórico:**
```
v1.0 - 01/01/2024 - Original (OBSOLETA)
v2.0 - 15/06/2024 - Atualização (ATIVA)
v3.0 - 02/12/2024 - Revisão (EM APROVAÇÃO)
```

---

### 🗑️ Exclusão (Soft Delete)

O sistema usa **exclusão suave**:

**O que significa?**
- Documentos "deletados" não são removidos
- São marcados como deletados
- Podem ser recuperados

**Como deletar:**
1. Abra o documento
2. `⋮ Mais opções` → **"Excluir"**
3. Confirme

**Como recuperar:**
1. Admin acessa: `Documentos → Lixeira`
2. Seleciona documento
3. **"Restaurar"**

> **🔒 Segurança:** Todas ações são registradas em log.

---

## 6. Sistema de Tarefas

### 📋 Tipos de Tarefas

| Tipo | Descrição | Quem Recebe |
|------|-----------|-------------|
| **Analisar** | Revisar e dar parecer | Gerentes |
| **Validar Conteúdo** | Validação técnica | Especialistas |
| **Validar e Codificar** | Gerar código definitivo | Validador UGQ |
| **Aprovar e Assinar** | Aprovação com assinatura digital | Aprovadores do bloco |
| **Realizar Correção** | Corrigir problemas | Autor do documento |
| **Publicar** | Publicação oficial | Validador UGQ |

---

### ✅ Executar uma Tarefa

**1. Acesse "Minhas Tarefas"**
- Dashboard → "Minhas Tarefas"
- Ou ícone 📋 no menu

**2. Selecione a tarefa**

```
┌────────────────────────────────────────────┐
│ 📄 Aprovar e assinar documento             │
│ POP.UGQ-CHUFC.001 v1                       │
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
- Verifique detalhes
- Consulte anexos

**4. Tome uma decisão**

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
│  🔒 Senha de confirmação: *            │
│  [______________]                      │
│                                        │
│  [Confirmar]                           │
└────────────────────────────────────────┘
```

**5. Confirme com senha**
- Digite sua senha de login
- Gera **assinatura digital**:
  - Hash SHA-256
  - Timestamp
  - IP e navegador
  - Registro auditável

**6. Pronto!**
- Tarefa concluída ✅
- Documento avança
- Próximo é notificado

---

### ⏰ Prazos e Alertas

**Código de cores:**
```
🟢 5+ dias: Verde (tranquilo)
🟡 2-4 dias: Amarelo (atenção)
🔴 1 dia: Vermelho (urgente)
⚫ Atrasada: Cinza (crítico!)
```

**Notificações automáticas:**
- 📧 Email ao receber tarefa
- 📱 WhatsApp (se habilitado)
- 🔔 In-app
- ⏰ Lembrete 24h antes
- ⚠️ Alerta se atrasar

---

## 7. Workflow Completo

### 🔄 Fluxo do Documento

```
┌──────────────────────────────────────────────────────────┐
│                    FLUXO GED EBSERH                      │
└──────────────────────────────────────────────────────────┘

1️⃣ CRIAÇÃO
   👤 Autor cria → Upload
   ↓
   🤖 IA processa
   ↓
   📤 Envia para UGQ
   Status: "Novo" → "Em Triagem"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2️⃣ TRIAGEM UGQ
   🔬 Triador analisa:

   ✓ Checkpoint 1: Formatação EBSERH
   ✓ Checkpoint 2: Completude
   ✓ Checkpoint 3: Adequação técnica

   Decisão:
   • ✅ OK → Validação
   • ❌ Problema → Volta p/ Autor

   Status: "Em Triagem" → "Em Validação" (ou "Em Correção")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3️⃣ VALIDAÇÃO UGQ
   🎯 Validador:

   • Valida tecnicamente
   • Gera código definitivo (POP.UGQ-CHUFC.001 v1)
   • Monta Bloco de Assinatura:
     - Seleciona aprovadores
     - Define ordem (sequencial/concomitante)

   Status: "Em Validação" → "Validado" → "Em Aprovação"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4️⃣ BLOCO DE ASSINATURA

   Modo Sequencial:
   👤 Aprovador 1 → ✅ → Notifica 2
   👤 Aprovador 2 → ✅ → Notifica 3
   👤 Aprovador 3 → ✅ → Completo!

   Modo Concomitante:
   👤 Todos assinam em paralelo
   ✓ Todos assinaram → Completo!

   Se reprovar:
   ❌ → "Em Ajustes" → Autor corrige

   Status: "Em Aprovação" → "Aprovado"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5️⃣ PUBLICAÇÃO
   🎯 Validador UGQ:

   • Gera PDF final codificado
   • Adiciona à Lista Mestra
   • Define vencimento (2 ou 4 anos)
   • Publica oficialmente
   • Notifica todos

   Status: "Aprovado" → "Publicado" ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 RESULTADO

• Documento no Repositório Público
• Código definitivo ativo
• Controle automático de validade
• Histórico completo
• Assinaturas registradas
```

---

## 8. Notificações

### 🔔 Canais de Notificação

O sistema envia por **3 canais**:

#### 1️⃣ In-App
- Ícone 🔔 no topo
- Contador de não lidas
- Tempo real

#### 2️⃣ Email
- Enviado para email cadastrado
- Link direto para ação
- Detalhes completos

#### 3️⃣ WhatsApp
- Mensagem instantânea
- Pode responder e assinar direto
- Menu interativo

---

### 📬 Eventos que Geram Notificações

| Evento | Você Recebe |
|--------|-------------|
| **Tarefa atribuída** | "Nova tarefa: Aprovar documento XYZ" |
| **Documento aprovado** | "Seu documento foi aprovado!" |
| **Documento reprovado** | "Precisa correções: [motivo]" |
| **Prazo próximo** | "Tarefa vence em 24h" |
| **Documento vencendo** | "Documento vence em 30 dias" |
| **Documento vencido** | "Documento venceu! Atualize" |
| **Menção** | "@você foi mencionado" |
| **IA concluída** | "IA terminou análise" |

---

### ⚙️ Configurar Preferências

**Acesse:** `Meu Perfil → Notificações`

```
┌─────────────────────────────────────────┐
│  Preferências de Notificações          │
├─────────────────────────────────────────┤
│  Receber por:                           │
│  ☑ Email                               │
│  ☑ WhatsApp                            │
│  ☑ In-App (sempre ativo)               │
│                                         │
│  Notificar sobre:                       │
│  ☑ Tarefas atribuídas                  │
│  ☑ Prazos próximos (24h)               │
│  ☑ Documentos vencendo (30d)           │
│  ☑ Menções                             │
│  ☐ Atualizações do sistema             │
│                                         │
│  Horário WhatsApp:                      │
│  [08:00] até [18:00]                   │
│  ☑ Somente dias úteis                  │
│                                         │
│  [Salvar]                               │
└─────────────────────────────────────────┘
```

---

## 9. WhatsApp e Assinatura Digital

### 📱 Como Funciona

O GED integra com WhatsApp via **Evolution API v2.2.2**, permitindo:

- ✅ Receber notificações instantâneas
- ✅ Ver tarefas pendentes
- ✅ Aprovar documentos
- ✅ **Assinar digitalmente pelo WhatsApp**
- ✅ Tudo sem sair do celular!

---

### 🔐 Assinando via WhatsApp

> **⚠️ IMPORTANTE:** O sistema pede seu **EMAIL** para confirmar, NÃO sua senha!

#### Exemplo de Conversa:

```
📱 Sistema GED EBSERH

👋 Olá, Dr. João Silva!

📋 Você tem 2 documentos pendentes:

1️⃣ POP.UGQ-CHUFC.001 v1
   Manual de Procedimentos da UTI
   ⏰ Prazo: Hoje, 17:00

2️⃣ PROT.CCIH-CHUFC.015 v2
   Protocolo de Sepse
   ⏰ Prazo: 05/12/2024

💬 Digite o número do documento:
```

**Você digita:** `1`

```
📄 POP.UGQ-CHUFC.001 v1
Manual de Procedimentos da UTI

👤 Autor: Maria Silva (Enfermagem)
📅 Criado: 28/11/2024
⏰ Prazo: Hoje, 17:00
🔗 Ver: [link completo]

💬 O que deseja?

1️⃣ - Aprovar e assinar
2️⃣ - Reprovar
3️⃣ - Ver documento
4️⃣ - Voltar
```

**Você digita:** `1`

```
📝 Digite seu parecer ou comentário:
(ou "ok" para aprovar sem comentário)
```

**Você digita:** `Documento bem elaborado, aprovado.`

```
🔒 Confirmação de Assinatura

Para confirmar, digite seu *email cadastrado*.

💡 Dica: j****o@hospital.com

_Responda 0 para cancelar._
```

**Você digita:** `joao.silva@hospital.com`

```
✅ ASSINATURA REGISTRADA COM SUCESSO!

📄 Documento: POP.UGQ-CHUFC.001 v1
   Manual de Procedimentos da UTI

⏰ Data/Hora: 02/12/2024 14:35:27
👤 Assinado por: Dr. João Silva
💬 Parecer: "Documento bem elaborado, aprovado."
🔐 Hash: 8A7F9D2E1B3C (SHA-256)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Você ainda tem 1 documento pendente.
Digite "menu" para ver.
```

---

### ⚠️ Segurança no WhatsApp

**Medidas de proteção:**

1. ✅ **Confirmação por email:** Sistema pede email cadastrado (case insensitive)
2. ✅ **3 tentativas:** Após 3 erros, bloqueia por 30 minutos
3. ✅ **Timeout:** Sessão expira após 15min inativa
4. ✅ **Assinatura auditável:** Registra IP, timestamp, hash SHA-256
5. ✅ **Horário configurável:** Funciona apenas em horário definido
6. ✅ **Número autorizado:** Só funciona com números cadastrados
7. ✅ **Dica de email:** Mostra email parcialmente oculto (j****o@hospital.com)

**Como funciona a validação de email:**
```
Você digita: joao.silva@hospital.com
Sistema compara com: joao.silva@hospital.com ✅

Você digita: JOAO.SILVA@HOSPITAL.COM
Sistema compara: Case insensitive ✅

Você digita: joao@hospital.com
Sistema compara: joao.silva@hospital.com ❌
"Email incorreto! Tentativas restantes: 2"
```

**Comandos úteis:**
- `menu` - Ver tarefas pendentes
- `docs` - Documentos recentes
- `ajuda` - Comandos disponíveis
- `0` - Cancelar ação atual
- `sair` - Encerrar sessão

---

### 🔒 Bloqueio por Tentativas

```
Tentativa 1 (email errado):
❌ Email incorreto!
💡 Dica: j****o@hospital.com
Tentativas restantes: 2

Tentativa 2 (email errado):
❌ Email incorreto!
💡 Dica: j****o@hospital.com
Tentativas restantes: 1

Tentativa 3 (email errado):
🚫 Conta temporariamente bloqueada

Muitas tentativas incorretas.
Tente novamente em 30 minutos.
```

---

## 10. Buscar Documentos

### 🔍 Busca Avançada

Acesse: `Menu → Buscar Documentos`

```
┌──────────────────────────────────────────────┐
│  🔍 Busca Avançada                           │
├──────────────────────────────────────────────┤
│  Texto:                                      │
│  [________________________________]          │
│  (busca em título, código, descrição)        │
│                                              │
│  Tipo:                                       │
│  [ ] POP  [ ] Manual  [ ] Protocolo         │
│  [ ] Política  [ ] Regimento                │
│                                              │
│  Status:                                     │
│  [ ] Publicado  [ ] Em Aprovação            │
│  [ ] Em Triagem                             │
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
│  Vencimento:                                 │
│  ( ) Todos                                  │
│  ( ) Vence em 30 dias                       │
│  ( ) Vencidos                               │
│                                              │
│  [🔍 Buscar]  [🗑️ Limpar]                   │
└──────────────────────────────────────────────┘
```

---

### 💡 Dicas de Busca

**Busca por código:**
```
✅ POP.UGQ-CHUFC.001     → Encontra exatamente
✅ POP.UGQ-CHUFC         → Todos da UGQ no CHUFC
✅ POP.                   → Todos os POPs
✅ -CHUFC                 → Todos do CHUFC
✅ v3                     → Todos versão 3
```

**Busca por texto:**
```
✅ "manual uti"          → Manual + UTI
✅ procedimento lavagem  → Procedimento E lavagem
✅ protocolo sepse       → Protocolo de sepse
```

**Operadores:**
```
✅ titulo:manual         → Busca só no título
✅ autor:"Maria Silva"   → Documentos da Maria
✅ setor:enfermagem      → Setor específico
```

---

### 📊 Resultados

```
┌────────────────────────────────────────────────┐
│  Encontrados: 15 documentos                    │
│  Ordenar: [Mais recentes ▼]                   │
├────────────────────────────────────────────────┤
│  📄 POP.UGQ-CHUFC.001 v1                       │
│  Manual de Procedimentos da UTI                │
│  👤 Maria | 📅 02/12/2024 | ✅ Publicado       │
│  [Ver] [Download PDF]                          │
├────────────────────────────────────────────────┤
│  📄 PROT.CCIH-HUWC.008 v2                      │
│  Protocolo de Higienização                     │
│  👤 João | 📅 01/12/2024 | 🟡 Em Aprovação     │
│  [Ver]                                         │
└────────────────────────────────────────────────┘
```

**Ordenação:**
- Mais recentes
- Mais antigos
- Alfabética (A-Z)
- Vencimento próximo

---

## 11. Comentários

### 💬 Sistema de Discussão

Cada documento tem área de discussão para:

- ✅ Adicionar comentários
- ✅ Responder (threads)
- ✅ Mencionar (@email)
- ✅ Editar/deletar

---

### ✍️ Adicionar Comentário

**1. Abra o documento**
**2. Role até "Comentários"**

```
┌──────────────────────────────────────────────┐
│  💬 Comentários (3)                          │
├──────────────────────────────────────────────┤
│  ✍️ Adicionar:                               │
│  [____________________________________]      │
│                                              │
│  💡 Use @email para mencionar               │
│                                              │
│  [Comentar]  [Cancelar]                     │
└──────────────────────────────────────────────┘
```

**3. Digite:**
```
@maria.silva@hospital.com, revise seção 3.2?
Prazo parece incorreto.
```

**4. Publique**

**Resultado:**
- ✅ Comentário publicado
- ✅ Maria recebe notificação
- ✅ Todos veem

---

### 🗣️ Menções

Quando é mencionado:

```
🔔 Notificação

💬 Menção em comentário

📄 POP.UGQ-CHUFC.001 v1
   Manual de Procedimentos

👤 João comentou:
"@voce@hospital.com, revise seção 3.2?"

[Ver Comentário]
```

---

### 🧵 Threads (Respostas)

```
┌──────────────────────────────────────────────┐
│  João - 02/12/2024 14:30                    │
│  Encontrei erro na página 5.                │
│                                              │
│  [Responder] [↓ 2 respostas]                │
│                                              │
│    └─ Maria - 02/12/2024 14:45              │
│       Corrigi! Obrigada.                    │
│                                              │
│       [Responder]                            │
│                                              │
│         └─ João - 02/12/2024 15:00          │
│            Perfeito! ✅                      │
└──────────────────────────────────────────────┘
```

---

## 12. Repositório Público

### 📚 O que é?

Repositório com **todos documentos publicados** do hospital, acessível a todos os usuários.

### 🔍 Como Acessar

**Menu → Repositório Público**

```
┌──────────────────────────────────────────────┐
│  📚 Repositório Público de Documentos        │
├──────────────────────────────────────────────┤
│  🔍 Busca:                                   │
│  [_____________________________] [🔍]        │
│                                              │
│  Filtros:                                    │
│  Tipo: [Todos ▼]                            │
│  Setor: [Todos ▼]                           │
│  Abrangência: [Todas ▼]                     │
│                                              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│                                              │
│  📄 POP.UGQ-CHUFC.001 v3                     │
│  Manual de Procedimentos da UTI              │
│  📅 Publicado: 02/12/2024                    │
│  ⏰ Vencimento: 02/12/2026                   │
│  🏥 CHUFC - UGQ                              │
│  [📥 Download PDF]                           │
│                                              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━          │
│                                              │
│  📄 PROT.CCIH-HUWC.008 v2                    │
│  Protocolo de Higienização Hospitalar        │
│  📅 Publicado: 28/11/2024                    │
│  ⏰ Vencimento: 28/11/2026                   │
│  🏥 HUWC - CCIH                              │
│  [📥 Download PDF]                           │
└──────────────────────────────────────────────┘
```

### ✨ Recursos

- 🔍 Busca por texto
- 📊 Filtros avançados
- 📥 Download direto de PDFs
- 📋 Visualizar histórico de versões
- ⏰ Ver data de vencimento
- 📈 Estatísticas de acesso

---

## 13. Templates

### 📝 O que são?

Modelos pré-aprovados que facilitam criação de documentos no padrão EBSERH.

**Vantagens:**
- ✅ Formatação correta garantida
- ✅ Seções obrigatórias incluídas
- ✅ Acelera criação
- ✅ Reduz erros

---

### 🆕 Usar um Template

**1. "Novo Documento" → "Usar Template"**

```
┌──────────────────────────────────────────┐
│  📚 Templates Disponíveis                │
├──────────────────────────────────────────┤
│  🔍 [____________] 🔍                    │
│                                          │
│  📋 POP - Modelo Geral                   │
│  Procedimento Operacional Padrão         │
│  📊 Usado 45 vezes                       │
│  [Usar]                                  │
├──────────────────────────────────────────┤
│  📘 Manual - Modelo EBSERH               │
│  Manual institucional completo           │
│  📊 Usado 12 vezes                       │
│  [Usar]                                  │
├──────────────────────────────────────────┤
│  🏥 Protocolo Assistencial              │
│  Protocolo clínico padrão                │
│  📊 Usado 28 vezes                       │
│  [Usar]                                  │
└──────────────────────────────────────────┘
```

**2. Template vem com:**
- ✅ Formatação EBSERH
- ✅ Cabeçalho/rodapé
- ✅ Seções estruturadas
- ✅ Campos para preencher

**3. Baixe, edite, faça upload**

---

## 14. Perguntas Frequentes

### ❓ FAQ - Geral

**Q: Esqueci minha senha. Como recupero?**
A: Login → "Esqueci minha senha" → Digite email → Siga instruções.

---

**Q: Posso editar documento após enviar?**
A:
- ✅ Se está em "Novo" ou "Em Análise": Sim
- ❌ Se em triagem: Não, a menos que devolvido
- ✅ Se receber tarefa "Realizar Correção": Sim

---

**Q: Como sei se foi aprovado?**
A: Notificação por email, WhatsApp e in-app. Status muda para "Aprovado" ou "Publicado".

---

**Q: Quanto tempo demora a IA?**
A: 10-30 segundos, dependendo do tamanho.

---

**Q: Posso deletar documento publicado?**
A: Não diretamente. Publicados podem ser:
- Marcados como "Obsoletos" (nova versão)
- "Cancelados" (admin, com justificativa)

---

**Q: Tarefa atrasada. E agora?**
A:
1. Execute o mais rápido possível
2. Se bloqueado, comunique gerente
3. Justifique no sistema
4. Gerente pode estender prazo

---

**Q: WhatsApp: esqueci meu email cadastrado!**
A: Acesse o sistema web → Meu Perfil → veja seu email.

---

**Q: Bloqueado no WhatsApp. O que fazer?**
A: Aguarde 30 minutos. Após 3 tentativas incorretas de email, sistema bloqueia temporariamente.

---

### ❓ FAQ - Gerentes

**Q: Como atribuo tarefa?**
A:
1. Abra documento
2. "Atribuir Tarefa"
3. Selecione tipo
4. Escolha responsável
5. Defina prazo/prioridade
6. "Criar"

---

**Q: Posso ver tarefas do setor?**
A: Sim! `Dashboard → Visão do Setor`.

---

**Q: Como gero relatório do setor?**
A: `Relatórios → Relatório do Setor → Período → Gerar`.

---

### ❓ FAQ - UGQ

**Q: Diferença entre código provisório e definitivo?**
A:
- **Provisório:** Auto (ex: POP-PROV-20241202143052)
- **Definitivo:** Validador UGQ gera (ex: POP.UGQ-CHUFC.001 v1)

Padrão: **TIPO.SETOR-ABRANGENCIA.SEQ vVERSÃO**

É o oficial da Lista Mestra.

---

**Q: Como monto bloco sequencial?**
A:
1. Documento validado
2. "Montar Bloco de Assinatura"
3. "Sequencial"
4. Adicione aprovadores **na ordem**
5. Confirme

Ordem 1 assina primeiro, depois 2, etc.

---

**Q: Aprovador de férias?**
A:
1. Substituir (antes de enviar)
2. Aguardar retorno (se não urgente)
3. Remontar bloco (se já enviado)

---

**Q: Posso publicar antes de todas assinaturas?**
A: Não. Sistema só permite após **todas** aprovações.

---

**Q: Como adiciono à Lista Mestra?**
A: Automático! Ao publicar, sistema adiciona com:
- Código definitivo
- Data publicação
- Validade calculada
- Status atualizado

---

## 15. Dicas e Boas Práticas

### ✅ Criação de Documentos

**FAÇA:**
- ✅ Use templates
- ✅ Preencha tudo obrigatório
- ✅ Revise antes de enviar
- ✅ Siga padrão EBSERH
- ✅ Inclua referências

**NÃO FAÇA:**
- ❌ Enviar incompleto
- ❌ Formatação personalizada
- ❌ Ignorar feedback da IA
- ❌ Submeter sem revisar

---

### ⏰ Gestão de Tarefas

**FAÇA:**
- ✅ Execute ao receber
- ✅ Leia documento completo
- ✅ Pareceres claros
- ✅ Use notificações
- ✅ Comunique bloqueios

**NÃO FAÇA:**
- ❌ Deixar para última hora
- ❌ Aprovar sem ler
- ❌ Pareceres vagos ("OK")
- ❌ Ignorar notificações

---

### 🔐 Segurança

**FAÇA:**
- ✅ Senha forte e única
- ✅ Nunca compartilhe senha
- ✅ Logout ao sair
- ✅ Verifique antes de aprovar
- ✅ Email atualizado

**NÃO FAÇA:**
- ❌ Senha fraca (123456)
- ❌ Anotar senha
- ❌ Sessão aberta em PC compartilhado
- ❌ Clicar links suspeitos
- ❌ Assinar sem verificar

---

### 📱 WhatsApp

**FAÇA:**
- ✅ Memorize seu email cadastrado
- ✅ Digite email corretamente (case insensitive)
- ✅ Use dica de email (j****o@hospital.com)
- ✅ Responda dentro do horário configurado
- ✅ Use comandos (menu, ajuda, 0)

**NÃO FAÇA:**
- ❌ Tentar adivinhar email
- ❌ Errar 3 vezes (bloqueia 30min)
- ❌ Usar fora do horário
- ❌ Compartilhar seu WhatsApp
- ❌ Assinar sem ler documento

---

### 💬 Comunicação

**FAÇA:**
- ✅ Use comentários
- ✅ Mencione (@email)
- ✅ Seja claro e respeitoso
- ✅ Responda menções
- ✅ Use threads

**NÃO FAÇA:**
- ❌ Discutir fora do sistema
- ❌ Comentários genéricos
- ❌ Ignorar menções
- ❌ Linguagem inadequada

---

### 🚀 Produtividade

**Atalhos úteis:**
- `Alt + N`: Novo documento
- `Alt + T`: Minhas tarefas
- `Alt + B`: Busca avançada
- `Alt + D`: Dashboard

**Automações:**
- Configure notificações inteligentes
- Use filtros salvos
- Crie templates recorrentes
- Agende relatórios

---

## 📞 Precisa de Ajuda?

### 🆘 Suporte Técnico

**Problemas no sistema:**
- 📧 Email: suporte.ged@hospital.ebserh.gov.br
- 📱 WhatsApp: (85) 9999-9999
- 🌐 Portal: http://suporte.ged.hospital

**Horário:**
- Segunda a Sexta: 8h às 18h
- Urgências: 24/7 (telefone plantão)

---

### 📚 Documentação Técnica

Para admins/desenvolvedores:
- `README.md` - Técnico completo
- `SECURITY.md` - Segurança
- `docs/` - Documentação técnica

---

### 🎓 Treinamentos

**Vídeos disponíveis:**
- Como criar primeiro documento
- Assinando via WhatsApp
- Gerenciando tarefas
- Busca avançada

**Acesse:** `Menu → Ajuda → Tutoriais`

---

## 🎉 Conclusão

O **GED EBSERH** foi desenvolvido para tornar a gestão de documentos **simples, segura e eficiente**.

### Lembre-se:

- ✅ Use o sistema regularmente
- ✅ Mantenha informações atualizadas
- ✅ Siga o workflow estabelecido
- ✅ Comunique-se através do sistema
- ✅ Respeite prazos
- ✅ **WhatsApp pede EMAIL, não senha!**

**Sua colaboração é fundamental! 🚀**

---

## 📋 Resumo de Comandos WhatsApp

```
menu       → Ver tarefas pendentes
docs       → Documentos recentes
ajuda      → Lista de comandos
0          → Cancelar ação atual
sair       → Encerrar sessão

Números:
1, 2, 3... → Selecionar opção/documento
```

---

## 🔐 Lembrete de Segurança WhatsApp

```
🔒 IMPORTANTE:

O sistema NUNCA pede sua SENHA pelo WhatsApp!

✅ Sistema pede: EMAIL cadastrado
❌ Sistema NÃO pede: Senha

Se alguém pedir senha pelo WhatsApp:
⚠️ É GOLPE! Não compartilhe!
📞 Reporte ao suporte imediatamente!
```

---

*Última atualização: Dezembro 2024*
*Versão do documento: 2.1*
*Sistema GED EBSERH - Gestão Eletrônica de Documentos*

---

## 📖 Changelog do Guia

**v2.1 (Dezembro 2024):**
- ✅ Corrigido: WhatsApp pede EMAIL (não senha)
- ✅ Adicionado: Sistema de bloqueio (3 tentativas, 30min)
- ✅ Atualizado: Código definitivo (TIPO.SETOR-ABRANGENCIA.SEQ vVERSÃO)
- ✅ Adicionado: Dica de email parcialmente oculto
- ✅ Adicionado: Evolution API v2.2.2
- ✅ Melhorado: Exemplos de assinatura WhatsApp
- ✅ Adicionado: FAQ sobre bloqueio WhatsApp
- ✅ Adicionado: Lembrete de segurança WhatsApp

**v2.0 (Dezembro 2024):**
- Versão inicial consolidada
