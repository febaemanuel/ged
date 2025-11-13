# Sistema GED - Gestão Eletrônica de Documentos

## 🎯 Sobre o Projeto

**Sistema completo e profissional** de Gestão Eletrônica de Documentos (GED) desenvolvido para instituições de saúde, especialmente hospitais e unidades de saúde que seguem o padrão **EBSERH** (Empresa Brasileira de Serviços Hospitalares).

### 🏥 Principais Características

- 📄 **Gestão Completa** de POPs, Manuais, Protocolos e Documentos Técnicos
- ✅ **Workflow EBSERH** - Fluxo de aprovação em 5 etapas obrigatórias
- 🔄 **Automação Inteligente** - Criação automática de tarefas sequenciais
- 🤖 **IA Integrada** - DeepSeek AI para extração, classificação e sumarização
- 📊 **Relatórios PDF** - Geração automática de relatórios gerenciais
- 🎨 **Interface Moderna** - Frontend completo com Bootstrap 5
- 🔐 **Controle de Acesso** - Sistema de perfis e permissões robusto

## 🔄 Workflow EBSERH-UGQ (Centralizado na Qualidade)

O sistema implementa o **fluxo oficial EBSERH centralizado na Unidade de Gestão da Qualidade (UGQ)**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│              FLUXO OFICIAL EBSERH - CENTRALIZADO NA UGQ                 │
│          (Baseado em FLX.UGQ-CHUFC.002 e POPs da Qualidade)            │
└─────────────────────────────────────────────────────────────────────────┘

0️⃣ AUTOR (Usuário Comum)
   └─> Cria documento e clica "Submeter para Análise da Qualidade"
       ⏱️ Sistema cria tarefa "Documento Recebido" → QUALIDADE (Triador)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                        🏢 UNIDADE DE GESTÃO DA QUALIDADE (UGQ)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ QUALIDADE (Triador) - Recebimento e Triagem
   └─> Checkpoint 1: Documento já existe?
       ├─ SIM → Devolve ao Autor (Processo Encerrado)
       └─ NÃO → Avança
   └─> Checkpoint 2: É Manual?
       ├─ SIM → Validado pelo Colegiado Executivo?
       │   ├─ NÃO → Devolve ao Autor (Processo Encerrado)
       │   └─ SIM → Avança
       └─ NÃO → Avança automaticamente
   └─> Checkpoint 3: Está no padrão de formatação?
       ├─ NÃO → Devolve ao Autor (Processo Encerrado)
       └─ SIM → Clica "Aprovar Triagem e Enviar para Validação"

   🔄 HAND-OFF (Transferência de Responsabilidade)
       ⏱️ Sistema cria tarefa "Validar e Codificar" → QUALIDADE (Validador)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2️⃣ QUALIDADE (Validador) - Codificação e Validação
   └─> Formatar documento (ajuste fino se necessário)
   └─> Codificar: Gerar código definitivo (ex: POP.SETOR-XYZ.001)
   └─> Atualizar Lista Mestra do sistema
   └─> Validar: Assinar Declaração SEI de VALIDAÇÃO
   └─> Clica "Documento Codificado e Validado. Iniciar Bloco de Assinatura"
       ⏱️ Sistema abre tela "Gestão do Bloco de Assinatura"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3️⃣ QUALIDADE (Validador) - Gestão do Bloco de Assinatura
   └─> Preparar Processo: Anexa PDF final codificado
   └─> Selecionar Aprovadores em ordem (ex: Chefe → Superintendente)
   └─> Iniciar Fluxo de Assinatura (Sequencial ou Concomitante):

       MODO SEQUENCIAL:
       ├─> Aprovador 1 recebe tarefa
       │   ├─ Reprovar → Volta para Validador com ajustes
       │   └─ Aprovar → Sistema cria tarefa para Aprovador 2
       └─> Repete até último aprovador

       MODO CONCOMITANTE (Paralelo):
       ├─> Todos aprovadores recebem tarefa simultaneamente
       ├─ Qualquer Reprovação → Volta para Validador com ajustes
       └─ Todos Aprovam → Sistema registra bloco como "Aprovado"

       ⏱️ Sistema cria tarefa "Publicar Documento" → QUALIDADE (Validador)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4️⃣ QUALIDADE (Validador) - Publicação Final
   └─> Move documento para status "VIGENTE"
   └─> Arquiva versão anterior como "ANTIGO"
   └─> Publica no Portal da instituição
   └─> Marca processo como "Concluído"
       ✅ FIM DO PROCESSO

