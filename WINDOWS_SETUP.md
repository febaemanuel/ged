# Sistema GED - Guia de Instalação Windows

## 🪟 Instalação Rápida no Windows

Este guia mostra como instalar e executar o Sistema GED no Windows usando os scripts `.bat` fornecidos.

---

## 📋 Pré-requisitos

### 1. Python 3.11+
**Baixar**: https://www.python.org/downloads/

**Durante a instalação:**
- ✅ Marque "Add Python to PATH"
- ✅ Marque "Install pip"

**Verificar instalação:**
```cmd
python --version
pip --version
```

### 2. PostgreSQL 12+
**Baixar**: https://www.postgresql.org/download/windows/

**Durante a instalação:**
- Anote a senha do usuário `postgres`
- Porta padrão: `5432`

**Verificar instalação:**
```cmd
psql --version
```

### 3. Git (Opcional)
**Baixar**: https://git-scm.com/download/win

---

## 🚀 Instalação Automática

### Passo 1: Download do Projeto
```cmd
git clone <url-do-repositorio>
cd ged
```

### Passo 2: Executar Setup
**Duplo clique** em `setup.bat` ou execute:
```cmd
setup.bat
```

O script irá:
- ✅ Verificar Python e pip
- ✅ Criar ambiente virtual (venv)
- ✅ Instalar todas as dependências
- ✅ Criar arquivo `.env`
- ✅ Criar diretórios necessários

---

## ⚙️ Configuração

### Passo 3: Configurar PostgreSQL

**Abrir PowerShell ou CMD como Administrador:**
```cmd
psql -U postgres
```

**Executar os comandos SQL:**
```sql
CREATE DATABASE ged_db;
CREATE USER ged_user WITH PASSWORD 'ged_password';
GRANT ALL PRIVILEGES ON DATABASE ged_db TO ged_user;
\q
```

### Passo 4: Configurar arquivo .env

**Abrir** `\.env` com Notepad, VS Code ou outro editor.

**Editar as seguintes variáveis:**
```env
# Database
DATABASE_URL=postgresql://ged_user:ged_password@localhost:5432/ged_db

# Flask
SECRET_KEY=sua_chave_secreta_aqui_minimo_32_caracteres_aleatorios

# IA API (opcional - configure depois se quiser)
AI_API_BASE_URL=https://api.exemplo.com
AI_API_KEY=sua_chave_api_aqui
```

**Gerar SECRET_KEY no Python:**
```cmd
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🗃️ Inicializar Banco de Dados

### Passo 5: Criar Tabelas e Usuários

**Duplo clique** em `init-db.bat` ou execute:
```cmd
init-db.bat
```

Isso irá:
- ✅ Criar todas as tabelas
- ✅ Criar 3 usuários padrão:
  - **admin@example.com** / admin123 (Administrador)
  - **gerente@example.com** / gerente123 (Gerente)
  - **usuario@example.com** / usuario123 (Usuário)

---

## ▶️ Executar a Aplicação

### Passo 6: Iniciar Servidor

**Duplo clique** em `start.bat` ou execute:
```cmd
start.bat
```

**Abrir no navegador:**
```
http://localhost:5000
```

Você será redirecionado para a página de login.

---

## 🛠️ Scripts Disponíveis

| Script | Descrição |
|--------|-----------|
| `setup.bat` | Instalação inicial completa |
| `start.bat` | Iniciar o servidor Flask |
| `init-db.bat` | Criar tabelas e dados iniciais |
| `verificar.bat` | Verificar instalação |

---

## 🔍 Verificar Instalação

Para verificar se tudo está configurado corretamente:

```cmd
verificar.bat
```

Este script verifica:
- ✅ Python e pip
- ✅ PostgreSQL
- ✅ Ambiente virtual
- ✅ Arquivo .env
- ✅ Estrutura de diretórios
- ✅ Sintaxe Python dos arquivos

---

## 🐛 Solução de Problemas

### Erro: "python não é reconhecido"

**Causa:** Python não está no PATH do Windows

**Solução:**
1. Reinstale Python marcando "Add Python to PATH"
2. OU adicione manualmente ao PATH:
   - Sistema > Configurações Avançadas > Variáveis de Ambiente
   - Adicione `C:\Users\SeuUsuario\AppData\Local\Programs\Python\Python311` ao PATH

### Erro: "psql não é reconhecido"

**Causa:** PostgreSQL não está no PATH

**Solução:**
1. Adicione ao PATH: `C:\Program Files\PostgreSQL\15\bin`
2. Ou use o caminho completo: `"C:\Program Files\PostgreSQL\15\bin\psql" -U postgres`

### Erro: "Falha ao conectar ao banco de dados"

**Verificar:**
1. PostgreSQL está rodando?
   ```cmd
   sc query postgresql-x64-15
   ```
2. Iniciar se necessário:
   ```cmd
   net start postgresql-x64-15
   ```
3. Verificar credenciais no `.env`

### Erro: "Porta 5000 em uso"

**Encontrar processo:**
```cmd
netstat -ano | findstr :5000
```

**Matar processo:**
```cmd
taskkill /PID <numero_do_pid> /F
```

### Erro: "ModuleNotFoundError"

**Causa:** Dependências não instaladas ou ambiente virtual não ativado

**Solução:**
```cmd
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### Permissões de Execução

