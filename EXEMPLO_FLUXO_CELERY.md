# Exemplo Prático: Upload de Documento com Celery

## 📝 Cenário: Maria envia um documento

Maria é uma enfermeira que precisa criar um novo POP (Procedimento Operacional Padrão) para o setor de UTI.

---

## 🎬 Passo a Passo - Visão do Usuário

### 1️⃣ Maria faz upload do documento

**Tela: Criar Novo Documento**

```
┌─────────────────────────────────────────────────────┐
│  📄 Criar Novo Documento                            │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Título: *                                          │
│  ┌───────────────────────────────────────────────┐ │
│  │ POP - Higienização de Mãos UTI                │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  Tipo: *                                            │
│  ┌───────────────────────────────────────────────┐ │
│  │ POP                                 ▼         │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  Setor: *                                           │
│  ┌───────────────────────────────────────────────┐ │
│  │ UTI - Adulto                        ▼         │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  Arquivo: *                                         │
│  ┌───────────────────────────────────────────────┐ │
│  │ 📎 POP_Higienizacao_v1.docx  (escolhido) ✓   │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  Descrição:                                         │
│  ┌───────────────────────────────────────────────┐ │
│  │ Procedimento padrão para higienização...      │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│           [ Cancelar ]    [ 💾 Criar Documento ]   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Maria clica em "Criar Documento"**

---

### 2️⃣ Resposta IMEDIATA (< 1 segundo)

```
┌─────────────────────────────────────────────────────┐
│  ✅ Sucesso!                                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ✓ Documento criado com sucesso!                   │
│                                                     │
│  📋 Código Provisório: GED-2025-001234              │
│  📊 Status: Novo                                    │
│                                                     │
│  🤖 Processamento com IA agendado...               │
│     Você receberá uma notificação quando           │
│     a análise estiver completa.                    │
│                                                     │
│           [ OK ]    [ Ver Documento ]              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**⏱️ Tempo de resposta: ~500ms**

Maria já pode continuar trabalhando! Ela não precisa esperar o processamento.

---

### 3️⃣ O que acontece NOS BASTIDORES (invisível para Maria)

```
TIMELINE DO PROCESSAMENTO EM BACKGROUND
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

t=0s     Flask Web recebe upload
         ├─ Valida arquivo (MIME type, extensão)
         ├─ Salva arquivo em disco
         ├─ Cria registro no banco PostgreSQL
         ├─ Agenda tarefa Celery: processar_documento_ia.delay(1234)
         └─ Retorna resposta para Maria ✅

t=0.5s   Maria vê mensagem de sucesso
         Maria pode continuar trabalhando! 🎉

t=1s     Celery Worker pega tarefa da fila Redis
         ├─ Tarefa: processar_documento_ia(documento_id=1234)
         └─ Status: STARTED

t=2s     Worker abre arquivo POP_Higienizacao_v1.docx
         ├─ Extrai texto do DOCX usando python-docx
         └─ Texto extraído: "1. OBJETIVO\n Este POP tem como..."

t=5s     Worker envia para IA DeepSeek
         ├─ API Request: POST https://api.deepseek.com/chat/completions
         ├─ Prompt: "Analise este documento e extraia metadados..."
         └─ Aguardando resposta...

t=12s    IA DeepSeek responde
         └─ Retorna JSON com metadados

t=13s    Worker processa resposta
         ├─ Extrai metadados:
         │  {
         │    "categoria": "Procedimento",
         │    "palavras_chave": ["higienização", "mãos", "UTI"],
         │    "requisitos": ["água", "sabão", "álcool 70%"],
         │    "tempo_execucao": "2 minutos",
         │    "nivel_complexidade": "Baixo"
         │  }
         ├─ Salva no campo documento.metadados_json
         ├─ Salva texto extraído
         └─ Cria log na tabela LogAI

t=14s    Worker confirma conclusão
         ├─ Commit no banco de dados
         └─ Status: SUCCESS ✅

t=15s    Worker agenda notificação por email
         ├─ Tarefa: enviar_notificacao_email.delay(
         │     usuario_id=maria.id,
         │     assunto="Documento processado",
         │     mensagem="O documento 'POP - Higienização...' foi processado!"
         │  )
         └─ Nova tarefa na fila

t=16s    Outro Worker envia email para Maria
         ├─ SMTP: smtp.gmail.com:587
         ├─ Para: maria@hospital.com
         └─ Email enviado ✅

t=17s    PROCESSAMENTO COMPLETO! 🎉
```

**📊 Resultado:**
- Maria esperou: **0.5 segundos** (só o upload)
- Processamento total: **17 segundos** (em background)
- Maria continuou trabalhando normalmente durante todo o processo!

---

### 4️⃣ Maria recebe notificação (15-30 segundos depois)