```

**Características do Workflow UGQ:**
- ✅ **Centralização Total** - Toda gestão concentrada na UGQ
- 👥 **2 Perfis Especializados** - Triador (triagem) e Validador (técnico)
- 🔄 **Hand-Off Inteligente** - Transferência automática entre perfis
- ✓ **3 Checkpoints Obrigatórios** - Triagem rigorosa conforme POPs
- 📝 **Lista Mestra Integrada** - Codificação automática sequencial
- 📋 **Bloco de Assinatura Flexível** - Modo sequencial ou concomitante
- 🔙 **Devolução ao Autor** - Processo pode retornar em qualquer etapa
- 📊 **Rastreabilidade Total** - Histórico completo UGQ-centric

## 🚀 Stack Tecnológica

### Backend
- **Python 3.11+** - Linguagem principal
- **Flask 3.0** - Framework web moderno
- **PostgreSQL 12+** - Banco de dados robusto
- **SQLAlchemy** - ORM para modelagem
- **Flask-Login** - Autenticação e sessões
- **ReportLab** - Geração de PDFs
- **DeepSeek AI** - Processamento de linguagem natural

### Frontend
- **Bootstrap 5.3** - Framework CSS responsivo
- **Bootstrap Icons 1.11** - Ícones vetoriais
- **JavaScript ES6+** - Interatividade moderna
- **Jinja2 Templates** - Renderização server-side

## 📦 Instalação Rápida

### 🐧 Linux / macOS

#### 1. Pré-requisitos
```bash
python3 --version  # Requer 3.11+
psql --version     # Requer PostgreSQL 12+
```

#### 2. Setup PostgreSQL
```sql
sudo -u postgres psql
CREATE DATABASE ged_db;
CREATE USER ged_user WITH PASSWORD 'ged_password';
GRANT ALL PRIVILEGES ON DATABASE ged_db TO ged_user;
\q
```

#### 3. Instalação Automática
```bash
git clone <repository-url>
cd ged
./setup.sh
source venv/bin/activate
cp .env.example .env  # Configure aqui
```

#### 4. Configurar `.env`
```env
DATABASE_URL=postgresql://ged_user:ged_password@localhost/ged_db
SECRET_KEY=sua-chave-secreta-aqui
AI_API_BASE_URL=https://api.deepseek.com
AI_API_KEY=sua-chave-deepseek-aqui
```

#### 5. Inicializar Banco
```bash
python init_database.py  # Cria tabelas + 10 usuários
# OU
flask init-db && flask seed-db
```

#### 6. Executar
```bash
python app.py
```

### 🪟 Windows

#### 1. Instalar Dependências
```cmd
python --version  # Requer 3.11+
```

#### 2. Setup PostgreSQL
```cmd
psql -U postgres
CREATE DATABASE ged_db;
CREATE USER ged_user WITH PASSWORD 'ged_password';
GRANT ALL PRIVILEGES ON DATABASE ged_db TO ged_user;
\q
```

#### 3. Instalação
```cmd
git clone <repository-url>
cd ged
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
copy .env.example .env
```

Edite `.env` com suas credenciais.

#### 4. Inicializar Banco
```cmd
python init_database.py
```

#### 5. Executar
```cmd
python app.py
```

---

✅ **Acesse**: http://localhost:5000

## 🔑 Usuários Padrão (Workflow UGQ)

O sistema cria automaticamente usuários para testar o **workflow centralizado UGQ**:

### ⚪ Autores (Usuários Comuns)
| Email | Senha | Perfil | Setor | Função no Workflow |
|-------|-------|--------|-------|-------------------|
| usuario@example.com | usuario123 | Comum | Operações | Cria documentos e submete para UGQ |
| rafael.alves@example.com | usuario123 | Comum | Produção | Cria documentos e submete para UGQ |
| fernanda.lima@example.com | usuario123 | Comum | Operações | Cria documentos e submete para UGQ |

### 🟡 UGQ - Triadores (ETAPA 1)
| Email | Senha | Perfil | Setor | Função no Workflow |
|-------|-------|--------|-------|-------------------|
| triador.ugq@example.com | ugq123 | Qualidade (Triador) | UGQ | Recebe e triagem: verifica duplicatas, validação colegiado, formatação |

### 🟢 UGQ - Validadores (ETAPAS 2, 3, 4)
| Email | Senha | Perfil | Setor | Função no Workflow |
|-------|-------|--------|-------|-------------------|
| validador.ugq@example.com | ugq123 | Qualidade (Validador) | UGQ | Codifica, valida, gerencia bloco de assinatura e publica |

### 🔵 Aprovadores (ETAPA 3 - Bloco de Assinatura)
| Email | Senha | Perfil | Setor | Função no Workflow |
|-------|-------|--------|-------|-------------------|
| maria.silva@example.com | gerente123 | Gerente | Produção | Assina documentos no bloco de assinatura |
| joao.santos@example.com | gerente123 | Gerente | Qualidade | Assina documentos no bloco de assinatura |
| carlos.mendes@example.com | gerente123 | Gerente | Operações | Assina documentos no bloco de assinatura |

### 🔴 Administrador do Sistema
| Email | Senha | Perfil | Setor | Função no Workflow |
|-------|-------|--------|-------|-------------------|
| admin@example.com | admin123 | Administrador | TI | Gerenciar sistema, usuários e configurações |

## 🌐 Arquitetura da API

### Blueprints Implementados (6)

```
app/routes/
├── routes_auth.py         # Autenticação e login
├── routes_documento.py    # CRUD de documentos
├── routes_tarefa.py       # CRUD de tarefas
├── routes_ia.py           # Integração DeepSeek AI
├── routes_dashboard.py    # Dashboard e relatórios PDF
└── routes_view.py         # Frontend HTML (25 rotas)
```

### Endpoints Principais

#### Autenticação
```bash
POST /auth/login           # Login
GET  /auth/me              # Dados do usuário
POST /auth/logout          # Logout
```

#### Documentos (CRUD Completo)
```bash
GET  /documento/lista      # Listar todos
POST /documento/criar      # Criar novo
GET  /documento/<id>       # Detalhes
PUT  /documento/<id>       # Atualizar
DELETE /documento/<id>     # Deletar
GET  /documento/publico    # Repositório público
```

#### Tarefas (Sistema de Workflow)
```bash
GET  /tarefa/minhas        # Minhas tarefas
POST /tarefa/criar         # Criar tarefa
GET  /tarefa/<id>          # Detalhes
POST /tarefa/<id>/concluir # Concluir (⏱️ cria próxima automaticamente)
```

#### Inteligência Artificial (DeepSeek)
```bash
POST /ia/extract/<id>      # Extrair texto do documento
POST /ia/classify/<id>     # Classificar categoria
POST /ia/summarize/<id>    # Gerar resumo
POST /ia/search            # Busca semântica
```

#### Relatórios PDF
```bash
GET /relatorio/pdf/tarefas_atrasadas  # PDF tarefas atrasadas
GET /relatorio/pdf/documentos_vencer  # PDF docs vencendo
GET /relatorio/pdf/geral              # PDF relatório geral
```

**Total: 42 endpoints** | Documentação completa: http://localhost:5000/home

## 📊 Funcionalidades Detalhadas

### 📄 Gestão de Documentos

- ✅ **CRUD Completo** - Criar, ler, editar, deletar
- ✅ **Upload de Arquivos** - Suporte a .doc, .docx, .odt, .pdf
- ✅ **Códigos Automáticos** - Provisório e definitivo
- ✅ **Classificação** - POPs, Manuais, Protocolos, Formulários
- ✅ **Controle de Versão** - Histórico de alterações
- ✅ **Controle de Vencimento** - Alertas automáticos
- ✅ **Validação de IA** - Classificação e extração automática
- ✅ **Filtros Avançados** - Por status, setor, tipo, data
- ✅ **Timeline de Atividades** - Histórico visual completo

### ✅ Sistema de Tarefas e Workflow

- ✅ **Workflow EBSERH** - 5 etapas automáticas obrigatórias
- ✅ **Criação Automática** - Próxima tarefa criada ao aprovar
- ✅ **6 Tipos de Tarefa**:
  - **Analisar** (Chefia Imediata)
  - **Validar Conteúdo** (Área Técnica)
  - **Validar Padronização** (Qualidade)
  - **Aprovar** (Superintendência)
  - **Publicar** (Gestão Documental)
  - **Realizar Correção** (Autor - se reprovado)
- ✅ **Prazos e Alertas** - Notificações de atraso
- ✅ **Pareceres Detalhados** - Registro de aprovação/rejeição
- ✅ **Atribuição Inteligente** - Responsável baseado em perfil e setor
- ✅ **Dashboard de Tarefas** - Visão completa pendentes/atrasadas

### 🤖 Inteligência Artificial (DeepSeek)

- ✅ **Extração de Texto** - OCR e processamento de documentos
- ✅ **Classificação Automática** - Identifica tipo de documento
- ✅ **Sumarização** - Resume documentos longos
- ✅ **Busca Semântica** - Pesquisa por significado
- ✅ **Análise de Conteúdo** - 8000 caracteres por vez
- ✅ **Logs de Auditoria** - Todas chamadas registradas
- ✅ **Tratamento de Erros** - Fallback e retry automático

### 📊 Relatórios e Dashboard

- ✅ **Dashboard Interativo** - Estatísticas em tempo real
- ✅ **Gráficos Visuais** - Documentos, tarefas, setores
- ✅ **Relatórios PDF Profissionais**:
  - Tarefas atrasadas por setor
  - Documentos vencendo (30, 60, 90 dias)
  - Relatório geral do sistema
- ✅ **Exportação** - PDF gerado com ReportLab

### 🔐 Controle de Acesso e Permissões

#### Perfis de Usuário

| Perfil | Permissões |
|--------|------------|
| **Comum** | Criar documentos, visualizar próprios documentos, concluir tarefas atribuídas |
| **Responsável Interno** | + Validar conteúdo técnico, validar padronização |
| **Gerente** | + Analisar documentos, aprovar final, acessar IA, ver relatórios |
| **Administrador** | Acesso total, gerenciar usuários, publicar documentos |

#### Regras de Negócio

- ✅ **Documento só editável** pelo criador (rascunho) ou admin
- ✅ **Tarefa só concluída** pelo responsável ou admin
- ✅ **Workflow obrigatório** - Não pode pular etapas
- ✅ **Setor específico** - Responsáveis do mesmo setor validam conteúdo

## 📁 Estrutura do Projeto

```
ged/
├── app.py                          # Ponto de entrada
├── config.py                       # Configurações
├── init_database.py                # Script de inicialização
├── aplicar_migracao.py             # Script de migração
├── WORKFLOW_SETUP.md               # Doc do workflow
│
├── app/
│   ├── __init__.py                 # Factory do Flask
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py               # 4 modelos (Usuario, Documento, Tarefa, LogAI)
│   │
│   ├── routes/                     # 6 Blueprints
│   │   ├── __init__.py
│   │   ├── routes_auth.py          # Autenticação
│   │   ├── routes_documento.py     # API Documentos
│   │   ├── routes_tarefa.py        # API Tarefas
│   │   ├── routes_ia.py            # API IA
│   │   ├── routes_dashboard.py     # API Dashboard/PDF
│   │   └── routes_view.py          # Frontend (25 rotas)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_client.py            # Cliente DeepSeek AI
│   │   ├── pdf_generator.py        # Geração de PDFs
│   │   └── workflow.py             # Motor de workflow EBSERH
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css           # 330 linhas CSS customizado
│   │   └── js/
│   │       └── main.js             # 470 linhas JavaScript
│   │
│   ├── templates/                  # 12 Templates HTML
│   │   ├── base.html               # Template base
│   │   ├── login.html              # Página de login
│   │   ├── dashboard.html          # Dashboard principal
│   │   ├── documentos.html         # Lista de documentos
│   │   ├── documento_criar.html    # Criar documento
│   │   ├── documento_detalhe.html  # Detalhes + timeline
│   │   ├── documento_editar.html   # Editar documento
│   │   ├── tarefas.html            # Lista de tarefas
│   │   ├── tarefa_criar.html       # Criar tarefa
│   │   ├── tarefa_detalhe.html     # Detalhes + concluir
│   │   ├── usuarios.html           # Gerenciar usuários
│   │   ├── perfil.html             # Perfil do usuário
│   │   └── repositorio_publico.html # Docs publicados
│   │
│   └── uploads/
│       ├── documentos/             # Arquivos originais
│       └── publicados/             # PDFs finais
│
├── migrations/
│   └── add_chefia_imediata_workflow.sql
│
├── logs/
│   └── ged.log                     # Logs da aplicação
│
├── venv/                           # Ambiente virtual
├── requirements.txt                # Dependências Python
├── .env.example                    # Template de configuração
├── .gitignore
└── README.md                       # Este arquivo
```

## 🎨 Interface do Usuário

### Páginas Implementadas (12 Templates)

1. **🔐 Login** - Autenticação segura com flash messages
2. **📊 Dashboard** - Visão geral com:
   - Estatísticas (docs, tarefas, atrasadas)
   - Tarefas pendentes
   - Ações rápidas
   - Atalhos principais
3. **📄 Documentos**:
   - Lista com filtros (status, setor, tipo)
   - Criar novo (com seleção de chefia)
   - Editar existente
   - Detalhes completos + timeline
4. **✅ Tarefas**:
   - Lista com filtros (tipo, prioridade, status)
   - Criar manual
   - Detalhes + formulário de conclusão
   - Estatísticas (pendentes, atrasadas, concluídas)
5. **👥 Usuários** - Gerenciamento (apenas Admin)
6. **👤 Perfil** - Dados pessoais + alterar senha
7. **🌐 Repositório Público** - Documentos publicados

### Recursos Frontend

- ✅ **Design Responsivo** - Mobile, tablet, desktop
- ✅ **Bootstrap 5.3** - Framework CSS moderno
- ✅ **Bootstrap Icons** - 200+ ícones vetoriais
- ✅ **JavaScript Vanilla** - Sem dependências extras
- ✅ **Validação de Formulários** - Client-side + server-side
- ✅ **Flash Messages** - Feedback visual de ações
- ✅ **Upload de Arquivos** - Interface intuitiva
- ✅ **Filtros Dinâmicos** - Pesquisa em tempo real
- ✅ **Paginação** - Navegação eficiente
- ✅ **Tooltips e Modals** - Interações modernas

## 🔧 Comandos Úteis

```bash
# Desenvolvimento
python app.py                   # Executar servidor de desenvolvimento
flask shell                     # Console Python interativo
tail -f logs/ged.log            # Ver logs em tempo real

