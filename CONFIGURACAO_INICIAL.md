# Configuração Inicial do Sistema GED

## 📋 Pré-requisitos

- Python 3.8 ou superior
- PostgreSQL 12 ou superior
- Git (opcional)

---

## 🚀 Instalação Rápida

### Windows

1. **Clone o repositório** (ou baixe o ZIP):
   ```cmd
   git clone https://github.com/febaemanuel/ged.git
   cd ged
   ```

2. **Crie ambiente virtual**:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Instale dependências**:
   ```cmd
   pip install -r requirements.txt
   ```

4. **Crie o arquivo .env**:
   ```cmd
   python criar_env.py
   ```

5. **Edite o arquivo .env** com suas configurações (veja seção abaixo)

6. **Execute migrações do banco**:
   ```cmd
   python aplicar_migracao.py
   ```

7. **Inicie a aplicação**:
   ```cmd
   python app.py
   ```

8. **Acesse**: http://127.0.0.1:5000

---

### Linux/Mac

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/febaemanuel/ged.git
   cd ged
   ```

2. **Crie ambiente virtual**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instale dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Crie o arquivo .env**:
   ```bash
   python3 criar_env.py
   ```

5. **Edite o arquivo .env** com suas configurações

6. **Execute migrações**:
   ```bash
   python3 aplicar_migracao.py
   ```

7. **Inicie a aplicação**:
   ```bash
   python3 app.py
   ```

8. **Acesse**: http://127.0.0.1:5000

---

## 🔑 Criando o Arquivo .env

### Método 1: Usando o Script Automático (Recomendado)

**Windows:**
```cmd
python criar_env.py
```

**Linux/Mac:**
```bash
python3 criar_env.py
```

O script vai:
- ✅ Gerar uma `SECRET_KEY` segura automaticamente
- ✅ Criar o arquivo `.env` baseado no `.env.example`
- ✅ Fazer backup se `.env` já existir

### Método 2: Manual

**Passo 1**: Copie o arquivo `.env.example`:

**Windows (CMD):**
```cmd
copy .env.example .env
```

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**Linux/Mac:**
```bash
cp .env.example .env
```

**Passo 2**: Gere uma `SECRET_KEY` segura:

**Python:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Resultado exemplo:**
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

**Passo 3**: Edite o arquivo `.env` e substitua:
```env
SECRET_KEY=your-secret-key-change-in-production
```

Por:
```env
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

---

## ⚙️ Configurando o Arquivo .env

Após criar o arquivo `.env`, você precisa configurar as seguintes variáveis:

### 1. Configuração Básica (Obrigatório)

```env
# SECRET_KEY já foi gerada automaticamente
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6...

# Modo de execução (development ou production)
FLASK_ENV=development
```

### 2. Banco de Dados PostgreSQL (Obrigatório)

```env
# Formato: postgresql://usuario:senha@host:porta/nome_banco
DATABASE_URL=postgresql://ged_user:ged_password@localhost:5432/ged_db?client_encoding=utf8
```

**Como configurar:**

1. **Instale PostgreSQL** (se ainda não tiver):
   - Windows: https://www.postgresql.org/download/windows/
   - Linux: `sudo apt install postgresql postgresql-contrib`
   - Mac: `brew install postgresql`

2. **Crie o banco de dados**:
   ```sql
   -- Conecte ao PostgreSQL como superusuário
   sudo -u postgres psql  # Linux
   psql -U postgres       # Windows

   -- Execute:
   CREATE DATABASE ged_db;
   CREATE USER ged_user WITH PASSWORD 'ged_password';
   GRANT ALL PRIVILEGES ON DATABASE ged_db TO ged_user;
   \q
   ```

3. **Atualize DATABASE_URL** no `.env` com suas credenciais

### 3. API de IA - DeepSeek (Opcional)

```env
AI_API_BASE_URL=https://api.deepseek.com
AI_API_KEY=sk-your-api-key-here
AI_API_MODEL=deepseek-chat
AI_API_TIMEOUT=30
```

**Para obter a chave:**
1. Acesse: https://platform.deepseek.com/
2. Crie uma conta
3. Vá em "API Keys" e gere uma nova chave
4. Copie e cole no `.env`

**Nota**: A IA é usada para análise inteligente de documentos. Se não configurar, o sistema funciona normalmente sem IA.

### 4. E-mail SMTP (Opcional)

```env
# Gmail (exemplo)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-aplicativo
MAIL_DEFAULT_SENDER=noreply@ged.com
```

**Como configurar Gmail:**

1. Ative a **verificação em 2 etapas** na sua conta Google
2. Gere uma **senha de aplicativo**:
   - Acesse: https://myaccount.google.com/apppasswords
   - Selecione "App personalizado" → digite "GED"
   - Copie a senha gerada (16 caracteres)
3. Use essa senha no campo `MAIL_PASSWORD`

**Outros provedores:**
- **Outlook**: `smtp.office365.com`, porta `587`
- **Yahoo**: `smtp.mail.yahoo.com`, porta `587`

**Nota**: E-mail é usado para notificações. Se não configurar, o sistema funciona, mas sem envio de e-mails.