**Email recebido:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
De: Sistema GED <noreply@ged.com>
Para: maria@hospital.com
Assunto: Documento processado com sucesso ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Olá Maria,

O documento "POP - Higienização de Mãos UTI" foi
processado com sucesso!

📋 Código: GED-2025-001234
🤖 Análise IA: Concluída
📊 Metadados: Extraídos automaticamente

Você pode visualizar o documento em:
http://localhost:5000/documento/1234

Atenciosamente,
Sistema GED EBSERH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 5️⃣ Maria visualiza o documento processado

**Tela: Visualizar Documento**

```
┌─────────────────────────────────────────────────────┐
│  📄 POP - Higienização de Mãos UTI                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  Código: GED-2025-001234      Status: Novo          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  📋 Informações Básicas                             │
│  ├─ Tipo: POP                                       │
│  ├─ Setor: UTI - Adulto                             │
│  ├─ Criado por: Maria Silva                         │
│  └─ Data: 29/11/2025 14:35                          │
│                                                     │
│  🤖 Metadados Extraídos pela IA  ✨ NOVO!          │
│  ├─ Categoria: Procedimento                         │
│  ├─ Palavras-chave:                                 │
│  │   🏷️ higienização  🏷️ mãos  🏷️ UTI            │
│  ├─ Requisitos:                                     │
│  │   • Água corrente                                │
│  │   • Sabão líquido                                │
│  │   • Álcool 70%                                   │
│  ├─ Tempo de execução: 2 minutos                    │
│  └─ Nível: Baixo                                    │
│                                                     │
│  📝 Descrição                                       │
│  Procedimento padrão para higienização de mãos      │
│  em ambiente de UTI conforme protocolo ANVISA.      │
│                                                     │
│  📎 Arquivo Original                                │
│  POP_Higienizacao_v1.docx (125 KB)                 │
│  [📥 Download]                                      │
│                                                     │
│  📊 Timeline                                        │
│  ✅ 29/11 14:35 - Documento criado                  │
│  ✅ 29/11 14:35 - Processamento IA concluído        │
│  ⏳ Aguardando triagem UGQ                          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**🎉 Maria vê que:**
1. O documento foi salvo
2. A IA extraiu informações automaticamente
3. Palavras-chave foram identificadas
4. Requisitos foram listados
5. Tudo pronto para seguir o workflow!

---

## 🔄 Comparação: COM vs SEM Celery

### ❌ SEM Celery (Bloqueante)

```
┌──────────────────────────────────────────────┐
│  Maria clica em "Criar Documento"           │
└──────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────┐
│  Salvando arquivo... ⏳                      │  1s
└──────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────┐
│  Extraindo texto... ⏳                       │  3s
└──────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────┐
│  Analisando com IA... ⏳⏳⏳                  │  10s
│  (Maria esperando... 😴)                     │
└──────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────┐
│  Salvando metadados... ⏳                    │  1s
└──────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────┐
│  ✅ Documento criado!                        │
│  (Maria esperou 15 segundos! 😫)             │
└──────────────────────────────────────────────┘

⏱️ TEMPO TOTAL: 15 segundos bloqueados
😫 UX RUIM: Maria fica esperando
❌ SERVIDOR: Bloqueado para processar 1 documento
```

### ✅ COM Celery (Assíncrono)

```
┌──────────────────────────────────────────────┐
│  Maria clica em "Criar Documento"           │
└──────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────┐
│  Salvando arquivo... ⏳                      │  0.3s
│  Agendando processamento... ✅               │  0.2s
└──────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────┐
│  ✅ Documento criado!                        │
│  (Maria pode continuar! 😊)                  │
└──────────────────────────────────────────────┘

⏱️ TEMPO DE ESPERA: 0.5 segundos
😊 UX EXCELENTE: Maria continua trabalhando
✅ SERVIDOR: Livre para outros usuários

        ┌─────────────────────────┐
        │  BACKGROUND (Celery)    │
        │  ├─ Extraindo texto...  │  3s
        │  ├─ IA analisando...    │  10s
        │  ├─ Salvando...         │  1s
        │  └─ Email enviado ✅    │  1s
        └─────────────────────────┘
```

---

## 📊 Outros Exemplos de Uso

### 📧 Exemplo 2: Documento vencendo (Tarefa Agendada)

```
⏰ TODO DIA ÀS 9:00 DA MANHÃ (automático)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Celery Beat dispara:
└─ alertar_documentos_vencendo()

Worker verifica:
├─ Busca documentos vencendo em 30 dias
├─ Encontra 3 documentos
└─ Para cada documento:
    ├─ Calcula dias restantes
    └─ Agenda email:
        enviar_notificacao_email.delay(
          criador.id,
          "Documento vence em 25 dias",
          "O POP-123 vence em 25 dias. Revise!"
        )

