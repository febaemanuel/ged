# Sistema GED - Gerenciador Eletrônico de Documentos

Sistema completo de gerenciamento eletrônico de documentos (POPs, Manuais, Protocolos) com fluxo de aprovação manual e recursos de IA integrados via API externa.

## 🚀 Stack Tecnológica

- **Linguagem:** Python 3.11+
- **Framework:** Flask
- **Banco de Dados:** PostgreSQL
- **ORM:** Flask-SQLAlchemy + psycopg2
- **Relatórios:** ReportLab
- **Autenticação:** Flask-Login
- **Comunicação com IA:** API externa REST

## 📁 Estrutura do Projeto

```
ged/
├── app/
│   ├── models/          # Modelos SQLAlchemy (Usuario, Documento, Tarefa)
│   ├── routes/          # Rotas da API REST
│   ├── services/        # Serviços (IA client, relatórios)
│   ├── templates/       # Templates HTML básicos
│   ├── static/          # Arquivos estáticos
│   ├── uploads/         # Upload de documentos
│   └── __init__.py      # Inicialização do app
├── config.py            # Configurações
├── app.py               # Ponto de entrada
├── requirements.txt     # Dependências Python
└── README.md           # Este arquivo
```

## ⚙️ Instalação

### 1. Clone o repositório

```bash
git clone <repository-url>
cd ged
```

### 2. Crie ambiente virtual Python

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Instale dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o PostgreSQL

Crie um banco de dados PostgreSQL:

```sql
CREATE DATABASE ged_db;
CREATE USER ged_user WITH PASSWORD 'ged_password';
GRANT ALL PRIVILEGES ON DATABASE ged_db TO ged_user;
```

### 5. Configure variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e configure:

```bash
cp .env.example .env
```

Edite `.env` com suas configurações:

```
DATABASE_URL=postgresql://ged_user:ged_password@localhost:5432/ged_db
SECRET_KEY=your-secret-key-here
AI_API_BASE_URL=https://api.ia.meudominio.com
AI_API_KEY=your-api-key-here
```

### 6. Inicialize o banco de dados

```bash
flask init-db
flask seed-db
```

Isso criará as tabelas e usuários padrão:
- **Admin:** admin@example.com / admin123
- **Gerente:** gerente@example.com / gerente123
- **Usuário:** usuario@example.com / usuario123

### 7. Execute a aplicação

```bash
flask run
# ou
python app.py
```

O servidor estará rodando em `http://localhost:5000`

## 🔐 Perfis de Usuário

### Comum
- Cria documentos
- Executa tarefas atribuídas

### Gerente
- Gerencia documentos do setor
- Cria e designa tarefas
- Aciona funções de IA

### Responsável Interno
- Gerencia fluxo de documentos específicos
- Aprova documentos

### Administrador
- Gerencia usuários e configurações
- Acesso total ao sistema

## 📋 Fluxo de Trabalho

### 1. Criação de Documento
- Usuário faz upload de arquivo (.doc, .odt)
- Sistema gera código provisório
- Status: **Novo**

### 2. Análise e Aprovação
- Gerente cria tarefas de análise
- Responsáveis executam tarefas
- Status: **Em Análise** → **Aprovado**

### 3. Publicação
- Tarefa de publicação anexa PDF final
- Sistema gera código definitivo
- Calcula data de vencimento
- Status: **Aprovado e Publicado**

### 4. Controle de Vencimento
- Rotina automática verifica vencimentos
- Documentos vencidos: **Obsoleto**

## 🤖 Funcionalidades de IA

Todas as funcionalidades de IA são processadas por API externa.

### Extração de Texto
```bash
POST /ia/extract/<id>
```
Extrai texto de documentos .doc, .odt, .pdf

### Classificação
```bash
POST /ia/classify/<id>
```
Classifica tipo de documento (POP, Manual, Protocolo)

### Sumarização
```bash
POST /ia/summarize/<id>
```
Gera resumo do conteúdo

### Busca Semântica
```bash
POST /ia/search
```
Busca documentos por similaridade conceitual

### Sugestão de Responsável
```bash
POST /ia/suggest_responsavel
```
Sugere responsável ideal baseado em histórico

## 🌐 API REST - Principais Endpoints

### Autenticação

```bash
# Login
POST /auth/login
{
  "email": "admin@example.com",
  "senha": "admin123"
}

# Logout
POST /auth/logout

# Informações do usuário atual
GET /auth/me

# Registrar novo usuário (admin apenas)
POST /auth/register
```

### Documentos

