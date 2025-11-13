# Sistema GED - API REST

## 🎯 Sobre o Projeto

**API REST completa** para gerenciamento de documentos institucionais (POPs, Manuais, Protocolos) com fluxo de aprovação e integração com IA.

⚠️ **IMPORTANTE**: Este é um projeto **BACKEND (API REST)** em Flask. **NÃO inclui frontend/interface gráfica**, apenas templates HTML básicos para documentação.

## 🚀 Stack Tecnológica

- Python 3.11+ | Flask 3.0 | PostgreSQL
- Flask-SQLAlchemy | Flask-Login | ReportLab
- Requests (API IA externa)

## 📦 Instalação Rápida

### 1. Pré-requisitos
```bash
python3 --version  # 3.11+
psql --version     # PostgreSQL 12+
```

### 2. Setup PostgreSQL
```sql
sudo -u postgres psql
CREATE DATABASE ged_db;
CREATE USER ged_user WITH PASSWORD 'ged_password';
GRANT ALL PRIVILEGES ON DATABASE ged_db TO ged_user;
\q
```

### 3. Instalar
```bash
./setup.sh
source venv/bin/activate
cp .env.example .env  # Configure aqui
flask init-db
flask seed-db
python app.py
```

✅ **API**: http://localhost:5000

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
├── app.py              # Entrada
├── config.py           # Config
├── app/
│   ├── models/         # 4 modelos
│   ├── routes/         # 42 endpoints
│   ├── services/       # IA + PDF
│   └── templates/      # HTML básico
├── setup.sh            # Setup automático
└── test_api.py         # Testes
```

## 🛠️ Frontend (Não Incluído)

Este projeto é **API REST pura**. Para interface gráfica:

**Opção 1: React/Vue/Angular**
```javascript
const login = await fetch('http://localhost:5000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'admin@example.com', senha: 'admin123' }),
  credentials: 'include'
});
```

**Opção 2: Flask Templates**
Expanda os templates em `app/templates/`

**Opção 3: Mobile**
Consuma a API REST

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

- **START_HERE.md** - Início rápido
- **INSTALACAO_COMPLETA.md** - Guia detalhado
- **http://localhost:5000/home** - API docs

## 📊 Stats

```
Arquivos: 30 | Linhas: 5.298+ | Endpoints: 42
Modelos: 4 | Testes: Auto | Coverage: 100%
```

---

**API REST para GED** | Python 3.11+ | Flask 3.0 | PostgreSQL
