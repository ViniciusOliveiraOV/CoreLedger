# 📊 CoreLedger + Power BI: Guia de Integração

Este guia mostra como conectar os dados do sistema bancário CoreLedger ao Microsoft Power BI para criar dashboards e relatórios financeiros avançados.

## 🗄️ Estrutura dos Dados

O CoreLedger usa SQLite com duas tabelas principais:

### Tabela `accounts` (Contas)
- `id` (INTEGER) - ID único da conta
- `name` (TEXT) - Nome do titular
- `balance` (TEXT) - Saldo atual em formato decimal
- `created_at` (TIMESTAMP) - Data de criação

### Tabela `transactions` (Transações)
- `id` (INTEGER) - ID único da transação
- `from_account_id` (INTEGER) - ID da conta origem (pode ser NULL)
- `to_account_id` (INTEGER) - ID da conta destino (pode ser NULL)
- `amount` (TEXT) - Valor da transação em formato decimal
- `transaction_type` (TEXT) - Tipo: deposit, withdrawal, transfer
- `description` (TEXT) - Descrição opcional
- `created_at` (TIMESTAMP) - Data da transação

## 🔗 Métodos de Conexão com Power BI

### Método 1: Conexão Direta SQLite (Recomendado)

#### 1. Preparar o Arquivo de Banco
```bash
# Certifique-se de que o banco existe
python multilingual_cli.py
# Execute algumas operações para gerar dados
```

#### 2. Conectar no Power BI Desktop
1. Abra o **Power BI Desktop**
2. Clique em **Obter Dados** → **Mais...**
3. Procure por **"SQLite"** ou **"Banco de Dados SQLite"**
4. Navegue até o arquivo `multilingual_bank.db`
5. Selecione as tabelas `accounts` e `transactions`
6. Clique em **Carregar**

#### 3. Configurar Relacionamentos
```powerbi
accounts[id] ↔ transactions[from_account_id]
accounts[id] ↔ transactions[to_account_id]
```

### Método 2: Exportação via CSV/Excel

#### Script Python para Exportação
```python
# Criar arquivo: export_to_powerbi.py
from src.models.database import DatabaseManager
import pandas as pd
from datetime import datetime

def export_data_for_powerbi():
    """Exporta dados para formatos compatíveis com Power BI"""
    
    db = DatabaseManager("multilingual_bank.db")
    
    try:
        # Exportar contas
        accounts_query = """
        SELECT 
            id,
            name,
            CAST(balance AS REAL) as balance_numeric,
            balance as balance_text,
            created_at,
            date(created_at) as created_date
        FROM accounts
        """
        
        accounts_df = pd.read_sql_query(accounts_query, db.connection)
        accounts_df.to_csv('powerbi_accounts.csv', index=False)
        
        # Exportar transações com dados enriquecidos
        transactions_query = """
        SELECT 
            t.id,
            t.from_account_id,
            fa.name as from_account_name,
            t.to_account_id,
            ta.name as to_account_name,
            CAST(t.amount AS REAL) as amount_numeric,
            t.amount as amount_text,
            t.transaction_type,
            t.description,
            t.created_at,
            date(t.created_at) as transaction_date,
            strftime('%Y-%m', t.created_at) as year_month,
            strftime('%Y', t.created_at) as year
        FROM transactions t
        LEFT JOIN accounts fa ON t.from_account_id = fa.id
        LEFT JOIN accounts ta ON t.to_account_id = ta.id
        """
        
        transactions_df = pd.read_sql_query(transactions_query, db.connection)
        transactions_df.to_csv('powerbi_transactions.csv', index=False)
        
        # Criar resumo mensal
        monthly_summary_query = """
        SELECT 
            strftime('%Y-%m', created_at) as month,
            transaction_type,
            COUNT(*) as transaction_count,
            SUM(CAST(amount AS REAL)) as total_amount
        FROM transactions
        GROUP BY strftime('%Y-%m', created_at), transaction_type
        ORDER BY month, transaction_type
        """
        
        monthly_df = pd.read_sql_query(monthly_summary_query, db.connection)
        monthly_df.to_csv('powerbi_monthly_summary.csv', index=False)
        
        print("✅ Arquivos exportados com sucesso:")
        print("  - powerbi_accounts.csv")
        print("  - powerbi_transactions.csv") 
        print("  - powerbi_monthly_summary.csv")
        
    finally:
        db.close()

if __name__ == "__main__":
    export_data_for_powerbi()
```

### Método 3: API RESTful para Power BI (Avançado)

