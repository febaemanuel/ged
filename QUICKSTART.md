# Quickstart - Sistema GED

Guia rápido para colocar o sistema em funcionamento.

## ⚡ Setup Rápido (Linux/Mac)

```bash
# 1. Execute o script de setup
./setup.sh

# 2. Configure PostgreSQL
sudo -u postgres psql
CREATE DATABASE ged_db;
CREATE USER ged_user WITH PASSWORD 'ged_password';
GRANT ALL PRIVILEGES ON DATABASE ged_db TO ged_user;
\q

# 3. Edite .env com suas configurações
nano .env

# 4. Ative ambiente virtual
source venv/bin/activate

# 5. Inicialize o banco
flask init-db
flask seed-db

# 6. Execute o servidor
python app.py
```

## 🪟 Setup Rápido (Windows)

```powershell
# 1. Crie ambiente virtual
python -m venv venv
venv\Scripts\activate

# 2. Instale dependências
pip install -r requirements.txt

# 3. Configure PostgreSQL (via pgAdmin ou psql)
CREATE DATABASE ged_db;
CREATE USER ged_user WITH PASSWORD 'ged_password';
GRANT ALL PRIVILEGES ON DATABASE ged_db TO ged_user;

# 4. Copie e edite .env
copy .env.example .env
notepad .env

# 5. Inicialize banco
flask init-db
flask seed-db

# 6. Execute servidor
python app.py
```

## 🔑 Credenciais Padrão

Após executar `flask seed-db`:

| Perfil | Email | Senha |
|--------|-------|-------|
| Administrador | admin@example.com | admin123 |
| Gerente | gerente@example.com | gerente123 |
| Usuário | usuario@example.com | usuario123 |

## 🧪 Testar a API

### Opção 1: Script Python

```bash
python test_api.py
```

### Opção 2: Postman

1. Importe `GED_API.postman_collection.json` no Postman
2. Execute a requisição "Login"
3. Teste os demais endpoints

### Opção 3: cURL

```bash
# Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","senha":"admin123"}' \
  -c cookies.txt

# Listar documentos
curl -X GET http://localhost:5000/documento/lista \
  -b cookies.txt

# Dashboard
curl -X GET http://localhost:5000/ \
  -b cookies.txt
```

## 📊 Fluxo de Uso Básico

### 1. Criar Documento

```bash
curl -X POST http://localhost:5000/documento/criar \
  -b cookies.txt \
  -F "titulo=Procedimento XYZ" \
  -F "tipo_documento=POP" \
  -F "setor=Qualidade" \
  -F "arquivo=@documento.doc"
```

### 2. Criar Tarefa de Análise

```bash
curl -X POST http://localhost:5000/tarefa/criar \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{
    "documento_id": 1,
    "responsavel_id": 2,
    "tipo_tarefa": "Analisar",
    "prazo": "2024-12-31T23:59:59"
  }'
```

### 3. Visualizar Minhas Tarefas

```bash
curl -X GET http://localhost:5000/tarefa/minhas \
  -b cookies.txt
```

### 4. Concluir Tarefa

```bash
curl -X POST http://localhost:5000/tarefa/1/concluir \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{
    "parecer": "Documento aprovado",
    "aprovado": true
  }'
```

### 5. Gerar Relatório PDF

```bash
curl -X GET http://localhost:5000/relatorio/pdf/tarefas_atrasadas \
  -b cookies.txt \
  --output relatorio.pdf
```

## 🤖 Usar Funcionalidades de IA

Funcionalidades de IA requerem configuração da API externa no `.env`:

```bash
AI_API_BASE_URL=https://api.ia.meudominio.com
AI_API_KEY=sua-chave-aqui
```

Exemplos:

```bash
# Extrair texto do documento
curl -X POST http://localhost:5000/ia/extract/1 \
  -b cookies.txt

# Classificar documento
curl -X POST http://localhost:5000/ia/classify/1 \
  -b cookies.txt

# Busca semântica
curl -X POST http://localhost:5000/ia/search \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"query": "procedimentos de segurança", "limit": 10}'
```

## 🛠️ Comandos Úteis

```bash
# Shell interativo com contexto do banco
flask shell

# Verificar documentos vencidos
flask verificar-vencimentos

# Ver logs
tail -f logs/ged.log

# Resetar banco de dados
flask shell
>>> db.drop_all()
>>> db.create_all()
>>> exit()
flask seed-db
```

## 🐛 Troubleshooting

### Erro de conexão com banco

```bash
# Verifique se PostgreSQL está rodando
sudo systemctl status postgresql

# Teste conexão
psql -h localhost -U ged_user -d ged_db
```

### Erro "ModuleNotFoundError"

```bash
# Certifique-se de que o ambiente virtual está ativado
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstale dependências
pip install -r requirements.txt
```

### Porta 5000 em uso

```bash
# Mude a porta no app.py:
app.run(debug=True, host='0.0.0.0', port=5001)

# Ou use variável de ambiente:
export FLASK_RUN_PORT=5001
flask run
```

## 📚 Próximos Passos

- Leia o [README.md](README.md) completo para documentação detalhada
- Explore a API em: http://localhost:5000/home
- Configure a integração com API de IA
- Customize templates em `app/templates/`
- Ajuste configurações em `config.py`

## 💡 Dicas

1. Use Postman ou Insomnia para explorar a API visualmente
2. Configure rotinas automáticas (cron) para `flask verificar-vencimentos`
3. Em produção, use gunicorn ou uWSGI ao invés de `flask run`
4. Configure HTTPS em produção
5. Faça backups regulares do banco de dados

## 🆘 Precisa de Ajuda?

Consulte:
- [README.md](README.md) - Documentação completa
- Código-fonte em `app/routes/` - Exemplos de uso
- Logs em `logs/ged.log` - Para debugging
