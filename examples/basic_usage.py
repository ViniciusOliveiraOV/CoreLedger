"""
Example usage of the CoreLedger bank ledger system.

This script demonstrates basic operations including:
- Creating accounts
- Making deposits and withdrawals  
- Transferring money between accounts
- Viewing transaction history
- Checking balance consistency
"""

import sys
import os
from decimal import Decimal

# Add the src directory to Python path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ledger import BankLedger


def main():
    """Demonstrate basic ledger operations."""
    print("=== CoreLedger Bank System Demo ===\n")
    
    # Create a new ledger (will create bank_demo.db file)
    with BankLedger("bank_demo.db") as ledger:
        
        # Create some accounts
        print("1. Creating accounts...")
        alice_id = ledger.create_account("Alice Johnson", "1000.00")
        bob_id = ledger.create_account("Bob Smith", "500.00")
        charlie_id = ledger.create_account("Charlie Brown", "0.00")
        
        print(f"   - Alice's account ID: {alice_id}")
        print(f"   - Bob's account ID: {bob_id}")
        print(f"   - Charlie's account ID: {charlie_id}")
        
        # Display initial balances
        print("\n2. Initial balances:")
        for account in ledger.list_accounts():
            print(f"   - {account.name}: ${account.balance}")
        
        print(f"\n   Total system balance: ${ledger.get_total_system_balance()}")
        
        # Perform some operations
        print("\n3. Performing transactions...")
        
        # Alice gets her salary
        print("   - Alice receives salary deposit of $2,500...")
        ledger.deposit(alice_id, "2500.00", "Monthly salary")
        print(f"     Alice's new balance: ${ledger.get_balance(alice_id)}")
        
        # Bob withdraws some cash
        print("   - Bob withdraws $100 from ATM...")
        ledger.withdraw(bob_id, "100.00", "ATM withdrawal")
        print(f"     Bob's new balance: ${ledger.get_balance(bob_id)}")
        
        # Alice lends money to Bob
        print("   - Alice transfers $300 to Bob...")
        alice_balance, bob_balance = ledger.transfer(
            alice_id, bob_id, "300.00", "Loan to Bob"
        )
        print(f"     Alice's new balance: ${alice_balance}")
        print(f"     Bob's new balance: ${bob_balance}")
        
        # Alice gives money to Charlie
        print("   - Alice transfers $200 to Charlie...")
        alice_balance, charlie_balance = ledger.transfer(
            alice_id, charlie_id, "200.00", "Gift to Charlie"
        )
        print(f"     Alice's new balance: ${alice_balance}")
        print(f"     Charlie's new balance: ${charlie_balance}")
        
        # Display final balances
        print("\n4. Final balances:")
        for account in ledger.list_accounts():
            print(f"   - {account.name}: ${account.balance}")
        
        print(f"\n   Total system balance: ${ledger.get_total_system_balance()}")
        
        # Show transaction history for Alice
        print("\n5. Alice's transaction history:")
        alice_transactions = ledger.get_account_transactions(alice_id)
        for i, transaction in enumerate(alice_transactions, 1):
            if transaction.transaction_type == "deposit":
                print(f"   {i}. DEPOSIT: +${transaction.amount} - {transaction.description}")
            elif transaction.transaction_type == "withdrawal":
                print(f"   {i}. WITHDRAWAL: -${transaction.amount} - {transaction.description}")
            elif transaction.transaction_type == "transfer":
                if transaction.from_account_id == alice_id:
                    print(f"   {i}. TRANSFER OUT: -${transaction.amount} - {transaction.description}")
                else:
                    print(f"   {i}. TRANSFER IN: +${transaction.amount} - {transaction.description}")
        
        # Demonstrate error handling
        print("\n6. Demonstrating error handling...")
        
        try:
            print("   - Attempting to withdraw $5000 from Charlie's account (insufficient funds)...")
            ledger.withdraw(charlie_id, "5000.00")
        except Exception as e:
            print(f"     Error: {e}")
        
        try:
            print("   - Attempting to transfer to same account...")
            ledger.transfer(alice_id, alice_id, "100.00")
        except Exception as e:
            print(f"     Error: {e}")
        
        try:
            print("   - Attempting to deposit negative amount...")
            ledger.deposit(alice_id, "-50.00")
        except Exception as e:
            print(f"     Error: {e}")
        
        print("\n7. Demonstrating decimal precision...")
        # Create test account for precision demo
        precision_id = ledger.create_account("Precision Test", "0.00")
        
        # Add amounts that would cause floating-point errors
        amounts = ["0.1", "0.2", "0.3"]
        for amount in amounts:
            ledger.deposit(precision_id, amount)
            print(f"   - Added ${amount}, balance: ${ledger.get_balance(precision_id)}")
        
        # The total should be exactly 0.60, not 0.6000000000000001
        final_precision_balance = ledger.get_balance(precision_id)
        print(f"   - Final precision test balance: ${final_precision_balance}")
        print(f"   - Is exactly $0.60? {final_precision_balance == Decimal('0.60')}")
        
        print("\n=== Demo Complete ===")
        print("\nThe database 'bank_demo.db' has been created with all the demo data.")
        print("You can inspect it or run the demo again to see persistent data.")


def demonstrate_advanced_features():
    """Demonstrate more advanced features of the ledger system."""
    print("\n=== Advanced Features Demo ===\n")
    
    with BankLedger("advanced_demo.db") as ledger:
        
        # Create multiple accounts
        accounts = {}
        account_names = ["Merchant Corp", "Supplier LLC", "Customer A", "Customer B", "Tax Authority"]
        
        for name in account_names:
            account_id = ledger.create_account(name, "1000.00")
            accounts[name] = account_id
        
        print("1. Created business accounts with $1000 each")
        
        # Simulate business transactions
        print("\n2. Simulating business transactions...")
        
        # Customer purchases
        ledger.transfer(accounts["Customer A"], accounts["Merchant Corp"], "250.00", "Purchase order #1001")
        ledger.transfer(accounts["Customer B"], accounts["Merchant Corp"], "175.50", "Purchase order #1002")
        
        # Merchant pays supplier
        ledger.transfer(accounts["Merchant Corp"], accounts["Supplier LLC"], "300.00", "Inventory purchase")
        
        # Tax payment
        ledger.transfer(accounts["Merchant Corp"], accounts["Tax Authority"], "85.25", "Monthly tax payment")
        
        print("   - Processed customer purchases and business payments")
        
        # Show business summary
        print("\n3. Business account summary:")
        for name, account_id in accounts.items():
            balance = ledger.get_balance(account_id)
            print(f"   - {name}: ${balance}")
        
        # Verify balance conservation
        total_balance = ledger.get_total_system_balance()
        expected_balance = Decimal("5000.00")  # 5 accounts × $1000 each
        print(f"\n4. Balance verification:")
        print(f"   - Total system balance: ${total_balance}")
        print(f"   - Expected balance: ${expected_balance}")
        print(f"   - Balances match: {total_balance == expected_balance}")


if __name__ == "__main__":
    main()
    demonstrate_advanced_features()