Maria recebe email:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ Atenção: Documento vence em breve!

POP - Higienização de Mãos UTI
Vence em: 25 dias (24/12/2025)

Por favor, providencie a revisão do documento.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 💾 Exemplo 3: Backup automático

```
⏰ TODO DIA ÀS 3:00 DA MANHÃ (automático)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Celery Beat dispara:
└─ backup_banco_dados()

Worker executa:
├─ Cria backup PostgreSQL
│  pg_dump -U ged_user ged_db > ged_backup_2025-11-29.sql
│
├─ Backup salvo em /app/backups/
│  ├─ ged_backup_2025-11-29.sql (novo) ✅
│  ├─ ged_backup_2025-11-28.sql
│  ├─ ged_backup_2025-11-27.sql
│  └─ ...
│
└─ Remove backups antigos (>7 dias)
    ├─ ged_backup_2025-11-21.sql (deletado) ✗
    └─ Espaço liberado!

Ninguém percebe, mas o sistema está protegido! 🛡️
```

### 📊 Exemplo 4: Relatório pesado

```
José (Diretor) solicita relatório anual:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

José clica: [ Gerar Relatório Anual 2025 ]

Resposta imediata:
┌─────────────────────────────────────────┐
│ ✅ Relatório sendo gerado...            │
│                                         │
│ Você receberá um email quando estiver   │
│ pronto. Tempo estimado: 2-3 minutos.    │
└─────────────────────────────────────────┘

⏱️ José esperou: 0.5s
😊 José pode voltar ao trabalho!

Background (Celery Worker):
├─ Busca 12.543 documentos do ano
├─ Calcula estatísticas por setor
├─ Gera 45 gráficos
├─ Compila PDF de 87 páginas
└─ 2min30s depois...
    ├─ Salva PDF em /app/relatorios/
    └─ Envia email para José:
        "Seu relatório está pronto! 📊"

José baixa relatório completo! 🎉
```

---

## 🎯 Benefícios na Prática

### Para o USUÁRIO (Maria):
✅ **Resposta instantânea** - não espera processamento
✅ **Pode continuar trabalhando** - não fica bloqueada
✅ **Notificações** - recebe email quando concluir
✅ **Sistema sempre rápido** - mesmo com IA pesada

### Para o SISTEMA:
✅ **Escalabilidade** - processa 100 documentos em paralelo
✅ **Confiabilidade** - retry automático em caso de erro
✅ **Performance** - servidor não trava
✅ **Manutenção** - tarefas agendadas automáticas

### Para a EQUIPE TI:
✅ **Monitoramento** - Flower mostra tudo que está acontecendo
✅ **Logs detalhados** - rastreamento de erros
✅ **Fácil debug** - testar tarefas manualmente
✅ **Backups automáticos** - sem intervenção manual

---

## 📈 Visão do Monitoramento (Flower)

Acesse http://localhost:5555 (se habilitado):

```
┌────────────────────────────────────────────────────┐
│  🌺 Flower - Celery Monitoring                     │
├────────────────────────────────────────────────────┤
│                                                    │
│  📊 Dashboard                                      │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                    │
│  Workers: 1 online  ✅                             │
│  Tasks processed: 1,247                            │
│  Success rate: 98.5%                               │
│                                                    │
│  ⏳ Active Tasks (3)                               │
│  ├─ processar_documento_ia(doc_id=1234)   5s      │
│  ├─ gerar_relatorio_pdf(tipo='mensal')   45s      │
│  └─ enviar_notificacao_email(user=89)     2s      │
│                                                    │
│  ✅ Recently Completed (10)                        │
│  ├─ processar_documento_ia(1233)  SUCCESS  12s    │
│  ├─ backup_banco_dados()          SUCCESS  34s    │
│  ├─ limpar_logs_antigos()         SUCCESS  8s     │
│  └─ ...                                            │
│                                                    │
│  📅 Scheduled (Celery Beat)                        │
│  ├─ verificar_documentos_vencidos  02:00 daily    │
│  ├─ backup_banco_dados             03:00 daily    │
│  ├─ limpar_logs_antigos            04:00 weekly   │
│  └─ alertar_documentos_vencendo    09:00 daily    │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

## 🚀 Resumo

**Antes (sem Celery):**
- Maria espera 15 segundos ⏳
- Sistema trava para outros usuários ❌
- Sem notificações automáticas ❌
- Sem backups automáticos ❌

**Agora (com Celery):**
- Maria espera 0.5 segundos ⚡
- Sistema processa em background ✅
- Notificações automáticas ✅
- Backups diários automáticos ✅
- Relatórios não travam o sistema ✅
- IA processa sem impactar UX ✅

**Resultado: Sistema profissional, escalável e com UX excelente!** 🎉
