@echo off
echo 🚀 Iniciando CoreLedger Real-Time Dashboard...
echo.

echo 📊 Passo 1: Verificando ambiente Python...
if not exist .venv (
    echo ❌ Ambiente virtual não encontrado!
    echo Execute: python -m venv .venv
    pause
    exit
)

echo ✅ Ativando ambiente virtual...
call .venv\Scripts\activate

echo 📦 Passo 2: Instalando dependências Python...
pip install -q fastapi uvicorn[standard] websockets

echo 🌐 Passo 3: Verificando Node.js...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js não encontrado!
    echo Instale Node.js de: https://nodejs.org
    pause
    exit
)

echo 📦 Passo 4: Instalando dependências React...
cd frontend
if not exist node_modules (
    echo Executando npm install...
    npm install
)
cd ..

echo 🔥 Passo 5: Iniciando serviços...
echo.
echo 🖥️  Backend rodará em: http://localhost:8000
echo 🌐 Frontend rodará em: http://localhost:3000
echo.

start "CoreLedger API" cmd /k "call .venv\Scripts\activate && python api/main.py"
timeout /t 3 >nul
start "CoreLedger Frontend" cmd /k "cd frontend && npm start"

echo ✅ CoreLedger Dashboard iniciado com sucesso!
echo 📱 O navegador abrirá automaticamente em alguns segundos...
echo.
pause