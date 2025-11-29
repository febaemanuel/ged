# Guia Docker - Sistema GED EBSERH

## 📋 Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+
- 2GB RAM disponível (mínimo)
- 10GB espaço em disco

## 🚀 Início Rápido

### 1. Configurar Variáveis de Ambiente

```bash
# Copiar template de variáveis
cp .env.docker .env

# Editar variáveis (IMPORTANTE!)
nano .env
```

**⚠️ OBRIGATÓRIO:** Altere estas variáveis em `.env`:

```bash
# Gerar SECRET_KEY forte (execute e copie o resultado)
python -c 'import secrets; print(secrets.token_hex(32))'

# Cole o valor no .env
SECRET_KEY=sua_chave_super_secreta_aqui

# Trocar senha do banco
DB_PASSWORD=sua_senha_forte_aqui
```

### 2. Iniciar Aplicação

```bash
# Subir todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Apenas logs da aplicação web
docker-compose logs -f web
```

### 3. Acessar Sistema

- **Aplicação:** http://localhost:5000
- **Health Check:** http://localhost:5000/health
- **PostgreSQL:** localhost:5432

### 4. Criar Usuários Iniciais

```bash
# Executar script de seed
docker-compose exec web flask seed-db

# Salvar as credenciais exibidas!
```

## 🛠️ Comandos Úteis

### Gerenciamento de Containers

```bash
# Parar serviços
docker-compose stop

# Parar e remover containers
docker-compose down

# Parar e remover TUDO (incluindo volumes - CUIDADO!)
docker-compose down -v

# Reiniciar apenas a aplicação web
docker-compose restart web

# Ver status dos serviços
docker-compose ps
```

### Logs e Debug

```bash
# Logs em tempo real
docker-compose logs -f

# Últimas 100 linhas
docker-compose logs --tail=100

# Logs do PostgreSQL
docker-compose logs -f db
```

### Banco de Dados

```bash
# Acessar PostgreSQL via CLI
docker-compose exec db psql -U ged_user -d ged_db

# Backup do banco
docker-compose exec db pg_dump -U ged_user ged_db > backup_$(date +%Y%m%d).sql

# Restaurar backup
cat backup.sql | docker-compose exec -T db psql -U ged_user -d ged_db

# Verificar conexão
docker-compose exec web python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.session.execute('SELECT 1'); print('✓ Conectado!')"
```

### Comandos Flask

```bash
# Abrir shell Flask
docker-compose exec web flask shell

# Criar tabelas do banco
docker-compose exec web flask init-db

# Verificar documentos vencidos
docker-compose exec web flask verificar-vencimentos

# Executar comando Python
docker-compose exec web python -c "print('Hello from container')"
```

### Gerenciamento de Volumes

```bash
# Listar volumes
docker volume ls | grep ged

# Inspecionar volume
docker volume inspect ged_postgres_data

# Limpar volumes não utilizados (CUIDADO!)
docker volume prune
```

## 🔧 Desenvolvimento com Docker

### Hot Reload (Desenvolvimento)

Use o arquivo `docker-compose.dev.yml` para ativar hot reload:

```bash
# Iniciar em modo desenvolvimento
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Código da aplicação será montado como volume
# Mudanças no código Python recarregam automaticamente
```

### Rebuild da Imagem

Após alterar `requirements.txt` ou `Dockerfile`:

```bash
# Rebuild da imagem
docker-compose build

# Rebuild sem cache
docker-compose build --no-cache

# Rebuild e reiniciar
docker-compose up -d --build
```

### Executar Testes

```bash
# Executar testes dentro do container
docker-compose exec web pytest

# Com coverage
docker-compose exec web pytest --cov=app

# Testes específicos
docker-compose exec web pytest tests/test_auth.py
```

## 🌐 Evolution API (WhatsApp) - OPCIONAL

Para habilitar integração WhatsApp:

### 1. Descomente no `docker-compose.yml`

```yaml
# Remover comentários das linhas 62-78
evolution-api:
  image: atendai/evolution-api:latest
  # ... resto da configuração
```

### 2. Configurar `.env`

```bash
# Gerar chave para Evolution API
python -c 'import secrets; print(secrets.token_urlsafe(32))'

# Adicionar no .env
EVOLUTION_API_KEY=sua_chave_evolution_api
EVOLUTION_INSTANCE_NAME=ged-instance
```

### 3. Iniciar Evolution API

```bash
docker-compose up -d evolution-api

# Acessar painel
# http://localhost:8080
```

## 📊 Monitoramento

### Health Checks