### 5. WhatsApp - Evolution API (Opcional)

```env
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_INSTANCE_NAME=minha_instancia
EVOLUTION_API_KEY=sua-api-key-aqui
```

**Como configurar:**

Veja o guia completo: **`GUIA_EVOLUTION_API.md`**

Resumo:
1. Instale a Evolution API seguindo o guia
2. Configure as credenciais no `.env`
3. Acesse http://127.0.0.1:5000/admin/whatsapp
4. Conecte seu WhatsApp escaneando o QR Code

**Nota**: WhatsApp é opcional e usado para notificações e chatbot.

---

## 🗄️ Configuração do Banco de Dados

### PostgreSQL no Windows

1. **Baixe e instale**: https://www.postgresql.org/download/windows/
2. **Durante instalação**:
   - Anote a senha do usuário `postgres`
   - Porta padrão: `5432`
3. **Após instalação**, abra **pgAdmin 4** ou **SQL Shell (psql)**
4. **Crie o banco**:
   ```sql
   CREATE DATABASE ged_db;
   CREATE USER ged_user WITH PASSWORD 'ged_password';
   GRANT ALL PRIVILEGES ON DATABASE ged_db TO ged_user;
   ```

### PostgreSQL no Linux

```bash
# Instalar PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Iniciar serviço
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Criar banco
sudo -u postgres psql -c "CREATE DATABASE ged_db;"
sudo -u postgres psql -c "CREATE USER ged_user WITH PASSWORD 'ged_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ged_db TO ged_user;"
```

### PostgreSQL no Mac

```bash
# Instalar com Homebrew
brew install postgresql

# Iniciar serviço
brew services start postgresql

# Criar banco
createdb ged_db
psql ged_db -c "CREATE USER ged_user WITH PASSWORD 'ged_password';"
psql ged_db -c "GRANT ALL PRIVILEGES ON DATABASE ged_db TO ged_user;"
```

---

## 🔧 Problemas Comuns

### Erro: "SECRET_KEY não definida"

**Causa**: Arquivo `.env` não existe ou está incompleto

**Solução**:
```bash
python criar_env.py
```

### Erro: "No module named 'flask'"

**Causa**: Dependências não instaladas

**Solução**:
```bash
pip install -r requirements.txt
```

### Erro: "could not connect to server: Connection refused"

**Causa**: PostgreSQL não está rodando ou configuração incorreta

**Solução**:
- **Windows**: Abra "Serviços" e inicie "postgresql-x64-XX"
- **Linux**: `sudo systemctl start postgresql`
- **Mac**: `brew services start postgresql`

### Erro: "FATAL: database 'ged_db' does not exist"

**Causa**: Banco de dados não foi criado

**Solução**: Siga a seção "Configuração do Banco de Dados" acima

### Erro: "ModuleNotFoundError: No module named 'app'"

**Causa**: Não está no diretório correto ou ambiente virtual não ativado

**Solução**:
```bash
cd /caminho/para/ged
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

---

## ✅ Checklist de Instalação

Use este checklist para garantir que tudo está configurado:

- [ ] Python 3.8+ instalado (`python --version`)
- [ ] PostgreSQL instalado e rodando
- [ ] Repositório clonado/baixado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo `.env` criado
- [ ] `SECRET_KEY` configurada no `.env`
- [ ] `DATABASE_URL` configurada no `.env`
- [ ] Banco de dados PostgreSQL criado (`ged_db`)
- [ ] Usuário PostgreSQL criado (`ged_user`)
- [ ] Migrações executadas (`python aplicar_migracao.py`)
- [ ] Aplicação iniciando sem erros (`python app.py`)
- [ ] Acesso ao sistema funcionando (http://127.0.0.1:5000)

---

## 🎯 Próximos Passos

Após a instalação:

1. **Acesse o sistema**: http://127.0.0.1:5000
2. **Crie o primeiro usuário administrador**
3. **Configure o sistema**:
   - Tipos de documento
   - Departamentos
   - Usuários
4. **Configure integrações opcionais**:
   - WhatsApp (veja `GUIA_EVOLUTION_API.md`)
   - E-mail SMTP
   - API de IA

---

## 📚 Documentação Relacionada

- **`GUIA_EVOLUTION_API.md`** - Setup completo do WhatsApp
- **`COMO_USAR_DIAGNOSTICO.md`** - Diagnóstico de problemas
- **`PROBLEMAS_COMUNS_WHATSAPP.md`** - Troubleshooting WhatsApp
- **`EVOLUTION_API_V2_REFERENCE.md`** - Referência da API
- **`README.md`** - Informações gerais do projeto

---

## 🆘 Precisa de Ajuda?

1. **Leia a documentação** relacionada acima
2. **Execute o diagnóstico**:
   ```bash
   python diagnostico_evolution_v2_completo.py
   ```
3. **Verifique os logs**:
   ```bash
   tail -f logs/app.log
   ```
4. **Abra uma issue** no GitHub com detalhes do erro

---

**Última atualização**: 21/11/2024
**Versão**: 2.0
**Compatível com**: Python 3.8+, PostgreSQL 12+
