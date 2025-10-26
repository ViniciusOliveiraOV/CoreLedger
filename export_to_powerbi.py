"""
Script para exportar dados do CoreLedger para Power BI
Gera arquivos CSV e Excel otimizados para análise no Power BI
"""

import pandas as pd
import os
from datetime import datetime
from src.models.database import DatabaseManager


def export_data_for_powerbi(db_path="multilingual_bank.db", output_dir="powerbi_exports"):
    """
    Exporta dados do CoreLedger para formatos compatíveis com Power BI
    
    Args:
        db_path: Caminho para o banco de dados SQLite
        output_dir: Diretório de saída para os arquivos
    """
    
    # Criar diretório de saída se não existir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    if not os.path.exists(db_path):
        print(f"❌ Erro: Banco de dados '{db_path}' não encontrado.")
        print("💡 Execute 'python multilingual_cli.py' primeiro para criar dados.")
        return
    
    print("🔄 Conectando ao banco de dados...")
    db = DatabaseManager(db_path)
    
    try:
        print("📊 Exportando dados para Power BI...")
        
        # 1. TABELA DE CONTAS (com cálculos adicionais)
        print("  📋 Exportando contas...")
        accounts_query = """
        SELECT 
            id,
            name as account_name,
            CAST(balance AS REAL) as balance_numeric,
            balance as balance_text,
            created_at,
            date(created_at) as created_date,
            strftime('%Y-%m', created_at) as created_year_month,
            strftime('%Y', created_at) as created_year,
            CASE 
                WHEN CAST(balance AS REAL) >= 10000 THEN 'Alto'
                WHEN CAST(balance AS REAL) >= 1000 THEN 'Médio'
                WHEN CAST(balance AS REAL) > 0 THEN 'Baixo'
                ELSE 'Zero'
            END as balance_category
        FROM accounts
        ORDER BY balance_numeric DESC
        """
        
        accounts_df = pd.read_sql_query(accounts_query, db.connection)
        
        # Salvar em múltiplos formatos
        accounts_df.to_csv(f'{output_dir}/accounts.csv', index=False, encoding='utf-8-sig')
        accounts_df.to_excel(f'{output_dir}/accounts.xlsx', index=False)
        
        print(f"    ✅ {len(accounts_df)} contas exportadas")
        
        # 2. TABELA DE TRANSAÇÕES (com dados enriquecidos)
        print("  💰 Exportando transações...")
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
            CASE 
                WHEN t.transaction_type = 'deposit' THEN 'Depósito'
                WHEN t.transaction_type = 'withdrawal' THEN 'Saque'
                WHEN t.transaction_type = 'transfer' THEN 'Transferência'
                ELSE t.transaction_type
            END as transaction_type_pt,
            t.description,
            t.created_at,
            date(t.created_at) as transaction_date,
            strftime('%Y-%m', t.created_at) as year_month,
            strftime('%Y', t.created_at) as year,
            strftime('%m', t.created_at) as month,
            strftime('%d', t.created_at) as day,
            strftime('%w', t.created_at) as weekday,
            CASE strftime('%w', t.created_at)
                WHEN '0' THEN 'Domingo'
                WHEN '1' THEN 'Segunda'
                WHEN '2' THEN 'Terça'
                WHEN '3' THEN 'Quarta'
                WHEN '4' THEN 'Quinta'
                WHEN '5' THEN 'Sexta'
                WHEN '6' THEN 'Sábado'
            END as weekday_name,
            CASE 
                WHEN CAST(t.amount AS REAL) >= 1000 THEN 'Grande'
                WHEN CAST(t.amount AS REAL) >= 100 THEN 'Média'
                ELSE 'Pequena'
            END as amount_category
        FROM transactions t
        LEFT JOIN accounts fa ON t.from_account_id = fa.id
        LEFT JOIN accounts ta ON t.to_account_id = ta.id
        ORDER BY t.created_at DESC
        """
        
        transactions_df = pd.read_sql_query(transactions_query, db.connection)
        
        # Converter datas para formato adequado
        transactions_df['created_at'] = pd.to_datetime(transactions_df['created_at'])
        transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'])
        
        transactions_df.to_csv(f'{output_dir}/transactions.csv', index=False, encoding='utf-8-sig')
        transactions_df.to_excel(f'{output_dir}/transactions.xlsx', index=False)
        
        print(f"    ✅ {len(transactions_df)} transações exportadas")
        
        # 3. RESUMO MENSAL
        print("  📊 Criando resumo mensal...")
        monthly_summary_query = """
        SELECT 
            strftime('%Y-%m', created_at) as year_month,
            strftime('%Y', created_at) as year,
            strftime('%m', created_at) as month,
            transaction_type,
            CASE 
                WHEN transaction_type = 'deposit' THEN 'Depósito'
                WHEN transaction_type = 'withdrawal' THEN 'Saque'
                WHEN transaction_type = 'transfer' THEN 'Transferência'
                ELSE transaction_type
            END as transaction_type_pt,
            COUNT(*) as transaction_count,
            SUM(CAST(amount AS REAL)) as total_amount,
            AVG(CAST(amount AS REAL)) as avg_amount,
            MIN(CAST(amount AS REAL)) as min_amount,
            MAX(CAST(amount AS REAL)) as max_amount
        FROM transactions
        GROUP BY strftime('%Y-%m', created_at), transaction_type
        ORDER BY year_month, transaction_type
        """
        
        monthly_df = pd.read_sql_query(monthly_summary_query, db.connection)
        monthly_df.to_csv(f'{output_dir}/monthly_summary.csv', index=False, encoding='utf-8-sig')
        monthly_df.to_excel(f'{output_dir}/monthly_summary.xlsx', index=False)
        
        print(f"    ✅ {len(monthly_df)} registros de resumo mensal")
        
        # 4. ANÁLISE DE FLUXO DE CAIXA
        print("  💹 Criando análise de fluxo...")
        cashflow_query = """
        SELECT 
            date(created_at) as date,
            SUM(CASE WHEN transaction_type = 'deposit' THEN CAST(amount AS REAL) ELSE 0 END) as inflow,
            SUM(CASE WHEN transaction_type = 'withdrawal' THEN CAST(amount AS REAL) ELSE 0 END) as outflow,
            SUM(CASE WHEN transaction_type = 'deposit' THEN CAST(amount AS REAL) ELSE 0 END) - 
            SUM(CASE WHEN transaction_type = 'withdrawal' THEN CAST(amount AS REAL) ELSE 0 END) as net_flow,
            COUNT(*) as total_transactions
        FROM transactions
        WHERE transaction_type IN ('deposit', 'withdrawal')
        GROUP BY date(created_at)
        ORDER BY date
        """
        
        cashflow_df = pd.read_sql_query(cashflow_query, db.connection)
        cashflow_df['date'] = pd.to_datetime(cashflow_df['date'])
        cashflow_df.to_csv(f'{output_dir}/cashflow_analysis.csv', index=False, encoding='utf-8-sig')
        
        # 5. KPIs PARA DASHBOARD
        print("  📈 Gerando KPIs...")
        kpis_query = """
        SELECT 
            (SELECT COUNT(*) FROM accounts) as total_accounts,
            (SELECT SUM(CAST(balance AS REAL)) FROM accounts) as total_balance,
            (SELECT COUNT(*) FROM transactions) as total_transactions,
            (SELECT COUNT(*) FROM transactions WHERE date(created_at) = date('now')) as today_transactions,
            (SELECT COUNT(*) FROM transactions WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')) as month_transactions,
            (SELECT AVG(CAST(balance AS REAL)) FROM accounts) as avg_balance,
            (SELECT AVG(CAST(amount AS REAL)) FROM transactions) as avg_transaction_amount
        """
        
        kpis_df = pd.read_sql_query(kpis_query, db.connection)
        kpis_df.to_csv(f'{output_dir}/kpis.csv', index=False, encoding='utf-8-sig')
        
        # 6. CRIAR ARQUIVO DE CONEXÃO PARA POWER BI
        connection_info = f"""
# Informações de Conexão Power BI - CoreLedger
# Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Arquivos Exportados:
- accounts.csv / accounts.xlsx          - Dados das contas
- transactions.csv / transactions.xlsx  - Dados das transações  
- monthly_summary.csv / monthly_summary.xlsx - Resumo mensal
- cashflow_analysis.csv                 - Análise de fluxo de caixa
- kpis.csv                             - Indicadores principais

## Para Power BI Desktop:
1. Obter Dados → Texto/CSV
2. Selecione os arquivos CSV desta pasta
3. Configure relacionamentos:
   - accounts[id] ↔ transactions[from_account_id]
   - accounts[id] ↔ transactions[to_account_id]

## Para conexão direta SQLite:
1. Obter Dados → SQLite
2. Selecione: {os.path.abspath(db_path)}
3. Importe tabelas: accounts, transactions

## Campos Principais:
- Contas: id, account_name, balance_numeric, balance_category
- Transações: amount_numeric, transaction_type_pt, transaction_date
- Datas: Use 'transaction_date' para eixos temporais
"""
        
        with open(f'{output_dir}/POWERBI_CONNECTION_INFO.txt', 'w', encoding='utf-8') as f:
            f.write(connection_info)
        
        print(f"\n🎉 Exportação concluída com sucesso!")
        print(f"📁 Arquivos salvos em: {os.path.abspath(output_dir)}")
        print(f"📊 Total de dados exportados:")
        print(f"   - {len(accounts_df)} contas")
        print(f"   - {len(transactions_df)} transações")
        print(f"   - {len(monthly_df)} registros mensais")
        print(f"   - {len(cashflow_df)} registros de fluxo")
        
        print(f"\n💡 Próximos passos:")
        print(f"   1. Abra o Power BI Desktop")
        print(f"   2. Importe os arquivos .csv ou .xlsx da pasta '{output_dir}'")
        print(f"   3. Configure relacionamentos entre tabelas")
        print(f"   4. Crie suas visualizações!")
        
    except Exception as e:
        print(f"❌ Erro durante exportação: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


def show_sample_data():
    """Mostra exemplos dos dados disponíveis"""
    
    if not os.path.exists("multilingual_bank.db"):
        print("❌ Banco de dados não encontrado. Execute 'python multilingual_cli.py' primeiro.")
        return
    
    db = DatabaseManager("multilingual_bank.db")
    
    try:
        cursor = db.connection.cursor()
        
        print("📊 AMOSTRA DOS DADOS DISPONÍVEIS")
        print("=" * 50)
        
        # Contas
        cursor.execute("SELECT COUNT(*) FROM accounts")
        accounts_count = cursor.fetchone()[0]
        print(f"\n👥 CONTAS ({accounts_count} registros):")
        
        cursor.execute("SELECT id, name, balance FROM accounts LIMIT 3")
        for row in cursor.fetchall():
            print(f"   ID: {row[0]} | Nome: {row[1]} | Saldo: R$ {row[2]}")
        
        # Transações
        cursor.execute("SELECT COUNT(*) FROM transactions")
        transactions_count = cursor.fetchone()[0]
        print(f"\n💰 TRANSAÇÕES ({transactions_count} registros):")
        
        cursor.execute("""
            SELECT transaction_type, amount, created_at 
            FROM transactions 
            ORDER BY created_at DESC 
            LIMIT 3
        """)
        for row in cursor.fetchall():
            print(f"   Tipo: {row[0]} | Valor: R$ {row[1]} | Data: {row[2]}")
        
        # Resumo por tipo
        print(f"\n📈 RESUMO POR TIPO:")
        cursor.execute("""
            SELECT transaction_type, COUNT(*), SUM(CAST(amount AS REAL))
            FROM transactions 
            GROUP BY transaction_type
        """)
        for row in cursor.fetchall():
            print(f"   {row[0]}: {row[1]} transações, Total: R$ {row[2]:.2f}")
        
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--sample":
        show_sample_data()
    else:
        export_data_for_powerbi()