"""
Interactive CLI Test with Sample Data

This script creates sample accounts and transactions, 
then shows how to use the interactive CLI interface.
"""

import sys
import os
from decimal import Decimal

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ledger import BankLedger

def create_sample_data():
    """Create sample accounts and transactions for demonstration."""
    print("🔧 Setting up sample data...")
    
    # Remove existing demo database
    db_path = "cli_demo.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Create ledger and sample data
    with BankLedger(db_path) as ledger:
        # Create accounts
        alice_id = ledger.create_account("Alice Johnson", "2500.00")
        bob_id = ledger.create_account("Bob Smith", "1800.00")
        charlie_id = ledger.create_account("Charlie Brown", "500.00")
        business_id = ledger.create_account("Tech Corp LLC", "15000.00")
        
        # Add some transactions
        ledger.deposit(alice_id, "500.00", "Salary bonus")
        ledger.withdraw(bob_id, "200.00", "ATM withdrawal")
        ledger.transfer(alice_id, charlie_id, "300.00", "Birthday gift")
        ledger.deposit(business_id, "2500.00", "Client payment")
        ledger.transfer(business_id, alice_id, "1000.00", "Consulting fee")
        ledger.withdraw(charlie_id, "50.00", "Coffee money")
        
        print(f"✅ Created {len(ledger.list_accounts())} accounts")
        print(f"✅ Total system balance: ${ledger.get_total_system_balance()}")
    
    return db_path

def show_cli_commands():
    """Show example CLI commands and usage."""
    print("\n" + "=" * 60)
    print("🎮 INTERACTIVE CLI FEATURES")
    print("=" * 60)
    
    features = [
        ("1. Create Account", "Add new bank accounts with initial balances"),
        ("2. Make Deposit", "Add money to any account with description"),
        ("3. Make Withdrawal", "Remove money with balance validation"),
        ("4. Transfer Money", "Move money between accounts safely"),
        ("5. View Account", "See detailed account info and recent transactions"),
        ("6. View All Accounts", "Complete overview of all accounts and balances"),
        ("7. Transaction History", "Full audit trail of all operations"),
        ("8. Delete Account", "Remove accounts with zero balance"),
    ]
    
    for title, description in features:
        print(f"   {title:<20} - {description}")
    
    print("\n💡 Pro Tips:")
    print("   • All amounts are validated for precision")
    print("   • Insufficient funds are automatically prevented")
    print("   • Transaction descriptions help track operations")
    print("   • Data is automatically saved to SQLite")
    print("   • Use Ctrl+C to safely exit at any time")

def main():
    """Main demo function."""
    print("🏦 CoreLedger Interactive CLI Demo")
    print("=" * 50)
    
    # Create sample data
    db_path = create_sample_data()
    
    # Show features
    show_cli_commands()
    
    print("\n" + "=" * 60)
    print("🚀 READY TO START INTERACTIVE SESSION")
    print("=" * 60)
    print(f"Database: {db_path}")
    print("Sample accounts have been created for testing.")
    print()
    print("Try these operations:")
    print("• View all accounts (option 6) to see sample data")
    print("• Make a deposit to Alice Johnson")
    print("• Transfer money between accounts")
    print("• View transaction history")
    print("• Create your own account")
    print()
    
    try:
        response = input("🎯 Start interactive CLI now? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            print("\n🎮 Starting Interactive CLI...")
            print("=" * 40)
            
            # Start the interactive CLI
            from interactive_cli import BankCLI
            cli = BankCLI(db_path)
            cli.start()
        else:
            print(f"\n💾 Sample data saved to: {db_path}")
            print(f"Run: python interactive_cli.py {db_path}")
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")

if __name__ == "__main__":
    main()