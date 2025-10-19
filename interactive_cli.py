"""
Interactive CLI for CoreLedger Bank System

A complete terminal-based interface for managing bank accounts,
performing transactions, and viewing account information.
"""

import sys
import os
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ledger import BankLedger, AccountNotFoundError, LedgerError
from models.account import InsufficientFundsError, InvalidAmountError


class BankCLI:
    """Interactive command-line interface for the bank ledger system."""
    
    def __init__(self, db_path: str = "bank_accounts.db"):
        """Initialize the CLI with a database path."""
        self.db_path = db_path
        self.ledger = None
        self.running = True
        
    def start(self):
        """Start the interactive CLI session."""
        self.ledger = BankLedger(self.db_path)
        
        print("=" * 60)
        print("🏦 Welcome to CoreLedger Bank System")
        print("=" * 60)
        print(f"Database: {self.db_path}")
        print(f"Accounts: {len(self.ledger.list_accounts())}")
        print(f"Total Balance: ${self.ledger.get_total_system_balance()}")
        print()
        
        try:
            while self.running:
                self.show_main_menu()
                choice = self.get_user_input("Select an option (1-9): ").strip()
                self.handle_main_menu_choice(choice)
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for using CoreLedger.")
        except Exception as e:
            print(f"\n❌ An unexpected error occurred: {e}")
        finally:
            if self.ledger:
                self.ledger.close()
    
    def show_main_menu(self):
        """Display the main menu options."""
        print("\n" + "=" * 40)
        print("📋 MAIN MENU")
        print("=" * 40)
        print("1. 👤 Create New Account")
        print("2. 💰 Make Deposit")
        print("3. 💸 Make Withdrawal")
        print("4. 🔄 Transfer Money")
        print("5. 💳 View Account Details")
        print("6. 📊 View All Accounts")
        print("7. 📜 View Transaction History")
        print("8. 🗑️  Delete Account")
        print("9. 🚪 Exit")
        print("-" * 40)
    
    def handle_main_menu_choice(self, choice: str):
        """Handle user's main menu selection."""
        menu_actions = {
            '1': self.create_account,
            '2': self.make_deposit,
            '3': self.make_withdrawal,
            '4': self.transfer_money,
            '5': self.view_account_details,
            '6': self.view_all_accounts,
            '7': self.view_transaction_history,
            '8': self.delete_account,
            '9': self.exit_application,
        }
        
        if choice in menu_actions:
            menu_actions[choice]()
        else:
            print("❌ Invalid choice. Please select 1-9.")
    
    def create_account(self):
        """Handle account creation."""
        print("\n" + "=" * 40)
        print("👤 CREATE NEW ACCOUNT")
        print("=" * 40)
        
        # Get account name
        while True:
            name = self.get_user_input("Enter account holder name: ").strip()
            if name:
                break
            print("❌ Account name cannot be empty.")
        
        # Get initial balance
        initial_balance = self.get_decimal_input("Enter initial balance (or press Enter for $0.00): ", default="0.00")
        if initial_balance is None:
            return
        
        try:
            account_id = self.ledger.create_account(name, str(initial_balance))
            print(f"✅ Account created successfully!")
            print(f"   Account ID: {account_id}")
            print(f"   Name: {name}")
            print(f"   Initial Balance: ${initial_balance}")
            
        except ValueError as e:
            print(f"❌ Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    def make_deposit(self):
        """Handle deposit operations."""
        print("\n" + "=" * 40)
        print("💰 MAKE DEPOSIT")
        print("=" * 40)
        
        account = self.select_account()
        if not account:
            return
        
        amount = self.get_decimal_input("Enter deposit amount: $")
        if amount is None or amount <= 0:
            print("❌ Invalid amount. Deposit must be positive.")
            return
        
        description = self.get_user_input("Enter description (optional): ").strip()
        
        try:
            new_balance = self.ledger.deposit(account.id, str(amount), description)
            print(f"✅ Deposit successful!")
            print(f"   Amount: ${amount}")
            print(f"   New Balance: ${new_balance}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def make_withdrawal(self):
        """Handle withdrawal operations."""
        print("\n" + "=" * 40)
        print("💸 MAKE WITHDRAWAL")
        print("=" * 40)
        
        account = self.select_account()
        if not account:
            return
        
        print(f"Current Balance: ${account.balance}")
        
        amount = self.get_decimal_input("Enter withdrawal amount: $")
        if amount is None or amount <= 0:
            print("❌ Invalid amount. Withdrawal must be positive.")
            return
        
        if amount > account.balance:
            print(f"❌ Insufficient funds. Available: ${account.balance}")
            return
        
        description = self.get_user_input("Enter description (optional): ").strip()
        
        try:
            new_balance = self.ledger.withdraw(account.id, str(amount), description)
            print(f"✅ Withdrawal successful!")
            print(f"   Amount: ${amount}")
            print(f"   New Balance: ${new_balance}")
            
        except InsufficientFundsError as e:
            print(f"❌ {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def transfer_money(self):
        """Handle money transfer operations."""
        print("\n" + "=" * 40)
        print("🔄 TRANSFER MONEY")
        print("=" * 40)
        
        print("Select FROM account:")
        from_account = self.select_account()
        if not from_account:
            return
        
        print(f"\nFrom Account: {from_account.name} (${from_account.balance})")
        print("Select TO account:")
        to_account = self.select_account(exclude_id=from_account.id)
        if not to_account:
            return
        
        print(f"\nTransfer Details:")
        print(f"From: {from_account.name} (${from_account.balance})")
        print(f"To: {to_account.name} (${to_account.balance})")
        
        amount = self.get_decimal_input("Enter transfer amount: $")
        if amount is None or amount <= 0:
            print("❌ Invalid amount. Transfer must be positive.")
            return
        
        if amount > from_account.balance:
            print(f"❌ Insufficient funds. Available: ${from_account.balance}")
            return
        
        description = self.get_user_input("Enter description (optional): ").strip()
        
        # Confirm transfer
        print(f"\n📋 Transfer Summary:")
        print(f"   From: {from_account.name}")
        print(f"   To: {to_account.name}")
        print(f"   Amount: ${amount}")
        print(f"   Description: {description or 'No description'}")
        
        if not self.confirm_action("Proceed with transfer?"):
            print("❌ Transfer cancelled.")
            return
        
        try:
            from_balance, to_balance = self.ledger.transfer(
                from_account.id, to_account.id, str(amount), description
            )
            print(f"✅ Transfer successful!")
            print(f"   {from_account.name} balance: ${from_balance}")
            print(f"   {to_account.name} balance: ${to_balance}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def view_account_details(self):
        """Display detailed account information."""
        print("\n" + "=" * 40)
        print("💳 ACCOUNT DETAILS")
        print("=" * 40)
        
        account = self.select_account()
        if not account:
            return
        
        print(f"\n📋 Account Information:")
        print(f"   ID: {account.id}")
        print(f"   Name: {account.name}")
        print(f"   Balance: ${account.balance}")
        print(f"   Created: {account.created_at.strftime('%Y-%m-%d %H:%M:%S') if account.created_at else 'Unknown'}")
        
        # Show recent transactions
        transactions = self.ledger.get_account_transactions(account.id)
        if transactions:
            print(f"\n📜 Recent Transactions (last 5):")
            for i, txn in enumerate(transactions[:5], 1):
                txn_type = self.format_transaction_type(txn, account.id)
                print(f"   {i}. {txn_type}: ${txn.amount} - {txn.description}")
        else:
            print("\n📜 No transactions found.")
    
    def view_all_accounts(self):
        """Display all accounts in the system."""
        print("\n" + "=" * 60)
        print("📊 ALL ACCOUNTS")
        print("=" * 60)
        
        accounts = self.ledger.list_accounts()
        if not accounts:
            print("No accounts found. Create an account first.")
            return
        
        total_balance = Decimal('0')
        
        print(f"{'ID':<4} {'Name':<25} {'Balance':<15} {'Created':<20}")
        print("-" * 64)
        
        for account in accounts:
            created_str = account.created_at.strftime('%Y-%m-%d %H:%M') if account.created_at else 'Unknown'
            print(f"{account.id:<4} {account.name:<25} ${account.balance:<14} {created_str:<20}")
            total_balance += account.balance
        
        print("-" * 64)
        print(f"{'Total:':<30} ${total_balance:<14}")
        print(f"Number of accounts: {len(accounts)}")
    
    def view_transaction_history(self):
        """Display transaction history for an account."""
        print("\n" + "=" * 40)
        print("📜 TRANSACTION HISTORY")
        print("=" * 40)
        
        account = self.select_account()
        if not account:
            return
        
        transactions = self.ledger.get_account_transactions(account.id)
        if not transactions:
            print(f"No transactions found for {account.name}.")
            return
        
        print(f"\n📋 Transaction History for {account.name}:")
        print(f"{'#':<3} {'Type':<12} {'Amount':<12} {'Description':<30}")
        print("-" * 57)
        
        for i, txn in enumerate(transactions, 1):
            txn_type = self.format_transaction_type(txn, account.id)
            description = txn.description[:27] + "..." if len(txn.description) > 30 else txn.description
            amount_str = f"${txn.amount}"
            print(f"{i:<3} {txn_type:<12} {amount_str:<12} {description:<30}")
        
        print(f"\nTotal transactions: {len(transactions)}")
    
    def delete_account(self):
        """Handle account deletion."""
        print("\n" + "=" * 40)
        print("🗑️  DELETE ACCOUNT")
        print("=" * 40)
        print("⚠️  WARNING: This action cannot be undone!")
        
        account = self.select_account()
        if not account:
            return
        
        if account.balance != 0:
            print(f"❌ Cannot delete account with non-zero balance (${account.balance}).")
            print("   Please withdraw all funds first.")
            return
        
        print(f"\n📋 Account to delete:")
        print(f"   ID: {account.id}")
        print(f"   Name: {account.name}")
        print(f"   Balance: ${account.balance}")
        
        if not self.confirm_action(f"Are you sure you want to delete {account.name}'s account?"):
            print("❌ Account deletion cancelled.")
            return
        
        try:
            success = self.ledger.delete_account(account.id)
            if success:
                print(f"✅ Account '{account.name}' deleted successfully.")
            else:
                print(f"❌ Failed to delete account.")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def select_account(self, exclude_id: Optional[int] = None) -> Optional[object]:
        """Allow user to select an account from available accounts."""
        accounts = self.ledger.list_accounts()
        if exclude_id:
            accounts = [acc for acc in accounts if acc.id != exclude_id]
        
        if not accounts:
            print("❌ No accounts available.")
            return None
        
        print("\nAvailable accounts:")
        for i, account in enumerate(accounts, 1):
            print(f"{i}. {account.name} (ID: {account.id}) - ${account.balance}")
        
        while True:
            try:
                choice = self.get_user_input(f"Select account (1-{len(accounts)}) or 'c' to cancel: ").strip().lower()
                
                if choice == 'c':
                    return None
                
                index = int(choice) - 1
                if 0 <= index < len(accounts):
                    return accounts[index]
                else:
                    print(f"❌ Invalid choice. Please select 1-{len(accounts)} or 'c'.")
                    
            except ValueError:
                print("❌ Invalid input. Please enter a number or 'c'.")
    
    def get_decimal_input(self, prompt: str, default: str = None) -> Optional[Decimal]:
        """Get decimal input from user with validation."""
        while True:
            try:
                user_input = self.get_user_input(prompt).strip()
                
                if not user_input and default is not None:
                    return Decimal(default)
                
                if not user_input:
                    print("❌ Amount cannot be empty.")
                    continue
                
                # Remove dollar sign if present
                if user_input.startswith('$'):
                    user_input = user_input[1:]
                
                amount = Decimal(user_input)
                if amount < 0:
                    print("❌ Amount cannot be negative.")
                    continue
                
                return amount
                
            except InvalidOperation:
                print("❌ Invalid amount. Please enter a valid number.")
            except KeyboardInterrupt:
                return None
    
    def get_user_input(self, prompt: str) -> str:
        """Get input from user with consistent formatting."""
        try:
            return input(f"➤ {prompt}")
        except KeyboardInterrupt:
            print("\n\n👋 Operation cancelled.")
            raise
    
    def confirm_action(self, message: str) -> bool:
        """Ask user for confirmation."""
        while True:
            response = self.get_user_input(f"{message} (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("❌ Please enter 'y' for yes or 'n' for no.")
    
    def format_transaction_type(self, transaction, account_id: int) -> str:
        """Format transaction type for display."""
        if transaction.transaction_type == "deposit":
            return "DEPOSIT +"
        elif transaction.transaction_type == "withdrawal":
            return "WITHDRAW -"
        elif transaction.transaction_type == "transfer":
            if transaction.from_account_id == account_id:
                return "SENT -"
            else:
                return "RECEIVED +"
        return transaction.transaction_type.upper()
    
    def exit_application(self):
        """Handle application exit."""
        print("\n" + "=" * 40)
        print("🚪 EXIT APPLICATION")
        print("=" * 40)
        
        accounts = self.ledger.list_accounts()
        total_balance = self.ledger.get_total_system_balance()
        
        print(f"📊 Session Summary:")
        print(f"   Total Accounts: {len(accounts)}")
        print(f"   Total Balance: ${total_balance}")
        print(f"   Database: {self.db_path}")
        
        print("\n👋 Thank you for using CoreLedger Bank System!")
        print("💾 All data has been automatically saved.")
        
        self.running = False


def main():
    """Main entry point for the CLI application."""
    # Get database path from command line or use default
    db_path = sys.argv[1] if len(sys.argv) > 1 else "interactive_bank.db"
    
    try:
        cli = BankCLI(db_path)
        cli.start()
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()