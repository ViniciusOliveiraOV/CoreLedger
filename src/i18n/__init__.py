"""
Internationalization (i18n) system for CoreLedger.

This module provides multilingual support with automatic language detection,
user language selection, and comprehensive translation management.
"""

import json
import os
import locale
from typing import Dict, List, Optional


class LanguageManager:
    """Manages language selection and translations for the application."""
    
    def __init__(self, translations_dir: str = None):
        """Initialize the language manager."""
        if translations_dir is None:
            translations_dir = os.path.join(os.path.dirname(__file__), 'translations')
        
        self.translations_dir = translations_dir
        self.current_language = 'en'  # Default to English
        self.translations = {}
        self.available_languages = {}
        
        self._load_available_languages()
        self._load_translations()
    
    def _load_available_languages(self):
        """Load the list of available languages."""
        self.available_languages = {
            'en': 'English',
            'es': 'Español (Spanish)',
            'fr': 'Français (French)', 
            'de': 'Deutsch (German)',
            'it': 'Italiano (Italian)',
            'pt': 'Português (Portuguese)',
            'ru': 'Русский (Russian)',
            'zh': '中文 (Chinese)',
            'ja': '日本語 (Japanese)',
            'ko': '한국어 (Korean)',
            'ar': 'العربية (Arabic)',
            'hi': 'हिन्दी (Hindi)',
            'nl': 'Nederlands (Dutch)',
            'sv': 'Svenska (Swedish)',
            'no': 'Norsk (Norwegian)',
            'da': 'Dansk (Danish)',
            'fi': 'Suomi (Finnish)',
            'pl': 'Polski (Polish)',
            'tr': 'Türkçe (Turkish)',
            'el': 'Ελληνικά (Greek)'
        }
    
    def _load_translations(self):
        """Load translation files for all available languages."""
        self.translations = {}
        
        # Load each language file if it exists
        for lang_code in self.available_languages.keys():
            translation_file = os.path.join(self.translations_dir, f'{lang_code}.json')
            if os.path.exists(translation_file):
                try:
                    with open(translation_file, 'r', encoding='utf-8') as f:
                        self.translations[lang_code] = json.load(f)
                except Exception as e:
                    print(f"Warning: Could not load translations for {lang_code}: {e}")
        
        # If no translations loaded, create default English
        if not self.translations:
            self.translations['en'] = self._get_default_english_translations()
    
    def _get_default_english_translations(self) -> Dict[str, str]:
        """Get default English translations (fallback)."""
        return {
            # Application
            'app_title': 'CoreLedger Bank System',
            'app_welcome': 'Welcome to CoreLedger Bank System',
            'app_goodbye': 'Thank you for using CoreLedger Bank System!',
            'app_exit': 'Exit',
            'app_cancel': 'Cancel',
            'app_confirm': 'Confirm',
            'app_yes': 'Yes',
            'app_no': 'No',
            'app_success': 'Success',
            'app_error': 'Error',
            'app_warning': 'Warning',
            
            # Language Selection
            'lang_select_title': 'Language Selection',
            'lang_select_prompt': 'Please select your preferred language:',
            'lang_select_help': '(Press Enter for auto-detect, or enter language number)',
            'lang_choice_prompt': 'Language choice',
            'lang_select_invalid': 'Invalid selection. Please choose a valid language number.',
            'lang_selected': 'Language set to: {language}',
            'lang_auto_detected': 'Auto-detected language: {language}',
            'lang_fallback': 'Falling back to English',
            
            # Main Menu
            'menu_title': 'MAIN MENU',
            'menu_create_account': 'Create New Account',
            'menu_deposit': 'Make Deposit',
            'menu_withdraw': 'Make Withdrawal',
            'menu_transfer': 'Transfer Money',
            'menu_view_account': 'View Account Details',
            'menu_view_all': 'View All Accounts',
            'menu_history': 'View Transaction History',
            'menu_delete': 'Delete Account',
            'menu_exit': 'Exit',
            'menu_select': 'Select an option (1-9):',
            'menu_invalid': 'Invalid choice. Please select 1-9.',
            
            # Account Creation
            'create_title': 'CREATE NEW ACCOUNT',
            'create_name_prompt': 'Enter account holder name:',
            'create_balance_prompt': 'Enter initial balance (or press Enter for $0.00):',
            'create_success': 'Account created successfully!',
            'create_account_id': 'Account ID: {id}',
            'create_account_name': 'Name: {name}',
            'create_initial_balance': 'Initial Balance: ${balance}',
            'create_name_empty': 'Account name cannot be empty.',
            'create_duplicate': 'Account with name \'{name}\' already exists',
            
            # Deposits
            'deposit_title': 'MAKE DEPOSIT',
            'deposit_amount_prompt': 'Enter deposit amount: $',
            'deposit_description_prompt': 'Enter description (optional):',
            'deposit_success': 'Deposit successful!',
            'deposit_amount': 'Amount: ${amount}',
            'deposit_new_balance': 'New Balance: ${balance}',
            'deposit_invalid_amount': 'Invalid amount. Deposit must be positive.',
            
            # Withdrawals
            'withdraw_title': 'MAKE WITHDRAWAL',
            'withdraw_current_balance': 'Current Balance: ${balance}',
            'withdraw_amount_prompt': 'Enter withdrawal amount: $',
            'withdraw_description_prompt': 'Enter description (optional):',
            'withdraw_success': 'Withdrawal successful!',
            'withdraw_amount': 'Amount: ${amount}',
            'withdraw_new_balance': 'New Balance: ${balance}',
            'withdraw_invalid_amount': 'Invalid amount. Withdrawal must be positive.',
            'withdraw_insufficient': 'Insufficient funds. Available: ${available}',
            
            # Transfers
            'transfer_title': 'TRANSFER MONEY',
            'transfer_from': 'Select FROM account:',
            'transfer_to': 'Select TO account:',
            'transfer_details': 'Transfer Details:',
            'transfer_from_account': 'From: {name} (${balance})',
            'transfer_to_account': 'To: {name} (${balance})',
            'transfer_amount_prompt': 'Enter transfer amount: $',
            'transfer_description_prompt': 'Enter description (optional):',
            'transfer_summary': 'Transfer Summary:',
            'transfer_confirm': 'Proceed with transfer?',
            'transfer_success': 'Transfer successful!',
            'transfer_cancelled': 'Transfer cancelled.',
            'transfer_same_account': 'Cannot transfer to the same account',
            'transfer_insufficient': 'Insufficient funds. Available: ${available}',
            
            # Account Details
            'details_title': 'ACCOUNT DETAILS',
            'details_info': 'Account Information:',
            'details_id': 'ID: {id}',
            'details_name': 'Name: {name}',
            'details_balance': 'Balance: ${balance}',
            'details_created': 'Created: {date}',
            'details_transactions': 'Recent Transactions (last 5):',
            'details_no_transactions': 'No transactions found.',
            
            # All Accounts
            'all_accounts_title': 'ALL ACCOUNTS',
            'all_accounts_empty': 'No accounts found. Create an account first.',
            'all_accounts_total': 'Total:',
            'all_accounts_count': 'Number of accounts: {count}',
            
            # Transaction History
            'history_title': 'TRANSACTION HISTORY',
            'history_for': 'Transaction History for {name}:',
            'history_empty': 'No transactions found for {name}.',
            'history_total': 'Total transactions: {count}',
            
            # Account Deletion
            'delete_title': 'DELETE ACCOUNT',
            'delete_warning': 'WARNING: This action cannot be undone!',
            'delete_nonzero': 'Cannot delete account with non-zero balance (${balance}).',
            'delete_withdraw_first': 'Please withdraw all funds first.',
            'delete_details': 'Account to delete:',
            'delete_confirm': 'Are you sure you want to delete {name}\'s account?',
            'delete_success': 'Account \'{name}\' deleted successfully.',
            'delete_failed': 'Failed to delete account.',
            'delete_cancelled': 'Account deletion cancelled.',
            
            # Account Selection
            'select_available': 'Available accounts:',
            'select_prompt': 'Select account (1-{count}) or \'c\' to cancel:',
            'select_no_accounts': 'No accounts available.',
            'select_invalid': 'Invalid choice. Please select 1-{count} or \'c\'.',
            'select_invalid_input': 'Invalid input. Please enter a number or \'c\'.',
            
            # Input/Validation
            'input_invalid_amount': 'Invalid amount. Please enter a valid number.',
            'input_negative_amount': 'Amount cannot be negative.',
            'input_empty_amount': 'Amount cannot be empty.',
            'input_cancelled': 'Operation cancelled.',
            'input_confirm_prompt': '{message} (y/n):',
            'input_confirm_invalid': 'Please enter \'y\' for yes or \'n\' for no.',
            
            # Transaction Types
            'txn_deposit_plus': 'DEPOSIT +',
            'txn_withdraw_minus': 'WITHDRAW -',
            'txn_sent_minus': 'SENT -',
            'txn_received_plus': 'RECEIVED +',
            
            # Session Summary
            'summary_title': 'Session Summary:',
            'summary_accounts': 'Total Accounts: {count}',
            'summary_balance': 'Total Balance: {balance}',
            'summary_database': 'Database: {path}',
            'summary_saved': 'All data has been automatically saved.',
            
            # Status Messages
            'status_loading': 'Loading...',
            'status_saving': 'Saving...',
            'status_processing': 'Processing...',
            
            # Error Messages
            'error_unexpected': 'An unexpected error occurred: {error}',
            'error_account_not_found': 'Account with ID {id} not found',
            'error_database': 'Database error: {error}',
            'error_file': 'File error: {error}',
            
            # Currency
            'currency_symbol': '$',
            'currency_format': '${amount}',
        }
    
    def set_language(self, language_code: str) -> bool:
        """Set the current language."""
        if language_code in self.available_languages:
            self.current_language = language_code
            return True
        return False
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get dictionary of available language codes and names."""
        return self.available_languages.copy()
    
    def detect_system_language(self) -> str:
        """Detect system language and return appropriate language code."""
        try:
            # Try to get system locale
            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                # Extract language code (first 2 characters)
                lang_code = system_locale.lower()[:2]
                if lang_code in self.available_languages:
                    return lang_code
        except:
            pass
        
        # Fallback to English
        return 'en'
    
    def get_text(self, key: str, **kwargs) -> str:
        """Get translated text for the given key."""
        # Get translation for current language
        if self.current_language in self.translations:
            translation = self.translations[self.current_language].get(key)
        else:
            translation = None
        
        # Fallback to English if translation not found
        if translation is None and self.current_language != 'en':
            translation = self.translations.get('en', {}).get(key)
        
        # Final fallback to key itself
        if translation is None:
            translation = key
        
        # Format with provided parameters
        try:
            return translation.format(**kwargs)
        except (KeyError, ValueError):
            return translation
    
    def get_language_name(self, lang_code: str = None) -> str:
        """Get the display name for a language code."""
        if lang_code is None:
            lang_code = self.current_language
        return self.available_languages.get(lang_code, lang_code)
    
    def select_language_interactive(self) -> str:
        """Interactive language selection for CLI."""
        # Initialize with English for the selection interface
        self.set_language('en')
        
        print("\n" + "=" * 50)
        print("🌍 " + self.get_text('lang_select_title'))
        print("=" * 50)
        
        # Show available languages
        languages = list(self.available_languages.items())
        for i, (code, name) in enumerate(languages, 1):
            print(f"{i:2}. {name}")
        
        # Auto-detect system language
        detected = self.detect_system_language()
        if detected != 'en':
            print(f"\n💡 {self.get_text('lang_auto_detected', language=self.available_languages[detected])}")
        
        print(f"\n➤ {self.get_text('lang_select_prompt')}")
        print("   (Press Enter for auto-detect, or enter language number)")
        
        while True:
            try:
                choice = input("Language choice: ").strip()
                
                # Empty choice = auto-detect
                if not choice:
                    selected_lang = detected
                    break
                
                # Numeric choice
                try:
                    index = int(choice) - 1
                    if 0 <= index < len(languages):
                        selected_lang = languages[index][0]
                        break
                    else:
                        print(f"❌ {self.get_text('lang_select_invalid')}")
                        continue
                except ValueError:
                    print(f"❌ {self.get_text('lang_select_invalid')}")
                    continue
                    
            except KeyboardInterrupt:
                # Default to English on cancel
                selected_lang = 'en'
                break
        
        # Set the selected language
        self.set_language(selected_lang)
        print(f"✅ {self.get_text('lang_selected', language=self.get_language_name(selected_lang))}")
        
        return selected_lang


# Global language manager instance
_language_manager = None


def get_language_manager() -> LanguageManager:
    """Get the global language manager instance."""
    global _language_manager
    if _language_manager is None:
        _language_manager = LanguageManager()
    return _language_manager


def _(key: str, **kwargs) -> str:
    """Shorthand function for getting translated text."""
    return get_language_manager().get_text(key, **kwargs)


def set_language(language_code: str) -> bool:
    """Set the global language."""
    return get_language_manager().set_language(language_code)


def get_current_language() -> str:
    """Get current language code."""
    return get_language_manager().current_language


def select_language_interactive() -> str:
    """Interactive language selection."""
    return get_language_manager().select_language_interactive()