# Banco de Dados
python init_database.py         # Inicializar com 10 usuários
flask init-db                   # Criar tabelas
flask seed-db                   # Popular dados exemplo
python aplicar_migracao.py      # Aplicar migração workflow

# Manutenção
flask verificar-vencimentos     # Rotina de vencimentos
python test_api.py              # Testar endpoints

# Produção
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🧪 Testando o Sistema

### Teste Manual do Workflow UGQ (Centralizado)

**ETAPA 0: Autor Submete Documento**

1. **Login como Autor** (`usuario@example.com` / `usuario123`)
   - Clicar em "Novo Documento"
   - Preencher: Título, Tipo (POP/Manual/Protocolo), Setor
   - Fazer upload do arquivo (.doc, .docx, .odt)
   - Clicar em **"Submeter para Análise da Qualidade"**
   - ✅ Sistema cria tarefa "Documento Recebido" → `triador.ugq@example.com`

---

**ETAPA 1: UGQ Triador Faz Triagem**

2. **Login como Triador UGQ** (`triador.ugq@example.com` / `ugq123`)
   - Ver tarefa "Documento Recebido" na dashboard
   - Abrir tarefa e executar **3 checkpoints**:

   - **Checkpoint 1:** Documento já existe?
     - Consultar Lista Mestra
     - Se SIM → Clicar "Devolver ao Autor" (processo encerra)
     - Se NÃO → Avançar

   - **Checkpoint 2:** É Manual?
     - Se SIM → Perguntar: "Foi validado pelo Colegiado Executivo?"
       - Se NÃO → Clicar "Devolver ao Autor" (processo encerra)
       - Se SIM → Avançar
     - Se NÃO → Avançar automaticamente

   - **Checkpoint 3:** Está no padrão de formatação?
     - Verificar margens, fontes, cabeçalhos
     - Se NÃO → Clicar "Devolver ao Autor" (processo encerra)
     - Se SIM → Clicar **"Aprovar Triagem e Enviar para Validação"**

   - ✅ Sistema cria tarefa "Validar e Codificar" → `validador.ugq@example.com`

