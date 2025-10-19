"""
Multilingual Interactive CLI for CoreLedger Bank System

A complete terminal-based interface with support for multiple languages,
allowing users to select their preferred language at startup.
"""

import sys
import os
import json
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ledger import BankLedger, AccountNotFoundError, LedgerError
from models.account import InsufficientFundsError, InvalidAmountError
from i18n import _, select_language_interactive, get_language_manager


class MultilingualBankCLI:
    """Multilingual interactive command-line interface for the bank ledger system."""
    
    def __init__(self, db_path: str = "bank_accounts.db"):
        """Initialize the CLI with a database path."""
        self.db_path = db_path
        self.ledger = None
        self.running = True
        self.lang_manager = get_language_manager()
        
    def start(self):
        """Start the interactive CLI session with language selection."""
        # Language selection at startup
        self.select_startup_language()
        
        # Initialize ledger
        self.ledger = BankLedger(self.db_path)
        
        # Welcome message
        print("=" * 60)
        print(f"🏦 {_('app_welcome')}")
        print("=" * 60)
        print(_('summary_database', path=self.db_path))
        print(_('summary_accounts', count=len(self.ledger.list_accounts())))
        print(_('summary_balance', balance=self.format_currency(self.ledger.get_total_system_balance())))
        print()
        
        try:
            while self.running:
                self.show_main_menu()
                choice = self.get_user_input(_('menu_select')).strip()
                self.handle_main_menu_choice(choice)
        except KeyboardInterrupt:
            print(f"\n\n👋 {_('app_goodbye')}")
        except Exception as e:
            print(f"\n❌ {_('error_unexpected', error=str(e))}")
        finally:
            if self.ledger:
                self.ledger.close()
    
    def select_startup_language(self):
        """Handle language selection at startup."""
        # Check if there's a saved language preference
        config_file = os.path.join(os.path.dirname(self.db_path), '.coreledger_config.json')
        saved_language = None
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    saved_language = config.get('language')
        except:
            pass
        
        # If no saved language, prompt for selection
        if not saved_language:
            selected_language = select_language_interactive()
            
            # Save language preference
            try:
                config = {'language': selected_language}
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f)
            except:
                pass  # Continue without saving if there's an error
        else:
            # Use saved language
            self.lang_manager.set_language(saved_language)
            print(f"🌍 {_('lang_selected', language=self.lang_manager.get_language_name())}")
    
    def format_currency(self, amount: Decimal) -> str:
        """Format currency according to current language settings."""
        currency_format = _('currency_format')
        try:
            return currency_format.format(amount=amount)
        except:
            return f"${amount}"  # Fallback
    
    def show_main_menu(self):
        """Display the main menu options."""
        print("\n" + "=" * 40)
        print(f"📋 {_('menu_title')}")
        print("=" * 40)
        print(f"1. 👤 {_('menu_create_account')}")
        print(f"2. 💰 {_('menu_deposit')}")
        print(f"3. 💸 {_('menu_withdraw')}")
        print(f"4. 🔄 {_('menu_transfer')}")
        print(f"5. 💳 {_('menu_view_account')}")
        print(f"6. 📊 {_('menu_view_all')}")
        print(f"7. 📜 {_('menu_history')}")
        print(f"8. 🗑️  {_('menu_delete')}")
        print(f"9. 🚪 {_('menu_exit')}")
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
            print(f"❌ {_('menu_invalid')}")
    
    def create_account(self):
        """Handle account creation."""
        print("\n" + "=" * 40)
        print(f"👤 {_('create_title')}")
        print("=" * 40)
        
        # Get account name
        while True:
            name = self.get_user_input(_('create_name_prompt')).strip()
            if name:
                break
            print(f"❌ {_('create_name_empty')}")
        
        # Get initial balance
        initial_balance = self.get_decimal_input(_('create_balance_prompt'), default="0.00")
        if initial_balance is None:
            return
        
        try:
            account_id = self.ledger.create_account(name, str(initial_balance))
            print(f"✅ {_('create_success')}")
            print(f"   {_('create_account_id', id=account_id)}")
            print(f"   {_('create_account_name', name=name)}")
            print(f"   {_('create_initial_balance', balance=initial_balance)}")
            
        except ValueError as e:
            if "already exists" in str(e):
                print(f"❌ {_('create_duplicate', name=name)}")
            else:
                print(f"❌ {_('app_error')}: {e}")
        except Exception as e:
            print(f"❌ {_('error_unexpected', error=str(e))}")
    
    def make_deposit(self):
        """Handle deposit operations."""
        print("\n" + "=" * 40)
        print(f"💰 {_('deposit_title')}")
        print("=" * 40)
        
        account = self.select_account()
        if not account:
            return
        
        amount = self.get_decimal_input(_('deposit_amount_prompt'))
        if amount is None or amount <= 0:
            print(f"❌ {_('deposit_invalid_amount')}")
            return
        
        description = self.get_user_input(_('deposit_description_prompt')).strip()
        
        try:
            new_balance = self.ledger.deposit(account.id, str(amount), description)
            print(f"✅ {_('deposit_success')}")
            print(f"   {_('deposit_amount', amount=amount)}")
            print(f"   {_('deposit_new_balance', balance=new_balance)}")
            
        except Exception as e:
            print(f"❌ {_('app_error')}: {e}")
    
    def make_withdrawal(self):
        """Handle withdrawal operations."""
        print("\n" + "=" * 40)
        print(f"💸 {_('withdraw_title')}")
        print("=" * 40)
        
        account = self.select_account()
        if not account:
            return
        
        print(f"{_('withdraw_current_balance', balance=account.balance)}")
        
        amount = self.get_decimal_input(_('withdraw_amount_prompt'))
        if amount is None or amount <= 0:
            print(f"❌ {_('withdraw_invalid_amount')}")
            return
        
        if amount > account.balance:
            print(f"❌ {_('withdraw_insufficient', available=account.balance)}")
            return
        
        description = self.get_user_input(_('withdraw_description_prompt')).strip()
        
        try:
            new_balance = self.ledger.withdraw(account.id, str(amount), description)
            print(f"✅ {_('withdraw_success')}")
            print(f"   {_('withdraw_amount', amount=amount)}")
            print(f"   {_('withdraw_new_balance', balance=new_balance)}")
            
        except InsufficientFundsError:
            print(f"❌ {_('withdraw_insufficient', available=account.balance)}")
        except Exception as e:
            print(f"❌ {_('app_error')}: {e}")
    
    def transfer_money(self):
        """Handle money transfer operations."""
        print("\n" + "=" * 40)
        print(f"🔄 {_('transfer_title')}")
        print("=" * 40)
        
        print(_('transfer_from'))
        from_account = self.select_account()
        if not from_account:
            return
        
        print(f"\n{_('transfer_from_account', name=from_account.name, balance=from_account.balance)}")
        print(_('transfer_to'))
        to_account = self.select_account(exclude_id=from_account.id)
        if not to_account:
            return
        
        print(f"\n{_('transfer_details')}")
        print(f"{_('transfer_from_account', name=from_account.name, balance=from_account.balance)}")
        print(f"{_('transfer_to_account', name=to_account.name, balance=to_account.balance)}")
        
        amount = self.get_decimal_input(_('transfer_amount_prompt'))
        if amount is None or amount <= 0:
            print(f"❌ {_('deposit_invalid_amount')}")
            return
        
        if amount > from_account.balance:
            print(f"❌ {_('transfer_insufficient', available=from_account.balance)}")
            return
        
        description = self.get_user_input(_('transfer_description_prompt')).strip()
        
        # Confirm transfer
        print(f"\n📋 {_('transfer_summary')}")
        print(f"   {_('transfer_from_account', name=from_account.name, balance=from_account.balance)}")
        print(f"   {_('transfer_to_account', name=to_account.name, balance=to_account.balance)}")
        print(f"   {_('deposit_amount', amount=amount)}")
        print(f"   Description: {description or _('details_no_transactions')}")
        
        if not self.confirm_action(_('transfer_confirm')):
            print(f"❌ {_('transfer_cancelled')}")
            return
        
        try:
            from_balance, to_balance = self.ledger.transfer(
                from_account.id, to_account.id, str(amount), description
            )
            print(f"✅ {_('transfer_success')}")
            print(f"   {from_account.name}: {self.format_currency(from_balance)}")
            print(f"   {to_account.name}: {self.format_currency(to_balance)}")
            
        except Exception as e:
            print(f"❌ {_('app_error')}: {e}")
    
    def view_account_details(self):
        """Display detailed account information."""
        print("\n" + "=" * 40)
        print(f"💳 {_('details_title')}")
        print("=" * 40)
        
        account = self.select_account()
        if not account:
            return
        
        print(f"\n📋 {_('details_info')}")
        print(f"   {_('details_id', id=account.id)}")
        print(f"   {_('details_name', name=account.name)}")
        print(f"   {_('details_balance', balance=account.balance)}")
        if account.created_at:
            print(f"   {_('details_created', date=account.created_at.strftime('%Y-%m-%d %H:%M:%S'))}")
        
        # Show recent transactions
        transactions = self.ledger.get_account_transactions(account.id)
        if transactions:
            print(f"\n📜 {_('details_transactions')}")
            for i, txn in enumerate(transactions[:5], 1):
                txn_type = self.format_transaction_type(txn, account.id)
                print(f"   {i}. {txn_type}: {self.format_currency(txn.amount)} - {txn.description}")
        else:
            print(f"\n📜 {_('details_no_transactions')}")
    
    def view_all_accounts(self):
        """Display all accounts in the system."""
        print("\n" + "=" * 60)
        print(f"📊 {_('all_accounts_title')}")
        print("=" * 60)
        
        accounts = self.ledger.list_accounts()
        if not accounts:
            print(_('all_accounts_empty'))
            return
        
        total_balance = Decimal('0')
        
        print(f"{'ID':<4} {'Name':<25} {'Balance':<15} {'Created':<20}")
        print("-" * 64)
        
        for account in accounts:
            created_str = account.created_at.strftime('%Y-%m-%d %H:%M') if account.created_at else 'Unknown'
            balance_str = self.format_currency(account.balance)
            print(f"{account.id:<4} {account.name:<25} {balance_str:<15} {created_str:<20}")
            total_balance += account.balance
        
        print("-" * 64)
        print(f"{_('all_accounts_total'):<30} {self.format_currency(total_balance):<15}")
        print(_('all_accounts_count', count=len(accounts)))
    
    def view_transaction_history(self):
        """Display transaction history for an account."""
        print("\n" + "=" * 40)
        print(f"📜 {_('history_title')}")
        print("=" * 40)
        
        account = self.select_account()
        if not account:
            return
        
        transactions = self.ledger.get_account_transactions(account.id)
        if not transactions:
            print(_('history_empty', name=account.name))
            return
        
        print(f"\n📋 {_('history_for', name=account.name)}")
        print(f"{'#':<3} {'Type':<12} {'Amount':<12} {'Description':<30}")
        print("-" * 57)
        
        for i, txn in enumerate(transactions, 1):
            txn_type = self.format_transaction_type(txn, account.id)
            description = txn.description[:27] + "..." if len(txn.description) > 30 else txn.description
            amount_str = self.format_currency(txn.amount)
            print(f"{i:<3} {txn_type:<12} {amount_str:<12} {description:<30}")
        
        print(f"\n{_('history_total', count=len(transactions))}")
    
    def delete_account(self):
        """Handle account deletion."""
        print("\n" + "=" * 40)
        print(f"🗑️  {_('delete_title')}")
        print("=" * 40)
        print(f"⚠️  {_('delete_warning')}")
        
        account = self.select_account()
        if not account:
            return
        
        if account.balance != 0:
            print(f"❌ {_('delete_nonzero', balance=account.balance)}")
            print(f"   {_('delete_withdraw_first')}")
            return
        
        print(f"\n📋 {_('delete_details')}")
        print(f"   {_('details_id', id=account.id)}")
        print(f"   {_('details_name', name=account.name)}")
        print(f"   {_('details_balance', balance=account.balance)}")
        
        if not self.confirm_action(_('delete_confirm', name=account.name)):
            print(f"❌ {_('delete_cancelled')}")
            return
        
        try:
            success = self.ledger.delete_account(account.id)
            if success:
                print(f"✅ {_('delete_success', name=account.name)}")
            else:
                print(f"❌ {_('delete_failed')}")
                
        except Exception as e:
            print(f"❌ {_('app_error')}: {e}")
    
    def select_account(self, exclude_id: Optional[int] = None) -> Optional[object]:
        """Allow user to select an account from available accounts."""
        accounts = self.ledger.list_accounts()
        if exclude_id:
            accounts = [acc for acc in accounts if acc.id != exclude_id]
        
        if not accounts:
            print(f"❌ {_('select_no_accounts')}")
            return None
        
        print(f"\n{_('select_available')}")
        for i, account in enumerate(accounts, 1):
            balance_str = self.format_currency(account.balance)
            print(f"{i}. {account.name} (ID: {account.id}) - {balance_str}")
        
        while True:
            try:
                choice = self.get_user_input(_('select_prompt', count=len(accounts))).strip().lower()
                
                if choice == 'c':
                    return None
                
                index = int(choice) - 1
                if 0 <= index < len(accounts):
                    return accounts[index]
                else:
                    print(f"❌ {_('select_invalid', count=len(accounts))}")
                    
            except ValueError:
                print(f"❌ {_('select_invalid_input')}")
    
    def get_decimal_input(self, prompt: str, default: str = None) -> Optional[Decimal]:
        """Get decimal input from user with validation."""
        while True:
            try:
                user_input = self.get_user_input(prompt).strip()
                
                if not user_input and default is not None:
                    return Decimal(default)
                
                if not user_input:
                    print(f"❌ {_('input_empty_amount')}")
                    continue
                
                # Remove currency symbols
                currency_symbol = _('currency_symbol')
                if user_input.startswith(currency_symbol):
                    user_input = user_input[len(currency_symbol):]
                elif user_input.startswith('$'):
                    user_input = user_input[1:]
                
                amount = Decimal(user_input)
                if amount < 0:
                    print(f"❌ {_('input_negative_amount')}")
                    continue
                
                return amount
                
            except InvalidOperation:
                print(f"❌ {_('input_invalid_amount')}")
            except KeyboardInterrupt:
                return None
    
    def get_user_input(self, prompt: str) -> str:
        """Get input from user with consistent formatting."""
        try:
            return input(f"➤ {prompt}")
        except KeyboardInterrupt:
            print(f"\n\n{_('input_cancelled')}")
            raise
    
    def confirm_action(self, message: str) -> bool:
        """Ask user for confirmation."""
        while True:
            # Get appropriate yes/no responses for current language
            yes_responses = [_('app_yes').lower(), 'y', 'yes', 'si', 'sí', 'oui', 'ja', 'はい', '是']
            no_responses = [_('app_no').lower(), 'n', 'no', 'non', 'nein', 'いいえ', '否']
            
            response = self.get_user_input(_('input_confirm_prompt', message=message)).strip().lower()
            
            if response in yes_responses:
                return True
            elif response in no_responses:
                return False
            else:
                print(f"❌ {_('input_confirm_invalid')}")
    
    def format_transaction_type(self, transaction, account_id: int) -> str:
        """Format transaction type for display."""
        if transaction.transaction_type == "deposit":
            return _('txn_deposit_plus')
        elif transaction.transaction_type == "withdrawal":
            return _('txn_withdraw_minus')
        elif transaction.transaction_type == "transfer":
            if transaction.from_account_id == account_id:
                return _('txn_sent_minus')
            else:
                return _('txn_received_plus')
        return transaction.transaction_type.upper()
    
    def exit_application(self):
        """Handle application exit."""
        print("\n" + "=" * 40)
        print(f"🚪 {_('menu_exit')}")
        print("=" * 40)
        
        accounts = self.ledger.list_accounts()
        total_balance = self.ledger.get_total_system_balance()
        
        print(f"📊 {_('summary_title')}")
        print(f"   {_('summary_accounts', count=len(accounts))}")
        print(f"   {_('summary_balance', balance=self.format_currency(total_balance))}")
        print(f"   {_('summary_database', path=self.db_path)}")
        
        print(f"\n👋 {_('app_goodbye')}")
        print(f"💾 {_('summary_saved')}")
        
        self.running = False


def main():
    """Main entry point for the multilingual CLI application."""
    # Get database path from command line or use default
    db_path = sys.argv[1] if len(sys.argv) > 1 else "multilingual_bank.db"
    
    try:
        cli = MultilingualBankCLI(db_path)
        cli.start()
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()