```bash
# Verificar saúde da aplicação
curl http://localhost:5000/health

# Verificar PostgreSQL
docker-compose exec db pg_isready -U ged_user

# Verificar logs de erro
docker-compose logs web | grep ERROR
```

### Uso de Recursos

```bash
# Ver uso de CPU/RAM
docker stats

# Apenas containers do GED
docker stats $(docker ps --filter "name=ged_" -q)
```

## 🔒 Segurança em Produção

### ✅ Checklist de Segurança

- [ ] `SECRET_KEY` forte e única (min. 32 caracteres)
- [ ] `DB_PASSWORD` forte e única
- [ ] `FLASK_ENV=production` no `.env`
- [ ] Firewall configurado (apenas portas necessárias)
- [ ] Backup automático do banco configurado
- [ ] SSL/TLS configurado (HTTPS)
- [ ] Logs sendo monitorados
- [ ] Versões do Docker atualizadas

### Configurar HTTPS (Nginx Reverse Proxy)

Adicione ao `docker-compose.yml`:

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - web
    networks:
      - ged_network
```

## 🐛 Troubleshooting

### Problema: Container não inicia

```bash
# Ver logs detalhados
docker-compose logs web

# Verificar configuração
docker-compose config

# Verificar portas em uso
sudo netstat -tulpn | grep 5000
```

### Problema: Erro de conexão com banco

```bash
# Verificar se PostgreSQL está rodando
docker-compose ps db

# Ver logs do PostgreSQL
docker-compose logs db

# Testar conexão manualmente
docker-compose exec web python -c "
from sqlalchemy import create_engine
import os
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    result = conn.execute('SELECT 1')
    print('✓ Conexão OK')
"
```

### Problema: Permissão negada em volumes

```bash
# Corrigir permissões
docker-compose exec web chown -R geduser:geduser /app

# Ou reconstruir
docker-compose down
docker-compose up -d --build
```

### Problema: Arquivo .env não carregado

```bash
# Verificar se .env existe
ls -la .env

# Recriar containers
docker-compose down
docker-compose up -d
```

## 📦 Backup e Restore

### Backup Completo

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup do banco
docker-compose exec -T db pg_dump -U ged_user ged_db > $BACKUP_DIR/database.sql

# Backup dos uploads
docker cp ged_web:/app/app/uploads $BACKUP_DIR/uploads
docker cp ged_web:/app/uploads/assinaturas $BACKUP_DIR/assinaturas

# Backup do .env
cp .env $BACKUP_DIR/.env.backup

echo "✓ Backup completo em: $BACKUP_DIR"
```

### Restore

```bash
#!/bin/bash
# restore.sh

BACKUP_DIR=$1

# Restore banco
cat $BACKUP_DIR/database.sql | docker-compose exec -T db psql -U ged_user ged_db

# Restore uploads
docker cp $BACKUP_DIR/uploads ged_web:/app/app/
docker cp $BACKUP_DIR/assinaturas ged_web:/app/uploads/

echo "✓ Restore completo de: $BACKUP_DIR"
```

## 📝 Variáveis de Ambiente Completas

Todas as variáveis disponíveis em `.env`:

```bash
# Flask
FLASK_ENV=production          # production, development, testing
FLASK_APP=app.py

# Segurança
SECRET_KEY=                   # OBRIGATÓRIO: min. 32 caracteres

# Banco de Dados
DB_PASSWORD=                  # OBRIGATÓRIO: senha forte
DB_PORT=5432

# Portas
WEB_PORT=5000
EVOLUTION_PORT=8080

# AI (DeepSeek) - OPCIONAL
AI_API_BASE_URL=https://api.deepseek.com
AI_API_KEY=
AI_API_MODEL=deepseek-chat
AI_API_TIMEOUT=30

# Email (SMTP) - OPCIONAL
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=

# WhatsApp (Evolution API) - OPCIONAL
EVOLUTION_API_URL=http://evolution-api:8080
EVOLUTION_API_KEY=
EVOLUTION_INSTANCE_NAME=ged-instance
```

## 🎯 Performance

### Otimização de Recursos

```yaml
# Em docker-compose.yml, adicionar limites
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M

  db:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### Aumentar Workers Gunicorn

```bash
# Editar docker-compose.yml
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "8", "--timeout", "120", "app:app"]

# Regra: (2 x CPU cores) + 1
```

## 🆘 Suporte

- **Documentação:** README.md
- **Issues:** https://github.com/febaemanuel/ged/issues
- **Logs:** `/app/logs/ged.log` dentro do container

---

**Última atualização:** 2025-01-29
