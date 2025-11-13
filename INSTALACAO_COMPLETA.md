# 🚀 GUIA COMPLETO DE INSTALAÇÃO E CONFIGURAÇÃO
## Sistema GED - Gerenciador Eletrônico de Documentos

## 📋 CHECKLIST DE VERIFICAÇÃO

### ✅ Requisitos Implementados

**Stack Tecnológica (COMPLETO)**
- ✅ Python 3.11+
- ✅ Flask 3.0.0
- ✅ PostgreSQL (via psycopg2-binary)
- ✅ Flask-SQLAlchemy 3.1.1
- ✅ Flask-Login 0.6.3
- ✅ ReportLab 4.0.7 (PDF)
- ✅ Requests 2.31.0 (API IA)

**Modelos de Dados (COMPLETO)**
- ✅ Usuario (id, nome, email, senha_hash, perfil, setor, ativo)
- ✅ Documento (id, titulo, tipo_documento, arquivo_original, arquivo_publicado_pdf, codigo_provisorio, codigo_definitivo, data_criacao, data_publicacao, validade_anos, data_vencimento, status, texto_extraido, metadados_json)
- ✅ Tarefa (id, documento_id, criador_id, responsavel_id, tipo_tarefa, descricao, prazo, data_conclusao, parecer, aprovado)
- ✅ LogAI (id, documento_id, usuario_id, funcao_ia, parametros_json, resposta_json, sucesso, tempo_resposta_ms)

**Regras de Negócio (COMPLETO)**
- ✅ Criação de documento com status "Novo"
- ✅ Fluxo de análise com tarefas
- ✅ Publicação com PDF e código definitivo
- ✅ Rotina de vencimento automático
- ✅ 4 perfis de usuário com permissões

**Módulo de IA (COMPLETO)**
- ✅ Extração de texto (extract_text)
- ✅ Classificação (classify_document)
- ✅ Sumarização (summarize_text)
- ✅ Busca semântica (search_semantic)
- ✅ Sugestão de responsável (suggest_responsavel)
- ✅ Logs completos de auditoria

