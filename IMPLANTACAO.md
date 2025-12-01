# 🚀 GUIA DE IMPLANTAÇÃO - SISTEMA GED EBSERH

## 📋 PRÉ-REQUISITOS

### Servidor/Ambiente
- [ ] **SO:** Ubuntu 22.04 LTS / Debian 11+ / CentOS 8+
- [ ] **RAM:** Mínimo 4GB (Recomendado: 8GB)
- [ ] **CPU:** Mínimo 2 cores (Recomendado: 4 cores)
- [ ] **Disco:** Mínimo 50GB (SSD recomendado)
- [ ] **Docker:** v24.0+
- [ ] **Docker Compose:** v2.20+
- [ ] **Git:** Instalado

### Domínio e Certificado SSL
- [ ] Domínio configurado (ex: ged.hospital.gov.br)
- [ ] Certificado SSL/TLS válido (Let's Encrypt ou comercial)
- [ ] Portas abertas: 80, 443

---

## 🔧 PASSO 1: PREPARAR SERVIDOR

### 1.1 Atualizar Sistema
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### 1.2 Instalar Docker
```bash
# Remover versões antigas
sudo apt remove docker docker-engine docker.io containerd runc

# Instalar dependências
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Adicionar chave GPG do Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Adicionar repositório
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verificar instalação
docker --version
docker compose version

# Adicionar usuário ao grupo docker (evitar usar sudo)
sudo usermod -aG docker $USER
newgrp docker
```

### 1.3 Configurar Firewall
```bash
# UFW (Ubuntu/Debian)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp  # SSH
sudo ufw enable

# Firewalld (CentOS/RHEL)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

---

## 📦 PASSO 2: CLONAR REPOSITÓRIO

```bash
# Clone o repositório
cd /opt
sudo git clone https://github.com/febaemanuel/ged.git
cd ged

# Checkout na branch com correções
git checkout claude/code-review-analysis-01657rLCoZuHUNxhvnB1pUB8

# Defina permissões
sudo chown -R $USER:$USER /opt/ged
```

---

## 🔐 PASSO 3: CONFIGURAR VARIÁVEIS DE AMBIENTE

### 3.1 Criar arquivo .env
```bash
cd /opt/ged
cp .env.example .env
```

### 3.2 Gerar Chaves Seguras
```bash
# 1. SECRET_KEY (64 caracteres hexadecimais)
python3 -c 'import secrets; print("SECRET_KEY=" + secrets.token_hex(32))'

# 2. DB_PASSWORD (senha do PostgreSQL)
python3 -c 'import secrets; print("DB_PASSWORD=" + secrets.token_urlsafe(32))'

# 3. REDIS_PASSWORD (senha do Redis)
python3 -c 'import secrets; print("REDIS_PASSWORD=" + secrets.token_urlsafe(32))'

# 4. BACKUP_ENCRYPTION_KEY (criptografia de backups)
python3 -c 'from cryptography.fernet import Fernet; print("BACKUP_ENCRYPTION_KEY=" + Fernet.generate_key().decode())'
```

### 3.3 Editar .env com as Chaves
```bash
nano .env
```

**Preencha TODAS as variáveis:**
```env
# OBRIGATÓRIO
FLASK_ENV=production
SECRET_KEY=<cole_a_chave_gerada_acima>
DB_PASSWORD=<cole_a_senha_do_postgres>
REDIS_PASSWORD=<cole_a_senha_do_redis>
DATABASE_URL=postgresql://ged_user:<DB_PASSWORD>@db:5432/ged_db

# IA (opcional mas recomendado)
AI_API_KEY=sk-seu-api-key-deepseek

# EMAIL (configure com seu servidor SMTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=seu-email@hospital.gov.br
MAIL_PASSWORD=sua-senha-de-app

# BACKUP
BACKUP_ENCRYPTION_KEY=<cole_a_chave_fernet>
```

**Salve e feche:** `Ctrl+X` → `Y` → `Enter`

---

## 🏗️ PASSO 4: CONSTRUIR E SUBIR CONTAINERS

### 4.1 Build das Imagens
```bash
cd /opt/ged

# Build (primeira vez demora ~5-10 min)
docker compose build

# Verifique se não há erros
echo "✅ Build concluído"
```

### 4.2 Iniciar Serviços
```bash
# Sobe todos os containers em background
docker compose up -d

# Monitore os logs (Ctrl+C para sair)
docker compose logs -f
```

### 4.3 Verificar Status
```bash
# Status dos containers
docker compose ps

# Deve mostrar todos como "running" (healthy):
# - ged_db (PostgreSQL)
# - ged_redis (Redis)
# - ged_web (Flask)
# - ged_celery_worker (Worker)
# - ged_celery_beat (Scheduler)
```

---

## ✅ PASSO 5: VALIDAR INSTALAÇÃO

### 5.1 Health Check
```bash
# Teste endpoint de saúde
curl http://localhost:5000/health | jq

# Resposta esperada:
# {
#   "status": "healthy",
#   "checks": {
#     "database": "ok",
#     "redis": "ok",
#     "celery_workers": "1 active",
#     "disk_free": "XX.X%"
#   }
# }
```

### 5.2 Verificar Logs
```bash
# Logs da aplicação
docker compose logs web | tail -50

# Logs do Celery
docker compose logs celery_worker | tail -50

# Logs do PostgreSQL
docker compose logs db | tail -50
```

### 5.3 Criar Usuário Admin
```bash
# Acesse o container
docker compose exec web bash

# Entre no shell Python
python3
```

```python
# No shell Python:
from app import create_app
from app.models import db, Usuario

app = create_app('production')
with app.app_context():
    # Crie admin
    admin = Usuario(
        nome='Administrador',
        email='admin@hospital.gov.br',
        perfil='administrador',
        ativo=True
    )
    admin.set_password('SenhaForte@2025')  # MUDE ISSO!
    
    db.session.add(admin)
    db.session.commit()
    
    print(f"✅ Admin criado: {admin.email}")
    exit()
```

```bash
# Saia do container
exit
```

---

## 🌐 PASSO 6: CONFIGURAR NGINX (Proxy Reverso)

### 6.1 Instalar Nginx
```bash
sudo apt install nginx -y
```

### 6.2 Configurar Site
```bash
sudo nano /etc/nginx/sites-available/ged
```

**Cole esta configuração:**
```nginx
server {
    listen 80;
    server_name ged.hospital.gov.br;  # SEU DOMÍNIO

    # Redireciona HTTP → HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ged.hospital.gov.br;  # SEU DOMÍNIO

    # Certificados SSL
    ssl_certificate /etc/letsencrypt/live/ged.hospital.gov.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ged.hospital.gov.br/privkey.pem;

    # Configurações SSL (Mozilla Modern)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logs
    access_log /var/log/nginx/ged_access.log;
    error_log /var/log/nginx/ged_error.log;

    # Proxy para Flask
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # WebSocket support (se necessário)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Aumenta limite de upload
    client_max_body_size 20M;
}
```

### 6.3 Ativar Site
```bash
# Cria link simbólico
sudo ln -s /etc/nginx/sites-available/ged /etc/nginx/sites-enabled/

# Testa configuração
sudo nginx -t

# Reinicia Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

## 🔒 PASSO 7: CERTIFICADO SSL (Let's Encrypt)

### 7.1 Instalar Certbot
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 7.2 Obter Certificado
```bash
# ANTES: Certifique-se que o domínio aponta para o servidor!

sudo certbot --nginx -d ged.hospital.gov.br

# Siga as instruções:
# - Email para renovações
# - Aceite termos
# - Escolha "2" para redirecionar HTTP → HTTPS
```

### 7.3 Auto-Renovação
```bash
# Testa renovação
sudo certbot renew --dry-run

# Cron job (já configurado automaticamente)
sudo systemctl status certbot.timer
```

---

## 📊 PASSO 8: MONITORAMENTO

### 8.1 Health Check Automático
```bash
# Crie script de monitoramento
sudo nano /usr/local/bin/ged-health-check.sh
```

```bash
#!/bin/bash
STATUS=$(curl -s http://localhost:5000/health | jq -r '.status')

if [ "$STATUS" != "healthy" ]; then
    echo "❌ GED UNHEALTHY: $STATUS" | mail -s "ALERTA GED" admin@hospital.gov.br
    
    # Restart se necessário
    cd /opt/ged
    docker compose restart web
fi
```

```bash
# Permissões
sudo chmod +x /usr/local/bin/ged-health-check.sh

# Cron (a cada 5 minutos)
crontab -e

# Adicione:
*/5 * * * * /usr/local/bin/ged-health-check.sh
```

### 8.2 Logs Centralizados
```bash
# Rotação de logs Docker
sudo nano /etc/docker/daemon.json
```

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

```bash
sudo systemctl restart docker
```

---

## 🔄 PASSO 9: BACKUP AUTOMÁTICO

### 9.1 Script de Backup
```bash
sudo nano /usr/local/bin/ged-backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/backup/ged"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup do banco (criptografado pelo Celery)
docker compose exec -T db pg_dump -U ged_user ged_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup dos uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /opt/ged/app/uploads

# Remove backups antigos (>30 dias)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "✅ Backup concluído: $DATE"
```

```bash
sudo chmod +x /usr/local/bin/ged-backup.sh

# Cron (diariamente às 2h)
sudo crontab -e

# Adicione:
0 2 * * * /usr/local/bin/ged-backup.sh
```

---

## 🎯 PASSO 10: ACESSAR SISTEMA

### 10.1 Primeiro Acesso
1. Abra navegador: https://ged.hospital.gov.br
2. Login com admin criado no Passo 5.3
3. ✅ **Sistema funcionando!**

### 10.2 Configurações Iniciais
1. **Criar Usuários:** Menu Admin → Usuários
2. **Configurar Setores:** Menu Admin → Setores
3. **Configurar WhatsApp:** Menu Admin → WhatsApp (opcional)
4. **Testar Upload:** Criar documento de teste

---

## 📝 CHECKLIST FINAL

Antes de liberar para produção:

- [ ] Arquivo `.env` configurado com senhas fortes
- [ ] Containers rodando (`docker compose ps` = todos healthy)
- [ ] Health check retorna `"status": "healthy"`
- [ ] Nginx configurado e SSL válido
- [ ] Usuário admin criado e testado
- [ ] Backup automático configurado
- [ ] Monitoramento (health check) ativo
- [ ] Logs rotacionando corretamente
- [ ] Firewall configurado (apenas 80, 443, 22)
- [ ] Email SMTP testado
- [ ] Domínio aponta para servidor
- [ ] Certificado SSL válido e auto-renovando

---

## 🚨 TROUBLESHOOTING

### Problema: Container não sobe
```bash
# Veja logs de erro
docker compose logs web

# Recrie containers
docker compose down -v
docker compose up -d
```

### Problema: Database error
```bash
# Verifique se PostgreSQL está rodando
docker compose ps db

# Veja logs
docker compose logs db

# Recrie banco (⚠️ PERDE DADOS!)
docker compose down -v
docker compose up -d
```

### Problema: Redis error
```bash
# Verifique senha no .env
grep REDIS_PASSWORD .env

# Teste conexão
docker compose exec redis redis-cli -a SUA_SENHA ping
```

### Problema: 502 Bad Gateway
```bash
# Nginx não consegue conectar ao Flask
# Verifique se Flask está rodando:
curl http://localhost:5000/health

# Verifique logs Nginx
sudo tail -f /var/log/nginx/ged_error.log
```

---

## 📞 SUPORTE

- **Documentação:** `/opt/ged/README_ATUALIZACOES.md`
- **Segurança:** `/opt/ged/SECURITY.md`
- **Logs:** `docker compose logs -f`
- **Issues:** https://github.com/febaemanuel/ged/issues

---

**✅ SISTEMA PRONTO PARA PRODUÇÃO!**

Última atualização: 2025-12-01