---

**ETAPA 2: UGQ Validador Codifica e Valida**

3. **Login como Validador UGQ** (`validador.ugq@example.com` / `ugq123`)
   - Ver tarefa "Validar e Codificar" na dashboard
   - Abrir tarefa e executar:

   - **Formatar:** Fazer ajustes finais de formatação (se necessário)
   - **Codificar:** Acessar "Lista Mestra", verificar último código, gerar novo
     - Exemplo: `POP.OPERACOES-XYZ.001` v1.0
   - **Atualizar Lista Mestra:** Inserir nova linha no sistema
   - **Validar:** Assinar Declaração SEI de VALIDAÇÃO
   - Clicar **"Documento Codificado e Validado. Iniciar Bloco de Assinatura"**

   - ✅ Sistema abre tela "Gestão do Bloco de Assinatura"

---

**ETAPA 3: UGQ Validador Gerencia Bloco de Assinatura**

4. **Ainda como Validador UGQ** (mesma sessão)
   - Tela de "Gestão do Bloco de Assinatura":

   - **Preparar Processo:** Anexar PDF final codificado
   - **Selecionar Aprovadores:** Adicionar em ordem:
     1. Carlos Mendes (Chefe Operações)
     2. Maria Silva (Superintendente)
   - **Escolher Modo:** Sequencial ou Concomitante
   - Clicar **"Iniciar Bloco de Assinatura"**

   - ✅ Sistema cria tarefas para os aprovadores

