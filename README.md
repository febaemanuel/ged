# Sistema GED - Completo (Backend + Frontend)

## 🎯 Sobre o Projeto

**Sistema completo** de gerenciamento eletrônico de documentos (GED) para instituições, com:
- 📄 Gestão de POPs, Manuais e Protocolos
- ✅ Fluxo de aprovação com tarefas
- 🤖 Integração com IA (extração, classificação, sumarização)
- 📊 Relatórios PDF automáticos
- 🎨 **Interface web completa e moderna**

✨ **NOVO**: Agora inclui **frontend completo** com Bootstrap 5, interface responsiva e todas as funcionalidades implementadas!

## 🚀 Stack Tecnológica

**Backend:**
- Python 3.11+ | Flask 3.0 | PostgreSQL
- Flask-SQLAlchemy | Flask-Login | ReportLab
- Requests (API IA externa)

**Frontend:**
- Bootstrap 5.3.0 | Bootstrap Icons 1.11.0
- JavaScript ES6+ | CSS3 customizado
- Jinja2 Templates | Responsive Design

## 📦 Instalação Rápida

### 🐧 Linux / macOS

#### 1. Pré-requisitos
```bash
python3 --version  # 3.11+
psql --version     # PostgreSQL 12+
```

#### 2. Setup PostgreSQL
```sql
sudo -u postgres psql
CREATE DATABASE ged_db;
CREATE USER ged_user WITH PASSWORD 'ged_password';
GRANT ALL PRIVILEGES ON DATABASE ged_db TO ged_user;
\q
```

#### 3. Instalar
```bash
./setup.sh
source venv/bin/activate
cp .env.example .env  # Configure aqui
flask init-db
flask seed-db
python app.py
```

### 🪟 Windows

**Instalação super fácil com scripts .bat!**

#### 1. Duplo clique em `setup.bat`
O script instala tudo automaticamente.

#### 2. Configure PostgreSQL e `.env`
Edite o arquivo `.env` com suas credenciais.

#### 3. Duplo clique em `init-db.bat`
Cria tabelas e usuários padrão.

#### 4. Duplo clique em `start.bat`
Inicia o servidor!

**📘 Guia completo**: [WINDOWS_SETUP.md](WINDOWS_SETUP.md)

---

✅ **Acesse**: http://localhost:5000

## 🔑 Usuários Padrão

| Email | Senha | Perfil |
|-------|-------|--------|
| admin@example.com | admin123 | Administrador |
| gerente@example.com | gerente123 | Gerente |
| usuario@example.com | usuario123 | Usuário |

## 🌐 Endpoints Principais

```bash
# Autenticação
POST /auth/login
GET  /auth/me

# Documentos
GET  /documento/lista
POST /documento/criar
GET  /documento/<id>
GET  /documento/publico

# Tarefas
GET  /tarefa/minhas
POST /tarefa/criar
POST /tarefa/<id>/concluir

# IA
POST /ia/extract/<id>
POST /ia/classify/<id>
POST /ia/search

# Relatórios PDF
GET /relatorio/pdf/tarefas_atrasadas
GET /relatorio/pdf/geral
```

**42 endpoints no total** | Documentação: http://localhost:5000/home

## 🧪 Testar

```bash
# Automático
python test_api.py

# Postman
# Importe: GED_API.postman_collection.json

# cURL
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","senha":"admin123"}' \
  -c cookies.txt

curl -X GET http://localhost:5000/documento/lista -b cookies.txt
```

## 📊 Funcionalidades

### ✅ Documentos
- CRUD completo (POPs, Manuais, Protocolos)
- Upload (.doc, .odt, .pdf)
- Códigos automáticos
- Controle de vencimento

### ✅ Fluxo de Aprovação
- 6 tipos de tarefas
- Prazos e alertas
- Pareceres e aprovações
- Timeline de ações

### ✅ IA (API Externa)
- Extração de texto
- Classificação automática
- Sumarização
- Busca semântica
- Logs de auditoria

### ✅ Relatórios PDF
- Tarefas atrasadas
- Documentos vencendo
- Relatório geral

### ✅ Permissões
- **Comum**: Documentos e tarefas
- **Gerente**: + Gestão e IA
- **Admin**: Acesso total

