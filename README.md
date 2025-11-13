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

## 🔄 Workflow EBSERH (5 Etapas Automáticas)

O sistema implementa o **fluxo de aprovação padronizado EBSERH**:

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUXO AUTOMÁTICO EBSERH                      │
└─────────────────────────────────────────────────────────────────┘

1️⃣ AUTOR (Usuário Comum)
   └─> Cria documento e seleciona Chefia Imediata
       ⏱️ Sistema cria automaticamente tarefa: "Analisar"

2️⃣ CHEFIA IMEDIATA (Gerente)
   └─> Analisa pertinência do documento
       ⏱️ Se aprovado → cria automaticamente: "Validar Conteúdo"

3️⃣ ÁREA TÉCNICA/ESPECIALISTA (Responsável Interno do Setor)
   └─> Valida conteúdo técnico
       ⏱️ Se aprovado → cria automaticamente: "Validar Padronização"

4️⃣ QUALIDADE (Responsável Interno - Setor Qualidade)
   └─> Valida padronização e normas EBSERH
       ⏱️ Se aprovado → cria automaticamente: "Aprovar"

5️⃣ APROVADOR (Gerente/Superintendência)
   └─> Aprovação final
       ⏱️ Se aprovado → cria automaticamente: "Publicar"

6️⃣ GESTÃO DOCUMENTAL (Administrador)
   └─> Publica e gera PDF final com código definitivo
       ✅ Documento publicado no repositório

```

**Características do Workflow:**
- ✅ **100% Automático** - Próxima tarefa criada automaticamente
- ⏱️ **Prazos Definidos** - Cada etapa tem prazo específico
- 📧 **Responsável Automático** - Sistema seleciona baseado em perfil e setor
- 🔙 **Rejeição Inteligente** - Volta ao autor para correção
- 📊 **Rastreabilidade Total** - Histórico completo de cada etapa

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

## 🔑 Usuários Padrão (10 Usuários EBSERH)

O sistema cria automaticamente **10 usuários** para testar todo o workflow:

### 🔴 Administrador (Gestão Documental)
| Email | Senha | Perfil | Setor |
|-------|-------|--------|-------|
| admin@example.com | admin123 | Administrador | Gestão Documental |

### 🔵 Gerentes (Chefia Imediata + Aprovadores)
| Email | Senha | Perfil | Setor |
|-------|-------|--------|-------|
| maria.silva@example.com | gerente123 | Gerente | Produção |
| joao.santos@example.com | gerente123 | Gerente | Qualidade |
| carlos.mendes@example.com | gerente123 | Gerente | Operações |

### 🟢 Responsáveis Internos (Validadores)
| Email | Senha | Perfil | Setor |
|-------|-------|--------|-------|
| ana.costa@example.com | resp123 | Responsável Interno | Qualidade |
| pedro.oliveira@example.com | resp123 | Responsável Interno | Produção |
| lucia.ferreira@example.com | resp123 | Responsável Interno | Operações |

### ⚪ Usuários Comuns (Autores)
| Email | Senha | Perfil | Setor |
|-------|-------|--------|-------|
| rafael.alves@example.com | usuario123 | Comum | Produção |
| fernanda.lima@example.com | usuario123 | Comum | Operações |
| usuario@example.com | usuario123 | Comum | Operações |

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

### Teste Manual do Workflow EBSERH

1. **Login como Usuário Comum** (`usuario@example.com` / `usuario123`)
   - Criar documento no setor "Operações"
   - Selecionar "Carlos Mendes" como Chefia Imediata
   - Sistema cria tarefa "Analisar" automaticamente

2. **Login como Carlos Mendes** (`carlos.mendes@example.com` / `gerente123`)
   - Ver tarefa "Analisar" na dashboard
   - Escrever parecer e clicar "Aprovar"
   - Sistema cria tarefa "Validar Conteúdo" para Lucia Ferreira

3. **Login como Lucia Ferreira** (`lucia.ferreira@example.com` / `resp123`)
   - Ver tarefa "Validar Conteúdo"
   - Aprovar
   - Sistema cria tarefa "Validar Padronização" para Ana Costa

4. **Login como Ana Costa** (`ana.costa@example.com` / `resp123`)
   - Ver tarefa "Validar Padronização" (Qualidade)
   - Aprovar
   - Sistema cria tarefa "Aprovar" para um Gerente

5. **Login como Gerente** (qualquer gerente)
   - Aprovar final
   - Sistema cria tarefa "Publicar" para Admin

6. **Login como Admin** (`admin@example.com` / `admin123`)
   - Fazer upload do PDF final
   - Publicar
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
