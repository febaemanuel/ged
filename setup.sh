#!/bin/bash

# Script de configuração rápida do Sistema GED

echo "========================================="
echo "Sistema GED - Setup Rápido"
echo "========================================="
echo ""

# Verifica Python
echo "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.11 ou superior."
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ $PYTHON_VERSION encontrado"
echo ""

# Cria ambiente virtual
echo "Criando ambiente virtual..."
python3 -m venv venv
echo "✅ Ambiente virtual criado"
echo ""

# Ativa ambiente virtual
echo "Ativando ambiente virtual..."
source venv/bin/activate
echo "✅ Ambiente virtual ativado"
echo ""

# Instala dependências
echo "Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependências instaladas"
echo ""

# Cria arquivo .env se não existir
if [ ! -f .env ]; then
    echo "Criando arquivo .env..."
    cp .env.example .env
    echo "✅ Arquivo .env criado. CONFIGURE-O antes de executar!"
    echo ""
    echo "⚠️  IMPORTANTE: Edite o arquivo .env com suas configurações:"
    echo "   - DATABASE_URL (PostgreSQL)"
    echo "   - SECRET_KEY"
    echo "   - AI_API_BASE_URL e AI_API_KEY"
    echo ""
else
    echo "✅ Arquivo .env já existe"
    echo ""
fi

# Cria diretórios necessários
echo "Criando diretórios..."
mkdir -p app/uploads/documentos
mkdir -p app/uploads/publicados
mkdir -p logs
echo "✅ Diretórios criados"
echo ""

echo "========================================="
echo "Setup concluído!"
echo "========================================="
echo ""
echo "Próximos passos:"
echo ""
echo "1. Configure o PostgreSQL e crie o banco de dados:"
echo "   CREATE DATABASE ged_db;"
echo "   CREATE USER ged_user WITH PASSWORD 'ged_password';"
echo "   GRANT ALL PRIVILEGES ON DATABASE ged_db TO ged_user;"
echo ""
echo "2. Configure o arquivo .env com suas credenciais"
echo ""
echo "3. Inicialize o banco de dados:"
echo "   flask init-db"
echo "   flask seed-db"
echo ""
echo "4. Execute a aplicação:"
echo "   python app.py"
echo "   ou"
echo "   flask run"
echo ""
echo "5. Acesse: http://localhost:5000/home"
echo ""
echo "Usuários padrão após seed-db:"
echo "  - admin@example.com / admin123"
echo "  - gerente@example.com / gerente123"
echo "  - usuario@example.com / usuario123"
echo ""
