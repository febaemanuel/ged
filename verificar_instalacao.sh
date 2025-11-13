#!/bin/bash

# Script de Verificação de Instalação do Sistema GED
# Verifica todos os requisitos e dependências

echo "════════════════════════════════════════════════════════════"
echo "  VERIFICAÇÃO DE INSTALAÇÃO - SISTEMA GED"
echo "════════════════════════════════════════════════════════════"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contadores
ERROS=0
AVISOS=0

# Função para verificar comando
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✅ $1 encontrado:${NC} $(command -v $1)"
        return 0
    else
        echo -e "${RED}❌ $1 NÃO ENCONTRADO${NC}"
        ERROS=$((ERROS + 1))
        return 1
    fi
}

# Função para verificar versão Python
check_python_version() {
    if command -v python3 &> /dev/null; then
        VERSION=$(python3 --version | cut -d' ' -f2)
        MAJOR=$(echo $VERSION | cut -d'.' -f1)
        MINOR=$(echo $VERSION | cut -d'.' -f2)

        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 11 ]; then
            echo -e "${GREEN}✅ Python $VERSION (OK)${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  Python $VERSION encontrado (recomendado: 3.11+)${NC}"
            AVISOS=$((AVISOS + 1))
            return 1
        fi
    else
        echo -e "${RED}❌ Python não encontrado${NC}"
        ERROS=$((ERROS + 1))
        return 1
    fi
}

# Função para verificar PostgreSQL
check_postgresql() {
    if command -v psql &> /dev/null; then
        VERSION=$(psql --version | cut -d' ' -f3)
        echo -e "${GREEN}✅ PostgreSQL $VERSION encontrado${NC}"

        # Verificar se está rodando
        if sudo systemctl is-active --quiet postgresql 2>/dev/null || brew services list 2>/dev/null | grep -q "postgresql.*started"; then
            echo -e "${GREEN}✅ PostgreSQL está rodando${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  PostgreSQL instalado mas pode não estar rodando${NC}"
            AVISOS=$((AVISOS + 1))
            return 1
        fi
    else
        echo -e "${RED}❌ PostgreSQL não encontrado${NC}"
        ERROS=$((ERROS + 1))
        return 1
    fi
}

# Verificar estrutura do projeto
check_project_structure() {
    echo ""
    echo "Verificando estrutura do projeto..."

    REQUIRED_FILES=(
        "app.py"
        "config.py"
        "requirements.txt"
        "app/__init__.py"
        "app/models/models.py"
        "app/routes/routes_auth.py"
        "app/routes/routes_documento.py"
        "app/routes/routes_tarefa.py"
        "app/routes/routes_ia.py"
        "app/routes/routes_dashboard.py"
        "app/services/ai_client.py"
        "app/services/report_generator.py"
    )

    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$file" ]; then
            echo -e "${GREEN}✅${NC} $file"
        else
            echo -e "${RED}❌${NC} $file não encontrado"
            ERROS=$((ERROS + 1))
        fi
    done
}

# Verificar ambiente virtual
check_virtualenv() {
    echo ""
    echo "Verificando ambiente virtual..."

    if [ -d "venv" ]; then
        echo -e "${GREEN}✅ Ambiente virtual existe em ./venv${NC}"

        if [[ "$VIRTUAL_ENV" != "" ]]; then
            echo -e "${GREEN}✅ Ambiente virtual está ATIVADO${NC}"
            echo "   Path: $VIRTUAL_ENV"
            return 0
        else
            echo -e "${YELLOW}⚠️  Ambiente virtual NÃO está ativado${NC}"
            echo "   Execute: source venv/bin/activate"
            AVISOS=$((AVISOS + 1))
            return 1
        fi
    else
        echo -e "${RED}❌ Ambiente virtual não existe${NC}"
        echo "   Execute: python3 -m venv venv"
        ERROS=$((ERROS + 1))
        return 1
    fi
}

# Verificar dependências Python
check_python_packages() {
    echo ""
    echo "Verificando pacotes Python instalados..."

    if [[ "$VIRTUAL_ENV" == "" ]]; then
        echo -e "${YELLOW}⚠️  Ambiente virtual não está ativado, pulando verificação de pacotes${NC}"
        AVISOS=$((AVISOS + 1))
        return 1
    fi

    REQUIRED_PACKAGES=(
        "Flask"
        "Flask-SQLAlchemy"
        "Flask-Login"
        "psycopg2"
        "reportlab"
        "requests"
    )

    for package in "${REQUIRED_PACKAGES[@]}"; do
        if python3 -c "import ${package//-/_}" 2>/dev/null; then
            VERSION=$(pip show $package 2>/dev/null | grep Version | cut -d' ' -f2)
            echo -e "${GREEN}✅${NC} $package ($VERSION)"
        else
            echo -e "${RED}❌${NC} $package não instalado"
            ERROS=$((ERROS + 1))
        fi
    done
}

