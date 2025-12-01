#!/bin/bash
# Restaurar backup do GED

if [ -z "$1" ]; then
    echo "❌ Uso: ./restore.sh <arquivo_backup.sql.gz>"
    echo "Backups disponíveis:"
    ls -lh /backup/ged/*.sql.gz 2>/dev/null || echo "Nenhum backup encontrado"
    exit 1
fi

BACKUP_FILE=$1
echo "⚠️  ATENÇÃO: Isso vai SUBSTITUIR o banco atual!"
read -p "Confirma restauração? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "❌ Operação cancelada"
    exit 1
fi

echo "🔄 Restaurando backup..."

# Para a aplicação
docker compose stop web celery_worker celery_beat

# Restaura banco
zcat $BACKUP_FILE | docker compose exec -T db psql -U ged_user -d ged_db

# Reinicia
docker compose start web celery_worker celery_beat

echo "✅ Backup restaurado!"
