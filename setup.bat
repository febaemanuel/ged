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

REM Atualiza pip e instala wheel
echo Atualizando pip e instalando wheel...
python -m pip install --upgrade pip wheel setuptools >nul 2>&1
echo [OK] pip atualizado
echo.

REM Instala dependencias (Windows)
echo Instalando dependencias...
echo (pode demorar alguns minutos...)
echo.

REM Tenta usar requirements-windows.txt primeiro
if exist requirements-windows.txt (
    echo Usando requirements-windows.txt para Windows...
    pip install -r requirements-windows.txt
    if errorlevel 1 (
        echo.
        echo [AVISO] Falha com requirements-windows.txt
        echo Tentando requirements.txt padrao...
        echo.
        pip install -r requirements.txt
        if errorlevel 1 (
            goto :install_error
        )
    )
) else (
    REM Usa requirements.txt padrao
    pip install -r requirements.txt
    if errorlevel 1 (
        goto :install_error
    )
)

echo [OK] Dependencias instaladas
echo.
goto :continue_setup

:install_error
echo.
echo =========================================
echo [ERRO] Falha ao instalar dependencias
echo =========================================
echo.
echo O erro mais comum e a falta do Visual C++ Build Tools.
echo.
echo SOLUCOES:
echo.
echo 1. Instalar Microsoft C++ Build Tools (RECOMENDADO):
echo    https://visualstudio.microsoft.com/visual-cpp-build-tools/
echo    - Baixe e instale
echo    - Selecione: Desktop development with C++
echo    - Execute setup.bat novamente
echo.
echo 2. OU instalar apenas psycopg2-binary manualmente:
echo    venv\Scripts\activate.bat
echo    pip install psycopg2-binary==2.9.7
echo    pip install -r requirements.txt
echo.
echo 3. OU baixar wheel pre-compilado:
echo    https://www.lfd.uci.edu/~gohlke/pythonlibs/#psycopg
echo    pip install psycopg2_binary-X.X.X-cpXXX-cpXXX-win_amd64.whl
echo.
pause
exit /b 1

:continue_setup
REM Cria .env
if not exist .env (
    echo Criando arquivo .env...
    copy .env.example .env >nul
    echo [OK] Arquivo .env criado
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
echo Configuracao de Banco de Dados
echo =========================================
echo.
echo IMPORTANTE: Configure o .env antes de continuar!
echo Abra o arquivo .env e edite:
echo   - DATABASE_URL (suas credenciais PostgreSQL)
echo   - SECRET_KEY
echo.
choice /C SN /M "Deseja inicializar o banco de dados agora"
if errorlevel 2 goto :skip_db_init
if errorlevel 1 goto :init_db

:init_db
echo.
echo Inicializando banco de dados...
python init_database.py
if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao inicializar banco de dados
    echo Verifique se:
    echo   1. PostgreSQL esta rodando
    echo   2. Banco de dados foi criado
    echo   3. Arquivo .env esta configurado corretamente
    echo.
    echo Voce pode inicializar manualmente depois com:
    echo    python init_database.py
    echo.
) else (
    echo [OK] Banco de dados inicializado com sucesso!
    echo.
)
goto :final_message

:skip_db_init
echo.
echo [AVISO] Inicializacao do banco pulada
echo Execute manualmente: python init_database.py
echo.

:final_message
echo =========================================
echo Setup concluido com sucesso!
echo =========================================
echo.
echo Proximos passos:
echo.
echo 1. Se ainda nao fez, configure PostgreSQL:
echo    psql -U postgres
echo    CREATE DATABASE ged_db;
echo    CREATE USER ged_user WITH PASSWORD 'ged_password';
echo    GRANT ALL PRIVILEGES ON DATABASE ged_db TO ged_user;
echo    \q
echo.
echo 2. Se pulou, edite o .env e execute:
echo    python init_database.py
echo.
echo 3. Execute o servidor:
echo    python app.py
echo.
echo 4. Acesse: http://localhost:5000
echo.
echo Usuarios padrao:
echo   admin@example.com / admin123
echo   gerente@example.com / gerente123
echo   usuario@example.com / usuario123
echo.
echo =========================================
pause
