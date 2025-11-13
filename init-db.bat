@echo off
REM Script para inicializar o banco de dados - Windows
chcp 65001 > nul

echo =========================================
echo Sistema GED - Inicializar Banco de Dados
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
call venv\Scripts\activate.bat

REM Verifica se o .env existe
if not exist .env (
    echo [ERRO] Arquivo .env nao encontrado!
    echo Execute setup.bat primeiro e configure o .env
    echo.
    pause
    exit /b 1
)

echo [OK] Ambiente configurado
echo.

REM Inicializa o banco
echo Criando tabelas no banco de dados...
flask init-db
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao criar tabelas.
    echo Verifique se o PostgreSQL esta rodando e o .env esta configurado.
    echo.
    pause
    exit /b 1
)
echo [OK] Tabelas criadas
echo.

REM Popula dados iniciais
echo Populando dados iniciais (usuarios padrao)...
flask seed-db
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao popular dados.
    echo.
    pause
    exit /b 1
)
echo [OK] Dados iniciais criados
echo.

echo =========================================
echo Banco de dados inicializado com sucesso!
echo =========================================
echo.
echo Usuarios padrao criados:
echo   - admin@example.com / admin123 (Administrador)
echo   - gerente@example.com / gerente123 (Gerente)
echo   - usuario@example.com / usuario123 (Usuario)
echo.
echo Para iniciar o servidor, execute: start.bat
echo.
pause
