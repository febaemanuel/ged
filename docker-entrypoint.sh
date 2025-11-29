#!/bin/bash
# ============================================
# Docker Entrypoint - Sistema GED EBSERH
# ============================================

set -e

echo "=========================================="
echo "Sistema GED EBSERH - Inicializando..."
echo "=========================================="

# Aguarda PostgreSQL estar pronto
echo "⏳ Aguardando PostgreSQL..."
until PGPASSWORD=${DB_PASSWORD:-ged_password_CHANGE_IN_PRODUCTION} psql -h db -U ged_user -d ged_db -c '\q' 2>/dev/null; do
  echo "⏳ PostgreSQL não está pronto - aguardando..."
  sleep 2
done
echo "✅ PostgreSQL está pronto!"

# Cria diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p /app/app/uploads/documentos
mkdir -p /app/app/uploads/publicados
mkdir -p /app/uploads/assinaturas
mkdir -p /app/logs
echo "✅ Diretórios criados!"

# Inicializa banco de dados (se necessário)
echo "🗄️  Verificando banco de dados..."
python << EOF
from app import create_app
from app.models import db
import os

app = create_app(os.getenv('FLASK_ENV', 'production'))
with app.app_context():
    try:
        # Tenta criar as tabelas
        db.create_all()
        print("✅ Banco de dados inicializado!")
    except Exception as e:
        print(f"ℹ️  Banco já existe ou erro: {e}")
EOF

echo "=========================================="
echo "✅ Inicialização completa!"
echo "🚀 Iniciando aplicação..."
echo "=========================================="

# Executa o comando passado como argumento
exec "$@"
