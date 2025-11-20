# 🔧 Guia Rápido: Configurar Banco Separado para Evolution API

## ⚠️ PROBLEMA

Você está vendo este erro ao iniciar a Evolution API:

```
❌ Error: P3005
The database schema is not empty
```

**Causa:** A Evolution API está tentando usar o mesmo banco `ged` do sistema GED principal.

---

## ✅ SOLUÇÃO: Criar Banco Separado

### Passo 1: Criar o banco `evolution_db` no PostgreSQL

**Opção A: Pelo pgAdmin (Interface Gráfica)**

1. Abra o **pgAdmin**
2. Conecte ao servidor PostgreSQL (localhost)
3. Clique com botão direito em **Databases** → **Create** → **Database**
4. Preencha:
   - **Database:** `evolution_db`
   - **Owner:** `ged_user`
   - **Encoding:** `UTF8`
5. Clique em **Save**

**Opção B: Pelo SQL Shell (psql)**

1. Abra o **SQL Shell (psql)** do Windows
2. Conecte como `postgres` (ou seu usuário admin)
3. Execute os comandos:

```sql
-- Criar o banco
CREATE DATABASE evolution_db OWNER ged_user;

-- Conceder permissões
GRANT ALL PRIVILEGES ON DATABASE evolution_db TO ged_user;

-- Conectar ao novo banco
\c evolution_db

-- Dar permissões no schema
GRANT ALL ON SCHEMA public TO ged_user;

-- Sair
\q
```

**Opção C: Linha de comando única**

```bash
psql -U postgres -c "CREATE DATABASE evolution_db OWNER ged_user;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE evolution_db TO ged_user;"
psql -U postgres -d evolution_db -c "GRANT ALL ON SCHEMA public TO ged_user;"
```

---

### Passo 2: Verificar que o banco foi criado

```sql
-- Abra o psql novamente
psql -U postgres

-- Liste os bancos
\l
```

Você deve ver:

```
 ged          | ged_user  | UTF8     | ... | Sistema GED Principal
 evolution_db | ged_user  | UTF8     | ... | Evolution API (SEPARADO!)
```

---

### Passo 3: Configurar o `.env` da Evolution API

**Localize o arquivo `.env` da Evolution API** (onde ela está instalada, NÃO no projeto GED):

```bash
# Exemplo de localização:
# C:\Users\SeuUsuario\evolution-api\.env
# ou
# /home/user/evolution-api/.env
```

**Edite o arquivo `.env` e configure:**

```bash
# Banco de dados
DATABASE_ENABLED=true
DATABASE_PROVIDER=postgresql
DATABASE_CONNECTION_URI=postgresql://ged_user:ged_password@host.docker.internal:5432/evolution_db
DATABASE_CONNECTION_CLIENT_NAME=evolution_api_client
```

**⚠️ Pontos importantes:**

- Use `host.docker.internal` se a Evolution API estiver no Docker
- Use `localhost` se estiver rodando direto no Windows/Linux
- Confirme que a senha `ged_password` está correta
- **NÃO use o banco `ged`!** Use `evolution_db`

---

### Passo 4: Reiniciar a Evolution API

**Se estiver usando Docker:**

```bash
cd /caminho/da/evolution-api
docker-compose down
docker-compose up -d
```

**Se estiver rodando com Node.js:**

```bash
# Pare o servidor (Ctrl+C)
npm start
```

---

### Passo 5: Verificar se funcionou

**Veja os logs da Evolution API:**

```bash
# Docker
docker logs evolution-api

# Ou se tiver nome diferente
docker logs nome-do-container-evolution
```

**✅ Sucesso! Você deve ver:**

```
✅ Conectando ao PostgreSQL...
✅ Datasource "db": PostgreSQL database "evolution_db" at "host.docker.internal:5432"
✅ Database schema created successfully
✅ Server is running on http://localhost:8080
```

**❌ Se ainda der erro:**

```
❌ Error: P3005 - The database schema is not empty
```

→ Verifique se o `.env` da Evolution API tem `evolution_db` (não `ged`)

---

## 📊 Resumo da Arquitetura

```
┌─────────────────────────────────────────┐
│         PostgreSQL Server               │
│         (host.docker.internal:5432)     │
├─────────────────────────────────────────┤
│                                         │
│  📦 Banco: ged                          │
│     ├─ Tabela: usuarios                │
│     ├─ Tabela: documentos              │
│     ├─ Tabela: assinaturas             │
│     └─ ... (todas do Sistema GED)      │
│                                         │
│  📦 Banco: evolution_db (SEPARADO!)    │
│     ├─ Tabela: instances               │
│     ├─ Tabela: messages                │
│     ├─ Tabela: webhooks                │
│     └─ ... (todas da Evolution API)    │
│                                         │
└─────────────────────────────────────────┘
         ▲                    ▲
         │                    │
   Sistema GED          Evolution API
   (Flask/Python)       (Node.js)
```

---

## 🔍 Checklist Final

- [ ] Banco `evolution_db` criado no PostgreSQL
- [ ] Usuário `ged_user` tem permissões no `evolution_db`
- [ ] `.env` da Evolution API aponta para `evolution_db`
- [ ] Evolution API reiniciada
- [ ] Logs mostram conexão bem-sucedida
- [ ] Teste de envio de mensagem funciona

---

## ❓ Precisa de Ajuda?

Consulte o **GUIA_EVOLUTION_API.md** completo para mais detalhes e troubleshooting.

Se ainda tiver problemas, verifique:

1. Se o PostgreSQL está aceitando conexões: `psql -U ged_user -d evolution_db`
2. Se a senha está correta
3. Se o firewall não está bloqueando a porta 5432
4. Os logs da Evolution API: `docker logs evolution-api`

---

**Desenvolvido para Sistema GED EBSERH**
**Data:** Novembro 2025
