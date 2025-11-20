# 📱 Sistema GED EBSERH - Gestão Eletrônica de Documentos

> **Sistema completo e profissional** de Gestão Eletrônica de Documentos para instituições de saúde seguindo padrão EBSERH

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12%2B-blue)](https://postgresql.org)
[![Evolution API](https://img.shields.io/badge/WhatsApp-Evolution%20API-brightgreen)](https://github.com/EvolutionAPI/evolution-api)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Índice

1. [Sobre o Projeto](#-sobre-o-projeto)
2. [Funcionalidades](#-funcionalidades-principais)
3. [Workflow EBSERH-UGQ](#-workflow-ebserh-ugq)
4. [Instalação Rápida](#-instalação-rápida)
5. [WhatsApp (Evolution API)](#-whatsapp-evolution-api)
6. [Stack Tecnológico](#-stack-tecnológico)
7. [Estrutura do Projeto](#-estrutura-do-projeto)
8. [Segurança](#-segurança)
9. [Documentação Completa](#-documentação-adicional)
10. [Licença](#-licença)

---

## 🎯 Sobre o Projeto

Sistema de **Gestão Eletrônica de Documentos (GED)** desenvolvido para instituições de saúde, especialmente hospitais e unidades que seguem o padrão **EBSERH** (Empresa Brasileira de Serviços Hospitalares).

### 🏥 Casos de Uso

- **POPs** (Procedimentos Operacionais Padrão)
- **Manuais** (Administrativos, Técnicos, Clínicos)
- **Protocolos** (Clínicos, Assistenciais)
- **Políticas** Institucionais
- **Regimentos** e Regulamentos
- **Normas** Técnicas

---

## ✨ Funcionalidades Principais

### 📄 Gestão de Documentos

- ✅ **CRUD Completo** - Criar, editar, visualizar, deletar documentos
- 📝 **Versionamento** - Controle completo de versões com histórico
- 🔍 **Busca Avançada** - Por título, código, tipo, setor, status
- 📊 **Metadata Rica** - Campos customizáveis por tipo de documento
- 📁 **Upload de Arquivos** - DOCX, PDF, ODT (max 16MB)
- 🏷️ **Codificação Automática** - Geração de códigos sequenciais por tipo/setor
- ⏰ **Controle de Validade** - Alertas automáticos de vencimento

### 🔄 Workflow EBSERH-UGQ

- ✅ **5 Etapas Obrigatórias** - Fluxo completo centralizado na Qualidade
- 👥 **6 Perfis de Usuário** - Comum, Gerente, Admin, Triador UGQ, Validador UGQ
- 🔄 **Automação Total** - Criação automática de tarefas sequenciais
- ✓ **3 Checkpoints** - Triagem rigorosa conforme POPs da Qualidade
- 📋 **Blocos de Assinatura** - Modo sequencial ou concomitante
- 📝 **Lista Mestra** - Controle centralizado de códigos publicados
- 🔙 **Devolução ao Autor** - Processo pode retornar em qualquer etapa

### 🤖 Inteligência Artificial

- 🧠 **DeepSeek AI** - Modelo de linguagem avançado
- 📄 **Extração de Texto** - OCR de PDFs e documentos escaneados
- 📊 **Classificação Automática** - Sugestão de tipo, setor, categoria
- 📝 **Sumarização** - Resumos automáticos de documentos longos
- 🏷️ **Metadados Inteligentes** - Extração automática de informações

### 📱 WhatsApp (Evolution API)

- ✅ **100% Gratuito** - Open-source, sem custos por mensagem
- 💬 **Chatbot Conversacional** - Menu interativo para assinatura
- ✍️ **Assinatura Digital** - Aprovação via WhatsApp com hash SHA256
- 🔔 **Notificações** - Tarefas novas, prazos, aprovações
- 🔒 **Segurança** - 2FA, timeout, bloqueio por tentativas
- ⏰ **Horários** - Configurável (seg-sex, 08:00-18:00)
- 📊 **Auditoria** - Log completo de todas as mensagens

### 📊 Dashboards e Relatórios

- 📈 **Dashboard Geral** - Visão geral do sistema (todos setores)
- 🏥 **Dashboard por Setor** - Métricas específicas de cada área
- 👔 **Dashboard Executivo** - KPIs para diretoria
- 📊 **Gráficos Interativos** - Chart.js com dados em tempo real
- 📄 **Relatórios PDF** - Geração automática com ReportLab
- 📧 **Export** - Excel, CSV, JSON

### 🔐 Segurança

- 🔒 **Autenticação** - Flask-Login com hashing bcrypt
- 🛡️ **Autorização** - Controle de acesso baseado em perfis
- 🔑 **CSRF Protection** - Proteção contra ataques CSRF
- ⚡ **Rate Limiting** - Proteção contra força bruta
- 📝 **Auditoria** - Log completo de ações críticas
- 🔐 **SQL Injection** - Prevenção via ORM SQLAlchemy
- 🚫 **XSS Protection** - Auto-escape de templates Jinja2

---

## 🔄 Workflow EBSERH-UGQ

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
       ├─ SIM → Devolve ao Autor
       └─ NÃO → Avança
   └─> Checkpoint 2: É Manual? Validado pelo Colegiado?
       ├─ NÃO Validado → Devolve ao Autor
       └─ Validado → Avança
   └─> Checkpoint 3: Está no padrão de formatação?
       ├─ NÃO → Devolve ao Autor
       └─ SIM → "Aprovar Triagem e Enviar para Validação"

   🔄 Sistema cria tarefa "Validar e Codificar" → QUALIDADE (Validador)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2️⃣ QUALIDADE (Validador) - Codificação e Validação
   └─> Formatar documento
   └─> Codificar: Gerar código definitivo (ex: POP.SETOR-001)
   └─> Atualizar Lista Mestra
   └─> Assinar Declaração SEI de VALIDAÇÃO
   └─> "Iniciar Bloco de Assinatura"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3️⃣ QUALIDADE (Validador) - Gestão do Bloco de Assinatura
   └─> Anexa PDF final codificado
   └─> Seleciona aprovadores (ex: Chefe → Superintendente)
   └─> Define modo: SEQUENCIAL ou CONCOMITANTE

       SEQUENCIAL: Aprovador 1 → Aprovador 2 → ... → Último
       CONCOMITANTE: Todos recebem simultaneamente

   🔄 Sistema cria tarefa "Publicar Documento" → QUALIDADE (Validador)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4️⃣ QUALIDADE (Validador) - Publicação Final
   └─> Move documento para status "VIGENTE"
   └─> Arquiva versão anterior como "ANTIGO"
   └─> Publica no Portal institucional
   └─> Marca processo como "Concluído"
       ✅ FIM DO PROCESSO
```

---

## 🚀 Instalação Rápida

### 1. Pré-requisitos

- Python 3.8+
- PostgreSQL 12+
- Git

### 2. Clone o Repositório

```bash
git clone https://github.com/febaemanuel/ged.git
cd ged
```

### 3. Crie Ambiente Virtual

```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 4. Instale Dependências

```bash
pip install -r requirements.txt
```

### 5. Configure Variáveis de Ambiente

```bash
cp .env.example .env
nano .env
```

**Configurações mínimas:**

```bash
# Flask
SECRET_KEY=sua-chave-secreta-super-forte-aqui

# PostgreSQL
DATABASE_URL=postgresql://ged_user:ged_password@localhost:5432/ged_db?client_encoding=utf8

# Email (Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-aplicativo

# DeepSeek AI (opcional)
AI_API_BASE_URL=https://api.deepseek.com
AI_API_KEY=sk-sua-chave-aqui
```

### 6. Crie o Banco de Dados

```bash
# Crie o banco PostgreSQL
createdb ged_db

# Inicialize tabelas e usuários padrão
python init_database.py
```

**Usuários criados automaticamente:**

| Email | Senha | Perfil |
|-------|-------|--------|
| admin@example.com | admin123 | Administrador |
| triador.ugq@example.com | ugq123 | Triador UGQ |
| validador.ugq@example.com | ugq123 | Validador UGQ |

### 7. Inicie o Sistema

```bash
python app.py
```

Acesse: **http://localhost:5000**

---

## 📱 WhatsApp (Evolution API)

Sistema utiliza **Evolution API** (open-source, gratuita, sem burocracia).

> ⚠️ **Nota:** Twilio foi **descontinuado** neste projeto. Use apenas Evolution API.

### Vantagens da Evolution API

| Critério | Valor |
|----------|-------|
| **Custo** | ✅ Gratuito (sem custos por mensagem) |
| **Aprovação** | ✅ Instantânea (sem burocracia) |
| **Multi-instância** | ✅ Ilimitadas (vários números WhatsApp) |
| **Hospedagem** | ✅ Própria (controle total) |
| **Código** | ✅ Open Source |
| **Banco de Dados** | ⚠️ Separado (`evolution_db`) |

### Instalação Evolution API (Docker)

```bash
docker run -d \
  --name evolution-api \
  -p 8080:8080 \
  -e AUTHENTICATION_API_KEY=sua-chave-super-secreta \
  atendai/evolution-api:latest
```

### Configuração no Sistema GED

1. Acesse: `http://localhost:5000/admin/whatsapp`
2. Preencha:
   - **URL Evolution API**: `http://localhost:8080`
   - **Nome da Instância**: `ged_ebserh`
   - **API Key**: `sua-chave-super-secreta`
3. Marque **Ativo** ✅
4. Clique **"Obter QR Code"**
5. Escaneie com WhatsApp (Aparelhos conectados)

### Funcionalidades WhatsApp

- ✅ **Chatbot conversacional** com menu interativo
- ✅ **Assinatura digital** de documentos via WhatsApp
- ✅ **Notificações** de tarefas novas
- ✅ **Segurança**: timeout, bloqueio, validação email
- ✅ **Auditoria**: log completo de mensagens

**Comandos do Chatbot:**

- `menu` - Ver documentos pendentes de assinatura
- `ajuda` - Ver comandos disponíveis
- `1`, `2`, `3`... - Escolher documento pelo número

**Documentação completa:** [GUIA_EVOLUTION_API.md](GUIA_EVOLUTION_API.md)

---

## 🛠️ Stack Tecnológico

### Backend

- **Python 3.8+**
- **Flask 3.0** - Web framework
- **SQLAlchemy 2.0** - ORM
- **PostgreSQL 12+** - Banco de dados
- **Flask-Login** - Autenticação
- **Flask-Mail** - Email
- **Werkzeug** - Hashing de senhas

### Frontend

- **Bootstrap 5** - Framework CSS
- **Jinja2** - Template engine
- **JavaScript** (Vanilla)
- **Chart.js** - Gráficos
- **Font Awesome** - Ícones

### Integrações

- **DeepSeek AI** - IA para análise de documentos
- **Evolution API** - WhatsApp (open-source)
- **ReportLab** - Geração de PDFs
- **python-docx** - Processamento DOCX

### Dependências Principais

```
Flask==3.0.0
SQLAlchemy==2.0.23
psycopg2-binary==2.9.9
Flask-Login==0.6.3
Flask-Mail==0.10.0
Flask-WTF==1.2.1
Flask-Limiter==3.5.0
openai==1.12.0 (DeepSeek compatible)
reportlab==4.0.7
python-docx==1.1.0
requests==2.31.0
```

---

## 📁 Estrutura do Projeto

```
ged/
├── app/
│   ├── __init__.py                 # Factory do Flask
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py              # Modelos SQLAlchemy (1600 linhas)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── workflow.py            # WorkflowUGQ (500 linhas)
│   │   ├── email_service.py       # EmailService (350 linhas)
│   │   ├── evolution_api_service.py  # WhatsApp (650 linhas)
│   │   ├── ai_client.py           # DeepSeek AI
│   │   └── report_generator.py    # Relatórios PDF
│   ├── routes/
│   │   ├── routes_auth.py         # Login, logout
│   │   ├── routes_view.py         # Templates
│   │   ├── routes_documento.py    # CRUD documentos
│   │   ├── routes_tarefa.py       # Tarefas
│   │   ├── routes_dashboard.py    # Dashboards
│   │   ├── routes_whatsapp.py     # WhatsApp admin
│   │   └── ...
│   ├── templates/
│   │   ├── base.html              # Layout base
│   │   ├── dashboard.html
│   │   ├── documento_detalhe.html
│   │   └── ...
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── uploads/
│       ├── documentos/
│       └── publicados/
├── config.py                       # Configurações
├── app.py                          # Entry point
├── init_database.py                # Inicializa DB
├── requirements.txt                # Dependências
├── .env.example                    # Variáveis de ambiente
├── README.md                       # Este arquivo
├── GUIA_EVOLUTION_API.md          # Guia WhatsApp
├── INSTALACAO_RAPIDA.md           # Quick start
└── DOCUMENTACAO_COMPLETA.md       # Docs técnicas
```

---

## 🔐 Segurança

### Autenticação e Autorização

- ✅ **Hashing bcrypt** de senhas
- ✅ **Flask-Login** para sessões
- ✅ **Perfis de acesso** (6 tipos)
- ✅ **Decoradores** `@login_required`
- ✅ **Verificação de permissões** em cada rota

### Proteção de Dados

- ✅ **HTTPS** (SSL/TLS em produção)
- ✅ **CSRF protection** (Flask-WTF)
- ✅ **Rate limiting** (Flask-Limiter)
- ✅ **SQL injection** prevention (ORM)
- ✅ **XSS protection** (Jinja2 auto-escape)

### WhatsApp

- ✅ **Timeout de sessão** (15 min)
- ✅ **Bloqueio por tentativas** (3 erros = 30 min)
- ✅ **Assinatura digital** com hash SHA256
- ✅ **Registro de IP/User-Agent**
- ✅ **Auditoria completa** de mensagens
- ✅ **Horários restritos** (seg-sex, 08:00-18:00)

### Auditoria

- ✅ **ValidacaoUGQ** - Registra todas transições do workflow
- ✅ **LogWhatsApp** - Todas mensagens enviadas/recebidas
- ✅ **Histórico de documentos** - Versionamento completo
- ✅ **Assinaturas digitais** - Imutáveis, rastreáveis

**Documentação completa:** [SECURITY_FIXES_IMPLEMENTED.md](SECURITY_FIXES_IMPLEMENTED.md)

---

## 📚 Documentação Adicional

- **[GUIA_EVOLUTION_API.md](GUIA_EVOLUTION_API.md)** - Setup completo WhatsApp
- **[INSTALACAO_RAPIDA.md](INSTALACAO_RAPIDA.md)** - Quick start guide
- **[DOCUMENTACAO_COMPLETA.md](DOCUMENTACAO_COMPLETA.md)** - Referência técnica
- **[SECURITY_FIXES_IMPLEMENTED.md](SECURITY_FIXES_IMPLEMENTED.md)** - Segurança
- **[AUDITORIA_SEGURANCA_COMPLETA.md](AUDITORIA_SEGURANCA_COMPLETA.md)** - Auditoria

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'psycopg2'"

```bash
pip install psycopg2-binary
```

### Erro: "FATAL: password authentication failed"

Verifique DATABASE_URL no .env com credenciais corretas.

### Erro: "WhatsApp não está ativo"

1. Verifique Evolution API rodando: `curl http://localhost:8080/`
2. Configure em `/admin/whatsapp`
3. Conecte WhatsApp via QR Code

### Erro: P3005 - "Database schema is not empty"

Evolution API precisa de banco separado! Veja: [SETUP_EVOLUTION_DB.md](SETUP_EVOLUTION_DB.md)

```sql
CREATE DATABASE evolution_db OWNER ged_user;
```

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Add: Nova feature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

## 📝 Licença

Este projeto está sob a licença **MIT**. Veja [LICENSE](LICENSE) para mais detalhes.

---

## 👥 Autores

- **Emanuel Feba** - Desenvolvimento principal

---

## 🎉 Agradecimentos

- **EBSERH** - Padrões e fluxos de qualidade
- **Evolution API** - Integração WhatsApp open-source
- **DeepSeek** - IA para análise de documentos
- **Flask Community** - Framework web Python

---

## 📊 Status do Projeto

| Item | Status |
|------|--------|
| **Backend** | ✅ 100% Funcional |
| **Frontend** | ✅ 100% Funcional |
| **Workflow UGQ** | ✅ 100% Implementado |
| **WhatsApp** | ✅ Evolution API |
| **IA** | ✅ DeepSeek integrado |
| **Segurança** | ✅ Auditado |
| **Documentação** | ✅ Completa |

---

## 🚀 Roadmap

- [ ] **App Mobile** (React Native)
- [ ] **Notificações Push**
- [ ] **Integração com SEI**
- [ ] **Assinatura Digital ICP-Brasil**
- [ ] **OCR Avançado** (Tesseract)
- [ ] **Webhooks** genéricos
- [ ] **API REST** pública

---

**Sistema GED EBSERH - Gestão Eletrônica de Documentos**

📱 WhatsApp Evolution API | 🤖 IA DeepSeek | 🔒 100% Seguro | 📊 Workflow Completo

**Desenvolvido com ❤️ para a saúde brasileira**