# Verificar arquivo .env
check_env_file() {
    echo ""
    echo "Verificando arquivo de configuração..."

    if [ -f ".env" ]; then
        echo -e "${GREEN}✅ Arquivo .env existe${NC}"

        # Verificar se tem as variáveis necessárias
        if grep -q "DATABASE_URL" .env && grep -q "SECRET_KEY" .env; then
            echo -e "${GREEN}✅ Variáveis básicas configuradas${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  .env existe mas pode estar incompleto${NC}"
            AVISOS=$((AVISOS + 1))
            return 1
        fi
    else
        echo -e "${RED}❌ Arquivo .env não encontrado${NC}"
        echo "   Execute: cp .env.example .env"
        ERROS=$((ERROS + 1))
        return 1
    fi
}

# Verificar conexão com PostgreSQL
check_database_connection() {
    echo ""
    echo "Verificando conexão com banco de dados..."

    if [ -f ".env" ]; then
        # Extrair credenciais do .env
        DB_URL=$(grep DATABASE_URL .env | cut -d'=' -f2)

        if [[ $DB_URL == *"ged_db"* ]]; then
            # Tentar conectar
            if PGPASSWORD=ged_password psql -h localhost -U ged_user -d ged_db -c "\q" 2>/dev/null; then
                echo -e "${GREEN}✅ Conexão com banco de dados OK${NC}"

                # Verificar se tabelas existem
                TABLES=$(PGPASSWORD=ged_password psql -h localhost -U ged_user -d ged_db -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')

                if [ "$TABLES" -gt 0 ]; then
                    echo -e "${GREEN}✅ Banco possui $TABLES tabelas${NC}"
                else
                    echo -e "${YELLOW}⚠️  Banco existe mas não possui tabelas${NC}"
                    echo "   Execute: flask init-db"
                    AVISOS=$((AVISOS + 1))
                fi

                return 0
            else
                echo -e "${RED}❌ Não foi possível conectar ao banco de dados${NC}"
                echo "   Verifique se PostgreSQL está rodando"
                echo "   Verifique credenciais no .env"
                ERROS=$((ERROS + 1))
                return 1
            fi
        else
            echo -e "${YELLOW}⚠️  DATABASE_URL pode estar incorreto${NC}"
            AVISOS=$((AVISOS + 1))
            return 1
        fi
    else
        echo -e "${RED}❌ Arquivo .env não encontrado${NC}"
        ERROS=$((ERROS + 1))
        return 1
    fi
}

# Verificar sintaxe Python
check_python_syntax() {
    echo ""
    echo "Verificando sintaxe dos arquivos Python..."

    ERRORS_FOUND=0

    for file in app.py config.py app/**/*.py; do
        if [ -f "$file" ]; then
            if python3 -m py_compile "$file" 2>/dev/null; then
                : # Silencioso se OK
            else
                echo -e "${RED}❌${NC} Erro de sintaxe em: $file"
                ERRORS_FOUND=$((ERRORS_FOUND + 1))
            fi
        fi
    done

    if [ $ERRORS_FOUND -eq 0 ]; then
        echo -e "${GREEN}✅ Todos os arquivos Python estão OK${NC}"
        return 0
    else
        echo -e "${RED}❌ Encontrados $ERRORS_FOUND arquivo(s) com erro de sintaxe${NC}"
        ERROS=$((ERROS + ERRORS_FOUND))
        return 1
    fi
}

# EXECUTAR VERIFICAÇÕES
echo "1. Verificando Python..."
check_python_version

echo ""
echo "2. Verificando PostgreSQL..."
check_postgresql

echo ""
echo "3. Verificando Git..."
check_command git

check_project_structure
check_virtualenv
check_python_packages
check_env_file
check_database_connection
check_python_syntax

# RESUMO FINAL
echo ""
echo "════════════════════════════════════════════════════════════"
echo "  RESUMO DA VERIFICAÇÃO"
echo "════════════════════════════════════════════════════════════"
echo ""

if [ $ERROS -eq 0 ] && [ $AVISOS -eq 0 ]; then
    echo -e "${GREEN}✅ PERFEITO! Sistema pronto para uso!${NC}"
    echo ""
    echo "Próximos passos:"
    echo "1. Ative o ambiente virtual: source venv/bin/activate"
    echo "2. Execute o servidor: python app.py"
    echo "3. Acesse: http://localhost:5000/home"
    echo ""
    exit 0
elif [ $ERROS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Sistema OK com $AVISOS aviso(s)${NC}"
    echo ""
    echo "Revise os avisos acima e corrija se necessário."
    echo ""
    exit 0
else
    echo -e "${RED}❌ Encontrados $ERROS erro(s) e $AVISOS aviso(s)${NC}"
    echo ""
    echo "Corrija os erros acima antes de executar o sistema."
    echo ""
    echo "Consulte INSTALACAO_COMPLETA.md para instruções detalhadas."
    echo ""
    exit 1
fi
