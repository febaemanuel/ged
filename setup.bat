@echo off
REM Script de configuração rápida do Sistema GED - Windows
REM Encoding: UTF-8

chcp 65001 > nul
cls

echo =========================================
echo Sistema GED - Setup Rapido (Windows)
echo =========================================
echo.

REM Verifica Python
echo Verificando Python...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado. Instale Python 3.11 ou superior.
    echo.
    echo Baixe em: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] %PYTHON_VERSION% encontrado
echo.

REM Verifica pip
python -m pip --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] pip nao encontrado.
    pause
    exit /b 1
)
echo [OK] pip encontrado
echo.

REM Cria ambiente virtual
echo Criando ambiente virtual...
if exist venv (
    echo [!!] Ambiente virtual ja existe. Pulando criacao.
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERRO] Falha ao criar ambiente virtual.
        pause
        exit /b 1
    )
    echo [OK] Ambiente virtual criado
)
echo.

REM Ativa ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao ativar ambiente virtual.
    pause
    exit /b 1
)
echo [OK] Ambiente virtual ativado
echo.

REM Atualiza pip
echo Atualizando pip...
python -m pip install --upgrade pip > nul 2>&1
echo [OK] pip atualizado
echo.

REM Instala dependências
echo Instalando dependencias...
echo (Isso pode demorar alguns minutos...)
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas
echo.

REM Cria arquivo .env se não existir
if not exist .env (
    echo Criando arquivo .env...
    copy .env.example .env > nul
    echo [OK] Arquivo .env criado. CONFIGURE-O antes de executar!
    echo.
    echo [!!] IMPORTANTE: Edite o arquivo .env com suas configuracoes:
    echo    - DATABASE_URL (PostgreSQL)
    echo    - SECRET_KEY
    echo    - AI_API_BASE_URL e AI_API_KEY
    echo.
) else (
    echo [OK] Arquivo .env ja existe
    echo.
)

REM Cria diretórios necessários
echo Criando diretorios...
if not exist app\uploads\documentos mkdir app\uploads\documentos
if not exist app\uploads\publicados mkdir app\uploads\publicados
if not exist logs mkdir logs
echo [OK] Diretorios criados
echo.

echo =========================================
echo Setup concluido!
echo =========================================
echo.
echo Proximos passos:
echo.
echo 1. Configure o PostgreSQL e crie o banco de dados:
echo    psql -U postgres
echo    CREATE DATABASE ged_db;
echo    CREATE USER ged_user WITH PASSWORD 'ged_password';
echo    GRANT ALL PRIVILEGES ON DATABASE ged_db TO ged_user;
echo    \q
echo.
echo 2. Configure o arquivo .env com suas credenciais
echo    (Use Notepad, VS Code ou outro editor de texto)
echo.
echo 3. Inicialize o banco de dados:
echo    flask init-db
echo    flask seed-db
echo.
echo 4. Execute a aplicacao:
echo    python app.py
echo    ou
echo    flask run
echo.
echo 5. Acesse: http://localhost:5000
echo.
echo Usuarios padrao apos seed-db:
echo   - admin@example.com / admin123
echo   - gerente@example.com / gerente123
echo   - usuario@example.com / usuario123
echo.
echo =========================================
echo.
echo DICA: Para ativar o ambiente virtual novamente, execute:
echo       venv\Scripts\activate.bat
echo.
pause
