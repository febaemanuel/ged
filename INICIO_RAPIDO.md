# ⚡ INÍCIO RÁPIDO - GED EBSERH

Para implantação completa, veja **IMPLANTACAO.md**. 
Aqui está o guia de início rápido:

## 🚀 3 PASSOS PARA RODAR

### 1. Configurar Ambiente
```bash
# Clone o repositório
git clone https://github.com/febaemanuel/ged.git
cd ged

# Crie .env
cp .env.example .env

# Gere chaves (Cole no .env)
python3 -c 'import secrets; print("SECRET_KEY=" + secrets.token_hex(32))'
python3 -c 'import secrets; print("DB_PASSWORD=" + secrets.token_urlsafe(32))'
python3 -c 'import secrets; print("REDIS_PASSWORD=" + secrets.token_urlsafe(32))'

# Edite .env com as chaves geradas
nano .env
```

### 2. Deploy Automático
```bash
# Torna executável
chmod +x scripts/deploy.sh

# Executa deploy
sudo scripts/deploy.sh
```

### 3. Criar Admin
```bash
# Cria primeiro usuário
./scripts/create-admin.sh

# Acesse
curl http://localhost:5000/health
```

## ✅ PRONTO!

Acesse: **http://localhost:5000**

## 📚 Documentação Completa

- **IMPLANTACAO.md** - Guia completo de produção
- **SECURITY.md** - Segurança e hardening
- **README_ATUALIZACOES.md** - Changelog e melhorias

## 🛠️ Scripts Úteis

```bash
# Deploy
sudo scripts/deploy.sh

# Health check
./scripts/health-check.sh

# Criar admin
./scripts/create-admin.sh

# Backup
sudo scripts/backup.sh

# Ver logs
docker compose logs -f web

# Restart
docker compose restart
```

## 🔧 Variáveis Obrigatórias no .env

```env
SECRET_KEY=...          # 64 caracteres hexadecimais
DB_PASSWORD=...         # Senha PostgreSQL (forte)
REDIS_PASSWORD=...      # Senha Redis (forte)
DATABASE_URL=postgresql://ged_user:${DB_PASSWORD}@db:5432/ged_db
```

## 🆘 Problemas?

```bash
# Logs detalhados
docker compose logs -f

# Reiniciar tudo
docker compose down -v
docker compose up -d

# Health check
curl http://localhost:5000/health | jq
```

## 📊 Verificar Status

```bash
# Containers
docker compose ps

# Health check
./scripts/health-check.sh

# Banco de dados
docker compose exec db psql -U ged_user -d ged_db
```

---

**Próximo passo:** Veja **IMPLANTACAO.md** para produção com HTTPS
