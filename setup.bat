@echo off
REM Sistema GED - Setup Windows

cls
echo =========================================
echo Sistema GED - Setup Windows
echo =========================================
echo.

REM Verifica Python
echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado
    echo Instale Python 3.11+ de: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PY_VER=%%i
echo [OK] %PY_VER% encontrado
echo.

REM Verifica pip
echo Verificando pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] pip nao encontrado
    pause
    exit /b 1
)
echo [OK] pip encontrado
echo.

REM Cria ambiente virtual
echo Criando ambiente virtual...
if exist venv (
    echo [AVISO] venv ja existe, pulando criacao
) else (
    python -m venv venv
    if errorlevel 1 (
        echo [ERRO] Falha ao criar venv
        pause
        exit /b 1
    )
    echo [OK] venv criado
)
echo.

REM Ativa ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERRO] Falha ao ativar venv
    pause
    exit /b 1
)
echo [OK] venv ativado
echo.

REM Atualiza pip
echo Atualizando pip...
python -m pip install --upgrade pip >nul 2>&1
echo [OK] pip atualizado
echo.

REM Instala dependencias
echo Instalando dependencias...
echo (pode demorar alguns minutos...)
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas
echo.

REM Cria .env
if not exist .env (
    echo Criando arquivo .env...
    copy .env.example .env >nul
    echo [OK] Arquivo .env criado
    echo.
    echo [IMPORTANTE] Configure o arquivo .env antes de continuar:
    echo   - DATABASE_URL (PostgreSQL)
    echo   - SECRET_KEY
    echo   - AI_API_BASE_URL e AI_API_KEY
    echo.
) else (
    echo [OK] Arquivo .env ja existe
    echo.
)

REM Cria diretorios
echo Criando diretorios...
if not exist app\uploads\documentos mkdir app\uploads\documentos
if not exist app\uploads\publicados mkdir app\uploads\publicados
if not exist logs mkdir logs
echo [OK] Diretorios criados
echo.

echo =========================================
echo Setup concluido com sucesso!
echo =========================================
echo.
echo Proximos passos:
echo.
echo 1. Configure PostgreSQL:
echo    psql -U postgres
echo    CREATE DATABASE ged_db;
echo    CREATE USER ged_user WITH PASSWORD 'ged_password';
echo    GRANT ALL PRIVILEGES ON DATABASE ged_db TO ged_user;
echo    \q
echo.
echo 2. Edite o arquivo .env com suas credenciais
echo.
echo 3. Inicialize o banco:
echo    venv\Scripts\activate.bat
echo    flask init-db
echo    flask seed-db
echo.
echo 4. Execute o servidor:
echo    python app.py
echo.
echo 5. Acesse: http://localhost:5000
echo.
echo Usuarios padrao:
echo   admin@example.com / admin123
echo   gerente@example.com / gerente123
echo   usuario@example.com / usuario123
echo.
echo =========================================
pause
