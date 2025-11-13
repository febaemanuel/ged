@echo off
REM Script de verificação da instalação - Windows
chcp 65001 > nul
cls

echo =========================================
echo Sistema GED - Verificacao de Instalacao
echo =========================================
echo.

set ERROR_COUNT=0

REM Verifica Python
echo [1/8] Verificando Python...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado
    set /a ERROR_COUNT+=1
) else (
    for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo [OK] %PYTHON_VERSION%
)
echo.

REM Verifica pip
echo [2/8] Verificando pip...
python -m pip --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] pip nao encontrado
    set /a ERROR_COUNT+=1
) else (
    echo [OK] pip instalado
)
echo.

REM Verifica PostgreSQL
echo [3/8] Verificando PostgreSQL...
psql --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [AVISO] PostgreSQL nao encontrado no PATH
    echo Instale em: https://www.postgresql.org/download/windows/
) else (
    for /f "tokens=*" %%i in ('psql --version') do set PG_VERSION=%%i
    echo [OK] %PG_VERSION%
)
echo.

REM Verifica ambiente virtual
echo [4/8] Verificando ambiente virtual...
if not exist venv (
    echo [ERRO] Ambiente virtual nao existe
    echo Execute: setup.bat
    set /a ERROR_COUNT+=1
) else (
    echo [OK] venv/ existe
)
echo.

REM Verifica arquivo .env
echo [5/8] Verificando arquivo .env...
if not exist .env (
    echo [AVISO] Arquivo .env nao existe
    echo Copie .env.example para .env e configure
) else (
    echo [OK] .env existe
)
echo.

REM Verifica requirements.txt
echo [6/8] Verificando requirements.txt...
if not exist requirements.txt (
    echo [ERRO] requirements.txt nao encontrado
    set /a ERROR_COUNT+=1
) else (
    echo [OK] requirements.txt existe
)
echo.

REM Verifica estrutura de diretórios
echo [7/8] Verificando estrutura de diretorios...
set DIR_OK=1
if not exist app (
    echo [ERRO] Diretorio app/ nao existe
    set DIR_OK=0
    set /a ERROR_COUNT+=1
)
if not exist app\models (
    echo [ERRO] Diretorio app/models/ nao existe
    set DIR_OK=0
    set /a ERROR_COUNT+=1
)
if not exist app\routes (
    echo [ERRO] Diretorio app/routes/ nao existe
    set DIR_OK=0
    set /a ERROR_COUNT+=1
)
if not exist app\services (
    echo [ERRO] Diretorio app/services/ nao existe
    set DIR_OK=0
    set /a ERROR_COUNT+=1
)
if not exist app\templates (
    echo [ERRO] Diretorio app/templates/ nao existe
    set DIR_OK=0
    set /a ERROR_COUNT+=1
)
if not exist app\static (
    echo [ERRO] Diretorio app/static/ nao existe
    set DIR_OK=0
    set /a ERROR_COUNT+=1
)
if %DIR_OK%==1 (
    echo [OK] Estrutura de diretorios completa
)
echo.

REM Verifica sintaxe Python dos arquivos principais
echo [8/8] Verificando sintaxe Python...
call venv\Scripts\activate.bat 2>nul
python -m py_compile app.py 2>nul
if %errorlevel% neq 0 (
    echo [ERRO] app.py tem erros de sintaxe
    set /a ERROR_COUNT+=1
) else (
    echo [OK] app.py - OK
)

python -m py_compile config.py 2>nul
if %errorlevel% neq 0 (
    echo [ERRO] config.py tem erros de sintaxe
    set /a ERROR_COUNT+=1
) else (
    echo [OK] config.py - OK
)
echo.

REM Resumo final
echo =========================================
echo Resumo da Verificacao
echo =========================================
echo.

if %ERROR_COUNT%==0 (
    echo [OK] Sistema pronto para uso!
    echo.
    echo Proximos passos:
    echo 1. Configure PostgreSQL e crie o banco ged_db
    echo 2. Configure o arquivo .env
    echo 3. Execute: init-db.bat
    echo 4. Execute: start.bat
) else (
    echo [!!] %ERROR_COUNT% erro(s) encontrado(s)
    echo.
    echo Corrija os erros acima antes de prosseguir.
    echo.
    echo Para configuracao completa, execute: setup.bat
)
echo.
pause