---

**ETAPA 3.1: Aprovadores Assinam**

5. **Login como Carlos Mendes** (`carlos.mendes@example.com` / `gerente123`)
   - Ver tarefa "Assinar Documento" na dashboard
   - Abrir documento PDF codificado
   - Decisão:
     - Se **Reprovar** → Sistema devolve para Validador UGQ com ajustes
     - Se **Aprovar** → Sistema registra assinatura e avança

6. **Login como Maria Silva** (`maria.silva@example.com` / `gerente123`)
   - Ver tarefa "Assinar Documento" (se modo sequencial)
   - Abrir e aprovar
   - ✅ Sistema cria tarefa "Publicar Documento" → `validador.ugq@example.com`

---

**ETAPA 4: UGQ Validador Publica**

7. **Login como Validador UGQ** (`validador.ugq@example.com` / `ugq123`)
   - Ver tarefa "Publicar Documento Aprovado"
   - Executar ações de publicação:
     - Move para status "VIGENTE"
     - Arquiva versão anterior (se houver) como "ANTIGO"
     - Publica no Portal da instituição
   - Clicar **"Marcar Processo como Concluído"**

   - ✅ **FIM DO PROCESSO**
   - Documento aparece no Repositório Público com código definitivo

### Teste da API com cURL

```bash
# Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","senha":"admin123"}' \
  -c cookies.txt

# Listar documentos
curl -X GET http://localhost:5000/documento/lista -b cookies.txt

# Minhas tarefas
curl -X GET http://localhost:5000/tarefa/minhas -b cookies.txt

# Classificar documento com IA
curl -X POST http://localhost:5000/ia/classify/1 -b cookies.txt

# Gerar relatório PDF
curl -X GET http://localhost:5000/relatorio/pdf/geral -b cookies.txt > relatorio.pdf
```

