"""
Exemplo de uso da classe DatabaseTriggersManager

Este arquivo demonstra como usar os triggers de proteção do banco de dados
para garantir a integridade dos dados mesmo quando acessando diretamente o SQLite.
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.database import DatabaseManager, DatabaseTriggersManager


def main():
    """Demonstração dos triggers de proteção do banco de dados."""
    
    print("🏦 CoreLedger - Demonstração de Triggers de Proteção")
    print("=" * 60)
    
    # Inicializar banco de dados
    db_manager = DatabaseManager("exemplo_triggers.db")
    triggers_manager = DatabaseTriggersManager(db_manager)
    
    print("\n1️⃣  Listando triggers existentes:")
    triggers_manager.list_triggers()
    
    print("\n2️⃣  Criando conta de teste...")
    try:
        # Criar conta com saldo para teste
        db_manager.execute_query(
            "INSERT OR REPLACE INTO accounts (id, name, balance) VALUES (999, 'Teste Trigger', '100.50')"
        )
        print("✅ Conta de teste criada com saldo R$ 100,50")
    except Exception as e:
        print(f"❌ Erro ao criar conta: {e}")
    
    print("\n3️⃣  Testando trigger de prevenção de exclusão...")
    try:
        # Tentar deletar conta com saldo não-zero (deve falhar)
        db_manager.execute_query("DELETE FROM accounts WHERE id = 999")
        print("⚠️  ATENÇÃO: Trigger não impediu a exclusão!")
    except Exception as e:
        print(f"✅ Trigger funcionando: {e}")
    
    print("\n4️⃣  Testando trigger de saldo negativo...")
    try:
        # Tentar definir saldo negativo (deve falhar)
        db_manager.execute_query("UPDATE accounts SET balance = '-50.00' WHERE id = 999")
        print("⚠️  ATENÇÃO: Trigger não impediu saldo negativo!")
    except Exception as e:
        print(f"✅ Trigger funcionando: {e}")
    
    print("\n5️⃣  Testando trigger de transação inválida...")
    try:
        # Tentar criar transação com valor negativo (deve falhar)
        db_manager.execute_query(
            "INSERT INTO transactions (from_account_id, amount, transaction_type) VALUES (999, '-10.00', 'withdrawal')"
        )
        print("⚠️  ATENÇÃO: Trigger não impediu transação com valor negativo!")
    except Exception as e:
        print(f"✅ Trigger funcionando: {e}")
    
    print("\n6️⃣  Zerando saldo e deletando conta...")
    try:
        # Zerar saldo e tentar deletar (deve funcionar)
        db_manager.execute_query("UPDATE accounts SET balance = '0.00' WHERE id = 999")
        print("✅ Saldo zerado com sucesso")
        
        db_manager.execute_query("DELETE FROM accounts WHERE id = 999")
        print("✅ Conta deletada com sucesso após zerar saldo")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
    
    print("\n7️⃣  Demonstração de gerenciamento de triggers:")
    print("\n📋 Comandos disponíveis:")
    print("   triggers_manager.create_all_protection_triggers()  # Criar todos")
    print("   triggers_manager.drop_all_protection_triggers()    # Remover todos")
    print("   triggers_manager.list_triggers()                   # Listar existentes")
    print("   triggers_manager.test_triggers()                   # Testar funcionamento")
    
    # Fechar conexão
    db_manager.close()
    
    print("\n" + "=" * 60)
    print("✅ Demonstração concluída!")
    print("💡 Os triggers garantem integridade mesmo com acesso direto ao SQLite")
    

if __name__ == "__main__":
    main()