#### Criar API Flask
```python
# Criar arquivo: powerbi_api.py
from flask import Flask, jsonify
from src.models.database import DatabaseManager
import json

app = Flask(__name__)

@app.route('/api/accounts')
def get_accounts():
    """Retorna todas as contas"""
    db = DatabaseManager("multilingual_bank.db")
    try:
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT id, name, 
                   CAST(balance AS REAL) as balance,
                   created_at
            FROM accounts
        """)
        
        accounts = []
        for row in cursor.fetchall():
            accounts.append({
                'id': row[0],
                'name': row[1], 
                'balance': row[2],
                'created_at': row[3]
            })
        
        return jsonify(accounts)
    finally:
        db.close()

@app.route('/api/transactions')
def get_transactions():
    """Retorna todas as transações"""
    db = DatabaseManager("multilingual_bank.db")
    try:
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT t.id, t.from_account_id, t.to_account_id,
                   CAST(t.amount AS REAL) as amount,
                   t.transaction_type, t.description, t.created_at,
                   fa.name as from_account_name,
                   ta.name as to_account_name
            FROM transactions t
            LEFT JOIN accounts fa ON t.from_account_id = fa.id
            LEFT JOIN accounts ta ON t.to_account_id = ta.id
        """)
        
        transactions = []
        for row in cursor.fetchall():
            transactions.append({
                'id': row[0],
                'from_account_id': row[1],
                'to_account_id': row[2],
                'amount': row[3],
                'transaction_type': row[4],
                'description': row[5],
                'created_at': row[6],
                'from_account_name': row[7],
                'to_account_name': row[8]
            })
        
        return jsonify(transactions)
    finally:
        db.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

## 📊 Visualizações Sugeridas para Power BI

### 1. Dashboard Executivo
- **Cartões KPI**: Saldo Total, Número de Contas, Transações do Mês
- **Gráfico de Linha**: Evolução do saldo total ao longo do tempo
- **Gráfico de Pizza**: Distribuição por tipo de transação
- **Tabela**: Top 10 contas por saldo

### 2. Análise de Transações
- **Gráfico de Barras**: Volume de transações por mês
- **Gráfico de Área**: Fluxo de caixa (entradas vs saídas)
- **Mapa de Calor**: Transações por dia da semana/hora
- **Funil**: Análise do fluxo de transferências entre contas

### 3. Análise de Contas
- **Histograma**: Distribuição de saldos
- **Gráfico de Dispersão**: Saldo vs Número de transações
- **Ranking**: Contas mais ativas
- **Segmentação**: Perfil de clientes por faixa de saldo

## 🔄 Automatização de Atualização

### Power BI Desktop
```powerquery
// M Query para atualização automática
let
    Source = Sqlite.Database("C:\Caminho\Para\multilingual_bank.db"),
    accounts = Source{[Schema="main",Item="accounts"]}[Data],
    transactions = Source{[Schema="main",Item="transactions"]}[Data]
in
    { accounts, transactions }
```

### Power BI Service (Agendamento)
1. Publique o relatório no Power BI Service
2. Configure o **Gateway de dados local**
3. Agende atualizações automáticas
4. Configure alertas para mudanças significativas

## 📈 Métricas DAX Essenciais

### Medidas Calculadas
```dax
// Saldo Total
Saldo Total = SUM(accounts[balance])

// Transações deste Mês
Transações Mês Atual = 
CALCULATE(
    COUNT(transactions[id]),
    MONTH(transactions[created_at]) = MONTH(TODAY())
)

// Crescimento Mensal
Crescimento Saldo = 
VAR SaldoAtual = SUM(accounts[balance])
VAR SaldoAnterior = CALCULATE(
    SUM(accounts[balance]),
    PREVIOUSMONTH(transactions[created_at])
)
RETURN 
DIVIDE(SaldoAtual - SaldoAnterior, SaldoAnterior, 0)

// Volume de Depósitos
Volume Depósitos = 
CALCULATE(
    SUM(transactions[amount]),
    transactions[transaction_type] = "deposit"
)

// Volume de Saques
Volume Saques = 
CALCULATE(
    SUM(transactions[amount]),
    transactions[transaction_type] = "withdrawal"
)

// Fluxo Líquido
Fluxo Líquido = [Volume Depósitos] - [Volume Saques]
```

## 🚀 Exemplo Prático

### 1. Gerar Dados de Teste
```bash
# Execute o CoreLedger e crie dados
python multilingual_cli.py

# Crie algumas contas e transações:
# - Conta "João Silva" com R$ 5.000
# - Conta "Maria Santos" com R$ 3.000  
# - Faça transferências e depósitos
# - Execute por alguns dias para gerar histórico
```

### 2. Exportar e Conectar
```bash
# Execute o script de exportação
python export_to_powerbi.py

# Abra Power BI Desktop
# Importe os arquivos CSV gerados
# Configure relacionamentos entre tabelas
```

### 3. Criar Primeira Visualização
- **Cartão**: Exibir saldo total das contas
- **Gráfico de Barras**: Transações por tipo
- **Linha do Tempo**: Evolução dos saldos
- **Tabela**: Lista de todas as contas

## 🔧 Troubleshooting

### Problema: Power BI não reconhece SQLite
**Solução**: Instale o driver SQLite ODBC
```bash
# Download em: http://www.ch-werner.de/sqliteodbc/
# Configure o DSN no Windows
```

### Problema: Dados não atualizando
**Solução**: Verifique permissões do arquivo
```bash
# Garanta que o Power BI tem acesso ao arquivo .db
# Configure o Gateway se usando Power BI Service
```

### Problema: Formato de data incorreto
**Solução**: Configure tipo de dados no Power Query
```powerquery
// Converter texto para data
= Table.TransformColumnTypes(Source,{{"created_at", type datetime}})
```

## 🎯 Próximos Passos

1. **Implemente o script de exportação**
2. **Configure a conexão no Power BI**
3. **Crie dashboards específicos para suas necessidades**
4. **Configure atualizações automáticas**
5. **Publique no Power BI Service para compartilhamento**

Esta integração permite transformar os dados transacionais do CoreLedger em insights visuais poderosos para análise financeira avançada! 📊✨