### Teste Automatizado

```bash
python test_api.py
```

## 🐳 Deploy em Produção

### Com Gunicorn (Recomendado)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app
```

### Com Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/ged/app/static;
    }
}
```

## 🐛 Solução de Problemas

### ModuleNotFoundError
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate.bat  # Windows
pip install -r requirements.txt
```

### Erro de Conexão com Banco
```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql  # Linux
# OU
pg_ctl status  # Windows

# Verificar credenciais no .env
cat .env | grep DATABASE
```

### Porta 5000 em uso
```bash
# Linux/Mac
lsof -ti:5000 | xargs kill -9

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Workflow não cria próxima tarefa
- Verificar logs em `logs/ged.log`
- Verificar se usuários com perfil correto existem
- Verificar se `chefia_imediata_id` está preenchido
- Ver prints no console com `[WORKFLOW]`

### DeepSeek AI não funciona
- Verificar `AI_API_KEY` no `.env`
- Verificar saldo da conta DeepSeek
- Ver logs de erro detalhados no console

## 📊 Estatísticas do Projeto

```
Backend:
  📄 Arquivos Python: 18
  📝 Linhas de código: ~7.500
  🌐 API Endpoints: 42
  🗂️ Modelos de dados: 4
  📦 Blueprints: 6
  ⚙️ Serviços: 3 (IA, PDF, Workflow)

Frontend:
  🎨 Templates HTML: 12
  💅 CSS: 330 linhas
  ⚡ JavaScript: 470 linhas
  🖼️ Componentes: 50+
  🌐 Rotas VIEW: 25

Database:
  📊 Tabelas: 4
  👥 Usuários padrão: 10
  🔗 Relacionamentos: 8

Total: ~10.000 linhas de código
```

## 📚 Documentação Adicional

- **WORKFLOW_SETUP.md** - Guia completo do workflow EBSERH
- **Documentação API** - http://localhost:5000/home (após executar)

## 🤝 Contribuindo

Este é um sistema completo e funcional. Para contribuir:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é proprietário. Todos os direitos reservados.

## ✨ Tecnologias e Conceitos Aplicados

- ✅ **Clean Architecture** - Separação de camadas
- ✅ **RESTful API** - Endpoints padronizados
- ✅ **ORM Pattern** - SQLAlchemy
- ✅ **Factory Pattern** - create_app()
- ✅ **Blueprint Pattern** - Modularização
- ✅ **Service Layer** - Lógica de negócio isolada
- ✅ **Template Inheritance** - DRY em templates
- ✅ **Session Management** - Flask-Login
- ✅ **Error Handling** - Try-except robusto
- ✅ **Logging** - Sistema de logs completo
- ✅ **Environment Variables** - Configuração segura
- ✅ **SQL Migrations** - Versionamento de DB

---

**Sistema GED EBSERH** | Workflow Automático | Integração IA | Python 3.11 | Flask 3.0 | PostgreSQL | Bootstrap 5

Desenvolvido para instituições de saúde que seguem o padrão EBSERH.