Se o Windows bloquear a execução dos scripts `.bat`:

1. Clique com botão direito no arquivo
2. Propriedades > Desbloquear
3. Ou execute como Administrador

---

## 📁 Estrutura de Diretórios

Após a instalação completa:

```
ged\
├── venv\                      # Ambiente virtual Python
├── app\
│   ├── models\                # Modelos do banco
│   ├── routes\                # Rotas (API + VIEW)
│   ├── services\              # Serviços (IA, PDF)
│   ├── static\                # CSS, JS
│   ├── templates\             # HTML
│   └── uploads\               # Arquivos enviados
│       ├── documentos\
│       └── publicados\
├── logs\                      # Logs da aplicação
├── .env                       # Configurações (NÃO COMMITAR)
├── setup.bat                  # Setup inicial ✨
├── start.bat                  # Iniciar servidor ✨
├── init-db.bat               # Inicializar BD ✨
├── verificar.bat             # Verificar instalação ✨
├── requirements.txt
└── app.py
```

---

## 🔐 Segurança

### Produção

**⚠️ NUNCA use em produção no Windows com Flask development server!**

Para produção, use:
- **Waitress** (WSGI server para Windows)
- **IIS** com wfastcgi
- **Docker** com Gunicorn

**Instalar Waitress:**
```cmd
pip install waitress
```

**Executar:**
```cmd
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

### Firewall

Permita a porta 5000 no Firewall do Windows:
```cmd
netsh advfirewall firewall add rule name="Flask GED" dir=in action=allow protocol=TCP localport=5000
```

---

## 🌐 Acessar de Outros Dispositivos

Para acessar de outros dispositivos na rede local:

1. **Descobrir seu IP local:**
   ```cmd
   ipconfig
   ```
   Procure por "IPv4 Address" (ex: 192.168.1.100)

2. **Iniciar servidor:**
   ```cmd
   start.bat
   ```

3. **Acessar de outro dispositivo:**
   ```
   http://192.168.1.100:5000
   ```

---

## 🎓 Comandos Úteis

### Ativar Ambiente Virtual
```cmd
venv\Scripts\activate.bat
```

### Desativar Ambiente Virtual
```cmd
deactivate
```

### Executar Flask Shell
```cmd
venv\Scripts\activate.bat
flask shell
```

### Ver Logs
```cmd
type logs\ged.log
```

### Limpar Cache Python
```cmd
del /s /q __pycache__
del /s /q *.pyc
```

### Atualizar Dependências
```cmd
pip install --upgrade -r requirements.txt
```

---

## 📊 Executar Testes

```cmd
venv\Scripts\activate.bat
python test_api.py
```

---

## 🆘 Suporte

### Documentação Completa
- **README.md** - Visão geral do projeto
- **INSTALACAO_COMPLETA.md** - Guia detalhado (Linux/Mac)
- **FRONTEND_COMPLETO.md** - Documentação do frontend
- **WINDOWS_SETUP.md** - Este arquivo

### Logs
Verifique os logs em `logs\ged.log` para debugging.

### Comunidade
Abra uma issue no repositório do projeto com:
- Sistema operacional e versão do Windows
- Versão do Python
- Mensagem de erro completa
- Logs relevantes

---

## ✅ Checklist de Instalação

- [ ] Python 3.11+ instalado
- [ ] PostgreSQL 12+ instalado
- [ ] Executado `setup.bat`
- [ ] Banco de dados `ged_db` criado
- [ ] Arquivo `.env` configurado
- [ ] Executado `init-db.bat`
- [ ] `verificar.bat` passou sem erros
- [ ] Consegue acessar http://localhost:5000
- [ ] Login funciona com usuário padrão

---

## 🎉 Pronto!

Seu Sistema GED está configurado e rodando no Windows! 🚀

**Credenciais Padrão:**
- Email: `admin@example.com`
- Senha: `admin123`

**Acesse:** http://localhost:5000

---

**Desenvolvido para Windows** | Python 3.11+ | Flask 3.0 | PostgreSQL | Bootstrap 5