## 📁 Estrutura

```
ged/
├── app.py                      # Entrada
├── config.py                   # Config
├── app/
│   ├── models/                 # 4 modelos SQLAlchemy
│   ├── routes/                 # 6 blueprints (API + VIEW)
│   │   ├── routes_auth.py      # API: Autenticação
│   │   ├── routes_documento.py # API: Documentos
│   │   ├── routes_tarefa.py    # API: Tarefas
│   │   ├── routes_ia.py        # API: IA
│   │   ├── routes_dashboard.py # API: Dashboard/PDF
│   │   └── routes_view.py      # VIEW: Frontend HTML ✨
│   ├── services/               # IA + PDF
│   ├── static/                 # Frontend assets ✨
│   │   ├── css/style.css       # CSS customizado
│   │   └── js/main.js          # JavaScript principal
│   └── templates/              # 12 templates HTML ✨
│       ├── base.html           # Template base
│       ├── login.html          # Login
│       ├── dashboard.html      # Dashboard
│       ├── documentos.html     # Listagem
│       ├── documento_*.html    # CRUD docs
│       ├── tarefas.html        # Listagem
│       ├── tarefa_*.html       # CRUD tarefas
│       ├── usuarios.html       # Gestão (Admin)
│       ├── perfil.html         # Perfil usuário
│       └── repositorio_publico.html
├── setup.sh                    # Setup automático
└── test_api.py                 # Testes
```

## 🎨 Frontend Completo

**Interface web moderna e responsiva** com Bootstrap 5!

### Páginas Implementadas:
- 🔐 **Login** - Autenticação segura
- 📊 **Dashboard** - Visão geral com estatísticas
- 📄 **Documentos** - CRUD completo + filtros + timeline
- ✅ **Tarefas** - Gestão completa + aprovações
- 👥 **Usuários** - Gerenciamento (Admin)
- 👤 **Perfil** - Dados pessoais + alterar senha
- 🌐 **Repositório Público** - Documentos publicados

### Recursos Frontend:
- ✅ Design responsivo (mobile, tablet, desktop)
- ✅ Bootstrap 5 + Bootstrap Icons
- ✅ JavaScript interativo (validações, modals, etc.)
- ✅ CSS customizado com animações
- ✅ Upload de arquivos com drag & drop
- ✅ Filtros e busca em tempo real
- ✅ Paginação automática
- ✅ Flash messages e toasts
- ✅ Integração total com API REST

**Documentação**: [FRONTEND_COMPLETO.md](FRONTEND_COMPLETO.md)

## 🔧 Comandos

```bash
./verificar_instalacao.sh  # Verificar sistema
flask shell                # Console
flask verificar-vencimentos # Rotina
tail -f logs/ged.log       # Logs
```

## 🐳 Produção

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🐛 Problemas?

### ModuleNotFoundError
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Database connection
```bash
sudo systemctl start postgresql
```

### Port 5000 in use
```bash
lsof -ti:5000 | xargs kill -9
```

**Guia completo**: [INSTALACAO_COMPLETA.md](INSTALACAO_COMPLETA.md)

## 📚 Documentação

- **START_HERE.md** - Início rápido (5 minutos)
- **INSTALACAO_COMPLETA.md** - Guia detalhado Linux/macOS
- **WINDOWS_SETUP.md** - Guia completo para Windows 🪟
- **FRONTEND_COMPLETO.md** - Documentação do frontend ✨
- **http://localhost:5000/home** - API docs
- **http://localhost:5000** - Interface web (após login)

## 📊 Stats

```
Backend:
  Arquivos Python: 14 | Linhas: 5.500+
  API Endpoints: 42 | Modelos: 4
  Blueprints: 6 (5 API + 1 VIEW)

Frontend:
  Templates HTML: 12 | CSS: 330 linhas
  JavaScript: 470 linhas | Componentes: 50+
  VIEW Endpoints: 25

Total: 8.000+ linhas de código
```

---

**Sistema GED Completo** | Backend API REST + Frontend Web | Python 3.11+ | Flask 3.0 | PostgreSQL | Bootstrap 5
