# 🚀 Como Executar o CoreLedger

Este guia mostra como executar o CoreLedger fora do VS Code, diretamente no terminal/PowerShell.

## 🎯 Execução Rápida

### Método 1: Arquivo Batch (Windows)
```cmd
# Duplo clique no arquivo ou execute:
run_coreledger.bat
```

### Método 2: PowerShell Script
```powershell
# Execute no PowerShell:
.\Run-CoreLedger.ps1

# Ou com banco personalizado:
.\Run-CoreLedger.ps1 -DatabasePath "meu_banco.db"
```

### Método 3: Python Direto
```bash
# Com ambiente virtual:
.venv\Scripts\python.exe multilingual_cli.py

# Ou Python global:
python multilingual_cli.py
```

## 🔧 Solução de Problemas

### Problema: "No module named pandas"
```bash
# Instalar dependências:
pip install -r requirements.txt

# Ou manualmente:
pip install pandas openpyxl pytest
```

### Problema: "Python não encontrado"
1. **Instale Python**: https://python.org
2. **Durante instalação**: Marque "Add Python to PATH"
3. **Teste**: Execute `python --version` no terminal

### Problema: "Execution policies" no PowerShell
```powershell
# Execute como administrador:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Ou execute direto:
powershell -ExecutionPolicy Bypass -File "Run-CoreLedger.ps1"
```

### Problema: Ambiente virtual não funciona
```bash
# Criar novo ambiente:
python -m venv .venv

# Ativar (Windows):
.venv\Scripts\activate

# Instalar dependências:
pip install -r requirements.txt

# Executar:
python multilingual_cli.py
```

## 📦 Setup Completo do Zero

### 1. Clonar Repositório
```bash
git clone https://github.com/ViniciusOliveiraOV/CoreLedger.git
cd CoreLedger
```

### 2. Criar Ambiente Virtual
```bash
python -m venv .venv
```

### 3. Ativar Ambiente (Windows)
```bash
# PowerShell:
.venv\Scripts\Activate.ps1

# CMD:
.venv\Scripts\activate.bat
```

### 4. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 5. Executar
```bash
python multilingual_cli.py
```

## 🎮 Execução Automática

O arquivo `multilingual_cli.py` agora detecta automaticamente:
- ✅ Se existe ambiente virtual (.venv)
- ✅ Se as dependências estão instaladas
- ✅ Re-executa com ambiente correto se necessário
- ✅ Mostra mensagens de erro úteis

### Detecção Automática de Ambiente
```python
# O script agora faz isto automaticamente:
1. Tenta importar pandas
2. Se falhar, procura .venv/Scripts/python.exe
3. Re-executa com ambiente virtual
4. Instala dependências se necessário
```

## 📋 Verificação do Sistema

### Testar Ambiente
```bash
# Verificar Python:
python --version

# Verificar pip:
pip --version

# Verificar dependências:
python -c "import pandas, openpyxl; print('✅ Dependências OK')"
```

### Arquivos de Execução Criados
- **`run_coreledger.bat`** - Batch script para Windows
- **`Run-CoreLedger.ps1`** - PowerShell script avançado
- **`multilingual_cli.py`** - Agora com detecção automática
- **`requirements.txt`** - Dependências atualizadas

## 🌟 Funcionalidades dos Scripts

### run_coreledger.bat
- ✅ Detecta ambiente virtual
- ✅ Instala dependências automaticamente
- ✅ Fallback para Python global
- ✅ Mensagens de erro úteis
- ✅ Pause para ver resultados

### Run-CoreLedger.ps1
- ✅ Interface colorida
- ✅ Parâmetros personalizáveis
- ✅ Verificação avançada de dependências
- ✅ Tratamento de erros detalhado
- ✅ Suporte a diferentes cenários

### multilingual_cli.py (Atualizado)
- ✅ Auto-detecção de ambiente
- ✅ Re-execução automática com venv
- ✅ Mensagens de erro melhoradas
- ✅ Compatibilidade total

## 💡 Dicas

### Para Usuários Finais
- Use **`run_coreledger.bat`** (duplo clique)
- Mais simples e direto

### Para Desenvolvedores
- Use **`Run-CoreLedger.ps1`** (mais controle)
- Permite parâmetros personalizados

### Para Automação
- Use **`python multilingual_cli.py`**
- Detecta ambiente automaticamente

---

**Agora o CoreLedger funciona perfeitamente fora do VS Code!** 🎉

Execute qualquer um dos métodos acima e o sistema se configurará automaticamente.