#!/bin/bash
# Backup completo do GED
BACKUP_DIR="/backup/ged"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

echo "💾 Backup GED - $DATE"

# Banco de dados
echo "1️⃣  Backup PostgreSQL..."
docker compose exec -T db pg_dump -U ged_user ged_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Uploads
echo "2️⃣  Backup uploads..."
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz -C /opt/ged app/uploads

# .env (sem senhas visíveis)
echo "3️⃣  Backup configuração..."
cp .env $BACKUP_DIR/env_$DATE.backup

# Remove backups antigos (>30 dias)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "✅ Backup concluído: $BACKUP_DIR"
ls -lh $BACKUP_DIR/*$DATE*