```bash
# Listar documentos
GET /documento/lista?status=Novo&tipo=POP&page=1

# Visualizar documento e timeline
GET /documento/<id>

# Criar documento
POST /documento/criar
Form data: titulo, tipo_documento, arquivo, setor

# Atualizar documento
PUT /documento/<id>

# Download
GET /documento/<id>/download/original
GET /documento/<id>/download/publicado

# Repositório público
GET /documento/publico?q=termo&tipo=POP
```

### Tarefas

```bash
# Minhas tarefas
GET /tarefa/minhas

# Listar tarefas
GET /tarefa/lista?concluida=false

# Visualizar tarefa
GET /tarefa/<id>

# Criar tarefa
POST /tarefa/criar
{
  "documento_id": 1,
  "responsavel_id": 2,
  "tipo_tarefa": "Analisar",
  "prazo": "2024-12-31T23:59:59"
}

# Concluir tarefa
POST /tarefa/<id>/concluir
{
  "parecer": "Documento aprovado",
  "aprovado": true
}

# Tarefas atrasadas
GET /tarefa/atrasadas
```

### IA

```bash
# Extrair texto
POST /ia/extract/<id>

# Classificar documento
POST /ia/classify/<id>

# Resumir documento
POST /ia/summarize/<id>?max_length=500

# Busca semântica
POST /ia/search
{
  "query": "procedimentos de segurança",
  "limit": 10
}

# Sugerir responsável
POST /ia/suggest_responsavel
{
  "tipo_documento": "POP",
  "setor": "Qualidade"
}

# Logs de IA
GET /ia/logs/<documento_id>

# Estatísticas de uso da IA
GET /ia/stats
```

### Dashboard e Relatórios

```bash
# Dashboard principal
GET /

# Estatísticas
GET /dashboard/stats

# Buscar documentos
GET /search?q=termo

# Preview de relatórios (JSON)
GET /relatorio/preview/tarefas_atrasadas
GET /relatorio/preview/documentos_vencendo?dias=30
GET /relatorio/preview/geral

# Relatórios PDF
GET /relatorio/pdf/tarefas_atrasadas
GET /relatorio/pdf/documentos_vencendo?dias=30
GET /relatorio/pdf/geral
```

### Rotinas Automáticas

```bash
# Verificar documentos vencidos
POST /rotina/verificar_vencimentos

# Via CLI
flask verificar-vencimentos
```

## 📊 Exemplos de Uso (cURL)

### Login
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "senha": "admin123"}' \
  -c cookies.txt
```

### Criar Documento
```bash
curl -X POST http://localhost:5000/documento/criar \
  -b cookies.txt \
  -F "titulo=Procedimento de Limpeza" \
  -F "tipo_documento=POP" \
  -F "setor=Operações" \
  -F "arquivo=@/path/to/documento.doc"
```

### Listar Tarefas Pendentes
```bash
curl -X GET http://localhost:5000/tarefa/minhas \
  -b cookies.txt
```

### Extrair Texto com IA
```bash
curl -X POST http://localhost:5000/ia/extract/1 \
  -b cookies.txt
```

### Gerar Relatório PDF
```bash
curl -X GET http://localhost:5000/relatorio/pdf/tarefas_atrasadas \
  -b cookies.txt \
  --output relatorio.pdf
```

## 🔒 Segurança e Auditoria

- Todas as chamadas à API de IA são registradas em `LogAI`
- Comunicação HTTPS obrigatória em produção
- Campos `texto_extraido` e `metadados_json` são auditáveis
- Apenas Gerentes e Administradores podem acionar funções de IA
- Senhas armazenadas com hash (Werkzeug)

## 📝 Comandos CLI

```bash
# Inicializar banco de dados
flask init-db

# Popular com dados iniciais
flask seed-db

# Verificar documentos vencidos
flask verificar-vencimentos

# Shell interativo com contexto
flask shell
>>> Usuario.query.all()
>>> Documento.query.filter_by(status='Novo').count()
```

## 🐳 Docker (Opcional)

Crie um `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y postgresql-client

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

E um `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ged_db
      POSTGRES_USER: ged_user
      POSTGRES_PASSWORD: ged_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      DATABASE_URL: postgresql://ged_user:ged_password@db:5432/ged_db
      FLASK_ENV: development
    depends_on:
      - db
    volumes:
      - ./app/uploads:/app/app/uploads

volumes:
  postgres_data:
```

Execute com:
```bash
docker-compose up
```

## 🧪 Testes

Para executar testes (configurar posteriormente):

```bash
pytest tests/
```

## 📚 Documentação da API

Visite `http://localhost:5000/home` para ver a documentação básica.

## 🤝 Contribuindo

1. Faça fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é proprietário e confidencial.

## 👥 Autores

Desenvolvido para gerenciamento de documentos institucionais.

## 📞 Suporte

Para suporte, entre em contato com o administrador do sistema.