**Rotas Principais (COMPLETO)**
- ✅ Dashboard (/)
- ✅ Documento (/documento/<id>)
- ✅ Repositório Público (/publico)
- ✅ Relatórios PDF (/relatorio/pdf/*)
- ✅ Tarefas (/tarefa/*)
- ✅ IA (/ia/*)

**Funcionalidades Extras (COMPLETO)**
- ✅ Geração de relatórios PDF (3 tipos)
- ✅ Sistema de auditoria completo
- ✅ Templates HTML básicos
- ✅ Documentação completa
- ✅ Scripts de teste

---

## 📦 PASSO 1: PRÉ-REQUISITOS

### 1.1. Instalar Python 3.11+

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**macOS:**
```bash
brew install python@3.11
```

**Windows:**
- Baixe de https://www.python.org/downloads/
- Marque "Add Python to PATH" durante instalação

**Verificar instalação:**
```bash
python3 --version  # Deve mostrar Python 3.11.x ou superior
```

### 1.2. Instalar PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Windows:**
- Baixe de https://www.postgresql.org/download/windows/
- Use o instalador gráfico

**Verificar instalação:**
```bash
psql --version  # Deve mostrar PostgreSQL 12+ ou superior
```

### 1.3. Instalar Git (se ainda não tiver)

```bash
# Ubuntu/Debian
sudo apt install git

# macOS
brew install git

# Verificar
git --version
```

---

## 🔧 PASSO 2: CONFIGURAÇÃO DO BANCO DE DADOS

### 2.1. Criar usuário e banco PostgreSQL

**Linux/macOS:**
```bash
# Acessar console PostgreSQL
sudo -u postgres psql

# Ou no macOS:
psql postgres
```

**Windows:**
```cmd
# Abra SQL Shell (psql) do menu iniciar
```

**Executar no console PostgreSQL:**
```sql
-- Criar banco de dados
CREATE DATABASE ged_db;

-- Criar usuário
CREATE USER ged_user WITH PASSWORD 'ged_password';

-- Dar permissões
GRANT ALL PRIVILEGES ON DATABASE ged_db TO ged_user;

-- No PostgreSQL 15+, também execute:
\c ged_db
GRANT ALL ON SCHEMA public TO ged_user;

-- Sair
\q
```

### 2.2. Testar conexão

```bash
psql -h localhost -U ged_user -d ged_db -W
# Senha: ged_password
# Digite \q para sair
```

Se conectou com sucesso, está OK! ✅

---

## 📥 PASSO 3: BAIXAR E CONFIGURAR O PROJETO

### 3.1. Clonar ou baixar o projeto

Se você já tem o projeto local, pule para 3.2.

```bash
# Via Git
git clone <url-do-repositorio>
cd ged
```

### 3.2. Criar ambiente virtual Python

```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

Seu terminal deve mostrar `(venv)` no início da linha.

### 3.3. Instalar dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Aguarde alguns minutos.** Isso instalará:
- Flask e extensões
- PostgreSQL driver (psycopg2)
- ReportLab (PDF)
- Requests (IA)
- E outras bibliotecas

**Verificar instalação:**
```bash
pip list | grep Flask
# Deve mostrar: Flask, Flask-Login, Flask-SQLAlchemy, etc.
```

### 3.4. Configurar variáveis de ambiente

```bash
# Copiar exemplo
cp .env.example .env

# Editar .env
nano .env  # ou vim, ou notepad no Windows
```

**Configurar o arquivo .env:**
```bash
# Configuração do Flask
FLASK_ENV=development
SECRET_KEY=mude-para-uma-chave-secreta-aleatoria-em-producao

# Configuração do Banco de Dados PostgreSQL
DATABASE_URL=postgresql://ged_user:ged_password@localhost:5432/ged_db

# Configuração da API de IA (OPCIONAL para testes iniciais)
AI_API_BASE_URL=https://api.ia.meudominio.com
AI_API_KEY=sua-chave-aqui
AI_API_TIMEOUT=30

# Configurações de Upload
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=app/uploads/documentos
PUBLISHED_FOLDER=app/uploads/publicados

# Configurações de Documentos
VALIDADE_PADRAO_ANOS=5
DIAS_ALERTA_VENCIMENTO=30
```

**IMPORTANTE:**
- Se não tiver API de IA configurada, pode deixar os valores padrão. As funcionalidades de IA retornarão erro, mas o resto funciona normalmente.
- Mude `SECRET_KEY` para algo aleatório em produção.

---

## 🗄️ PASSO 4: INICIALIZAR BANCO DE DADOS

### 4.1. Criar tabelas

```bash
# Certifique-se de estar com ambiente virtual ativado (venv)
flask init-db
```

**Saída esperada:**
```
Banco de dados inicializado com sucesso!
```

### 4.2. Popular com dados iniciais

```bash
flask seed-db
```

**Saída esperada:**
```
Dados iniciais criados com sucesso!

Usuários criados:
  Admin:   admin@example.com    / admin123
  Gerente: gerente@example.com  / gerente123
  Usuário: usuario@example.com  / usuario123
```

### 4.3. Verificar se as tabelas foram criadas

```bash
psql -h localhost -U ged_user -d ged_db -W
```

```sql
-- Listar tabelas
\dt

-- Deve mostrar:
-- usuarios
-- documentos
-- tarefas
-- logs_ia

-- Ver usuários criados
SELECT id, nome, email, perfil FROM usuarios;

-- Sair
\q
```

---

## 🚀 PASSO 5: EXECUTAR O SISTEMA

### 5.1. Iniciar servidor Flask

```bash
# Certifique-se de estar na pasta raiz do projeto (ged/)
# e com ambiente virtual ativado (venv)

python app.py
```

**Saída esperada:**
```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://0.0.0.0:5000
Press CTRL+C to quit
```

**✅ SISTEMA RODANDO!**

Deixe este terminal aberto. Abra um novo terminal para os próximos passos.

### 5.2. Acessar interface web

Abra seu navegador em:
```
http://localhost:5000/home
```

Você deve ver a página de boas-vindas do Sistema GED!

---

## 🧪 PASSO 6: TESTAR O SISTEMA

### 6.1. Teste Rápido via cURL

**Abra um NOVO terminal** (deixe o servidor rodando no anterior):

```bash
# Teste 1: Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","senha":"admin123"}' \
  -c cookies.txt \
  -w "\nStatus: %{http_code}\n"

# Deve retornar status 200 e JSON com dados do usuário
```

```bash
# Teste 2: Ver informações do usuário
curl -X GET http://localhost:5000/auth/me \
  -b cookies.txt

# Deve retornar dados do admin
```

```bash
# Teste 3: Listar documentos
curl -X GET http://localhost:5000/documento/lista \
  -b cookies.txt

# Deve retornar array vazio (ainda não há documentos)
```

```bash
# Teste 4: Ver dashboard
curl -X GET http://localhost:5000/ \
  -b cookies.txt

# Deve retornar estatísticas
```

### 6.2. Teste Completo com Script Python

```bash
# Certifique-se de estar com venv ativado
python test_api.py
```

**Saída esperada:**
- Login bem-sucedido ✅
- Listagem de usuários ✅
- Dashboard carregado ✅
- Documento criado ✅
- Tarefa criada ✅
- Todos os testes passando!

### 6.3. Teste com Postman

1. Abra Postman
2. Importe `GED_API.postman_collection.json`
3. Execute a requisição "Login"
4. Teste outros endpoints

---

## 📊 PASSO 7: CRIAR DOCUMENTO DE TESTE

### 7.1. Criar arquivo de teste

```bash
echo "Este é um documento de exemplo para o Sistema GED.

PROCEDIMENTO OPERACIONAL PADRÃO - POP-001

1. Objetivo
Este documento descreve o procedimento de teste do sistema.

2. Escopo
Aplicável a todos os usuários do sistema.

3. Responsabilidades
- Gerente de Qualidade: Aprovar documento
- Usuários: Seguir procedimento

4. Procedimento
4.1. Acessar o sistema
4.2. Fazer login
4.3. Criar documento
4.4. Aguardar aprovação" > documento_teste.txt
```

### 7.2. Fazer upload via cURL

```bash
curl -X POST http://localhost:5000/documento/criar \
  -b cookies.txt \
  -F "titulo=POP - Procedimento de Teste" \
  -F "tipo_documento=POP" \
  -F "descricao=Documento de exemplo criado para teste do sistema" \
  -F "setor=Qualidade" \
  -F "validade_anos=5" \
  -F "arquivo=@documento_teste.txt"
```

**Saída esperada:**
```json
{
  "mensagem": "Documento criado com sucesso",
  "documento": {
    "id": 1,
    "codigo_provisorio": "POP-PROV-20241113...",
    "titulo": "POP - Procedimento de Teste",
    "status": "Novo"
  }
}
```

### 7.3. Visualizar documento criado

```bash
curl -X GET http://localhost:5000/documento/1 \
  -b cookies.txt
```

---

## 📋 PASSO 8: TESTAR FLUXO COMPLETO

### 8.1. Login como Gerente

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"gerente@example.com","senha":"gerente123"}' \
  -c cookies_gerente.txt
```

### 8.2. Criar Tarefa de Análise

```bash
curl -X POST http://localhost:5000/tarefa/criar \
  -b cookies_gerente.txt \
  -H "Content-Type: application/json" \
  -d '{
    "documento_id": 1,
    "responsavel_id": 3,
    "tipo_tarefa": "Analisar",
    "descricao": "Analisar conteúdo do documento de teste",
    "prioridade": "normal",
    "prazo": "2024-12-31T23:59:59"
  }'
```

### 8.3. Verificar Minhas Tarefas

```bash
# Login como usuário comum
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"usuario@example.com","senha":"usuario123"}' \
  -c cookies_usuario.txt

# Ver tarefas
curl -X GET http://localhost:5000/tarefa/minhas \
  -b cookies_usuario.txt
```

### 8.4. Concluir Tarefa

```bash
curl -X POST http://localhost:5000/tarefa/1/concluir \
  -b cookies_usuario.txt \
  -H "Content-Type: application/json" \
  -d '{
    "parecer": "Documento analisado e aprovado. Conteúdo está de acordo com as normas.",
    "aprovado": true
  }'
```

### 8.5. Gerar Relatório PDF

```bash
curl -X GET http://localhost:5000/relatorio/pdf/geral \
  -b cookies.txt \
  --output relatorio_sistema.pdf

# Abrir PDF
# Linux: xdg-open relatorio_sistema.pdf
# macOS: open relatorio_sistema.pdf
# Windows: start relatorio_sistema.pdf
```

---

## 🤖 PASSO 9: TESTAR INTEGRAÇÃO COM IA (OPCIONAL)

**NOTA:** Requer configuração de API de IA no .env

Se você configurou uma API de IA válida:

```bash
# Extrair texto do documento
curl -X POST http://localhost:5000/ia/extract/1 \
  -b cookies.txt

# Classificar documento
curl -X POST http://localhost:5000/ia/classify/1 \
  -b cookies.txt

# Resumir documento
curl -X POST http://localhost:5000/ia/summarize/1?max_length=200 \
  -b cookies.txt

# Busca semântica
curl -X POST http://localhost:5000/ia/search \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"query": "procedimentos de qualidade", "limit": 5}'
```

---

## ✅ VERIFICAÇÃO FINAL - CHECKLIST

Marque cada item conforme completar:

**Instalação:**
- [ ] Python 3.11+ instalado
- [ ] PostgreSQL instalado e rodando
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas (pip install -r requirements.txt)
- [ ] Arquivo .env configurado

**Banco de Dados:**
- [ ] Banco ged_db criado
- [ ] Usuário ged_user criado
- [ ] Permissões configuradas
- [ ] Tabelas criadas (flask init-db)
- [ ] Dados iniciais carregados (flask seed-db)
- [ ] 3 usuários visíveis no banco

**Sistema:**
- [ ] Servidor Flask rodando (python app.py)
- [ ] Interface web acessível (http://localhost:5000/home)
- [ ] Login funcionando (admin@example.com / admin123)
- [ ] Documento criado com sucesso
- [ ] Tarefa criada e concluída
- [ ] Relatório PDF gerado

**Testes:**
- [ ] Script test_api.py executado com sucesso
- [ ] cURL funcionando
- [ ] Postman collection importada e testada

---

## 🐛 SOLUÇÃO DE PROBLEMAS COMUNS

### Erro: "ModuleNotFoundError: No module named 'flask'"

**Solução:**
```bash
# Certifique-se de que o ambiente virtual está ativado
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Reinstale as dependências
pip install -r requirements.txt
```

### Erro: "psycopg2.OperationalError: could not connect to server"

**Solução:**
```bash
# Verifique se PostgreSQL está rodando
sudo systemctl status postgresql  # Linux
brew services list                # macOS

# Inicie PostgreSQL se necessário
sudo systemctl start postgresql   # Linux
brew services start postgresql@15 # macOS

# Verifique credenciais no .env
cat .env | grep DATABASE_URL
```

### Erro: "OSError: [Errno 98] Address already in use"

**Solução:**
```bash
# Porta 5000 já está em uso
# Opção 1: Matar processo na porta 5000
lsof -ti:5000 | xargs kill -9

# Opção 2: Usar outra porta
export FLASK_RUN_PORT=5001
python app.py
```

### Erro: "werkzeug.routing.BuildError"

**Solução:**
- Verifique se todos os blueprints estão registrados em app/__init__.py
- Certifique-se de que não há erros de sintaxe nos arquivos de rotas

### Erro: "sqlalchemy.exc.ProgrammingError: relation does not exist"

**Solução:**
```bash
# Recrie o banco de dados
flask init-db
flask seed-db
```

### API de IA retorna erro

**Solução:**
- Se não tiver API de IA configurada, é normal retornar erro
- Configure AI_API_BASE_URL e AI_API_KEY no .env
- Ou ignore funções de IA - o resto do sistema funciona normalmente

---

## 📚 DOCUMENTAÇÃO ADICIONAL

- **README.md** - Documentação completa da API
- **QUICKSTART.md** - Guia rápido de instalação
- **app/routes/** - Código das rotas com comentários
- **app/models/models.py** - Modelos de dados documentados
- **http://localhost:5000/home** - Documentação web

---

## 🎉 SISTEMA PRONTO PARA USO!

Se todos os testes passaram, seu Sistema GED está 100% funcional!

**Próximos passos sugeridos:**
1. Customize templates em `app/templates/`
2. Configure rotina automática de vencimento (cron)
3. Configure backup do PostgreSQL
4. Em produção: use gunicorn + nginx
5. Configure HTTPS em produção

**Para desenvolvimento:**
- Use Postman para testar endpoints visualmente
- Consulte logs em `logs/ged.log`
- Use `flask shell` para queries diretas no banco

**Comandos úteis:**
```bash
# Ver logs em tempo real
tail -f logs/ged.log

# Shell interativo
flask shell
>>> Usuario.query.all()
>>> Documento.query.count()

# Verificar vencimentos
flask verificar-vencimentos

# Resetar banco (CUIDADO!)
flask shell
>>> db.drop_all()
>>> db.create_all()
flask seed-db
```

---

## 💻 DESENVOLVIMENTO

**Estrutura de arquivos:**
```
app/
├── __init__.py          # Factory do Flask
├── models/              # Modelos de dados
│   ├── models.py        # Usuario, Documento, Tarefa, LogAI
│   └── __init__.py
├── routes/              # Rotas da API
│   ├── routes_auth.py   # Autenticação
│   ├── routes_documento.py  # Documentos
│   ├── routes_tarefa.py     # Tarefas
│   ├── routes_ia.py         # IA
│   ├── routes_dashboard.py  # Dashboard
│   └── __init__.py
├── services/            # Serviços auxiliares
│   ├── ai_client.py     # Cliente API de IA
│   ├── report_generator.py  # PDF
│   └── __init__.py
└── templates/           # HTML
    ├── base.html
    └── index.html
```

**Boas práticas:**
- Sempre ative o ambiente virtual antes de trabalhar
- Use git para versionar alterações
- Teste endpoints com Postman antes de integrar
- Consulte logs para debugging
- Faça backup do banco regularmente

---

**Sistema desenvolvido com Flask, PostgreSQL e integração com APIs de IA.**
**Versão: 1.0.0**
**Data: Novembro 2024**
