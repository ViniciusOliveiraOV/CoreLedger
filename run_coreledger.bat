@echo off
setlocal

REM Script para executar o CoreLedger no Windows
REM Detecta automaticamente o ambiente virtual e executa

echo.
echo ==========================================
echo   🏦 CoreLedger - Sistema Bancario
echo ==========================================
echo.

REM Verificar se estamos no diretório correto
if not exist "multilingual_cli.py" (
    echo ❌ Erro: Script nao encontrado
    echo 💡 Execute este arquivo na pasta do CoreLedger
    pause
    exit /b 1
)

REM Verificar se o ambiente virtual existe
if exist ".venv\Scripts\python.exe" (
    echo 🔄 Ativando ambiente virtual...
    call .venv\Scripts\activate.bat
    
    REM Verificar se as dependências estão instaladas
    .venv\Scripts\python.exe -c "import pandas" 2>nul
    if errorlevel 1 (
        echo 📦 Instalando dependências...
        .venv\Scripts\pip.exe install pandas openpyxl pytest
    )
    
    echo 🚀 Iniciando CoreLedger...
    echo.
    .venv\Scripts\python.exe multilingual_cli.py %*
) else (
    REM Tentar com Python global
    echo ⚠️  Ambiente virtual nao encontrado
    echo 🔄 Tentando com Python global...
    python --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Python nao encontrado no sistema
        echo.
        echo 💡 Instale o Python em: https://python.org
        echo    Ou crie um ambiente virtual:
        echo    python -m venv .venv
        echo    .venv\Scripts\activate
        echo    pip install pandas openpyxl pytest
        pause
        exit /b 1
    )
    
    python multilingual_cli.py %*
)

echo.
echo 👋 CoreLedger finalizado.
pause