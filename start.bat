@echo off
REM Script para iniciar o Sistema GED - Windows
chcp 65001 > nul

echo =========================================
echo Sistema GED - Iniciando Servidor
echo =========================================
echo.

REM Verifica se o ambiente virtual existe
if not exist venv (
    echo [ERRO] Ambiente virtual nao encontrado!
    echo Execute setup.bat primeiro.
    echo.
    pause
    exit /b 1
)

REM Ativa ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Verifica se o .env existe
if not exist .env (
    echo [AVISO] Arquivo .env nao encontrado!
    echo Copiando .env.example...
    copy .env.example .env
    echo.
    echo [!!] CONFIGURE o arquivo .env antes de continuar!
    echo.
    pause
    exit /b 1
)

echo [OK] Ambiente configurado
echo.

REM Inicia a aplicação
echo Iniciando servidor Flask...
echo.
echo Acesse: http://localhost:5000
echo.
echo Pressione CTRL+C para parar o servidor
echo =========================================
echo.

python app.py
