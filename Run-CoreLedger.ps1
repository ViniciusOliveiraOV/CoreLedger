# CoreLedger PowerShell Launcher
# Executa o sistema bancário com detecção automática de ambiente

param(
    [string]$DatabasePath = "multilingual_bank.db"
)

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   🏦 CoreLedger - Sistema Bancário" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se estamos no diretório correto
if (-not (Test-Path "multilingual_cli.py")) {
    Write-Host "❌ Erro: Script não encontrado" -ForegroundColor Red
    Write-Host "💡 Execute este arquivo na pasta do CoreLedger" -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Função para verificar se um comando existe
function Test-Command($command) {
    try {
        if (Get-Command $command -ErrorAction Stop) { return $true }
    }
    catch { return $false }
}

# Verificar ambiente virtual
$venvPython = ".\.venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    Write-Host "🔄 Ambiente virtual detectado" -ForegroundColor Green
    
    # Verificar dependências
    try {
        & $venvPython -c "import pandas, openpyxl" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "📦 Instalando dependências..." -ForegroundColor Yellow
            & ".\.venv\Scripts\pip.exe" install pandas openpyxl pytest
        }
    }
    catch {
        Write-Host "📦 Instalando dependências..." -ForegroundColor Yellow
        & ".\.venv\Scripts\pip.exe" install pandas openpyxl pytest
    }
    
    Write-Host "🚀 Iniciando CoreLedger..." -ForegroundColor Green
    Write-Host ""
    
    # Executar com ambiente virtual
    & $venvPython "multilingual_cli.py" $DatabasePath
}
elseif (Test-Command "python") {
    Write-Host "⚠️  Ambiente virtual não encontrado" -ForegroundColor Yellow
    Write-Host "🔄 Tentando com Python global..." -ForegroundColor Yellow
    
    # Verificar dependências globais
    try {
        python -c "import pandas, openpyxl" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Dependências não encontradas" -ForegroundColor Red
            Write-Host "💡 Execute: pip install pandas openpyxl pytest" -ForegroundColor Yellow
            Read-Host "Pressione Enter para sair"
            exit 1
        }
    }
    catch {
        Write-Host "❌ Erro ao verificar dependências" -ForegroundColor Red
        Read-Host "Pressione Enter para sair"
        exit 1
    }
    
    Write-Host "🚀 Iniciando CoreLedger..." -ForegroundColor Green
    Write-Host ""
    
    # Executar com Python global
    python "multilingual_cli.py" $DatabasePath
}
else {
    Write-Host "❌ Python não encontrado no sistema" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Para resolver:" -ForegroundColor Yellow
    Write-Host "   1. Instale Python: https://python.org" -ForegroundColor White
    Write-Host "   2. Ou crie ambiente virtual:" -ForegroundColor White
    Write-Host "      python -m venv .venv" -ForegroundColor Gray
    Write-Host "      .venv\Scripts\activate" -ForegroundColor Gray
    Write-Host "      pip install pandas openpyxl pytest" -ForegroundColor Gray
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host ""
Write-Host "👋 CoreLedger finalizado." -ForegroundColor Green
Read-Host "Pressione Enter para sair"