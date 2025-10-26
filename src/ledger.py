"""Main ledger system for CoreLedger."""

from decimal import Decimal
from typing import Optional, List, Tuple

from .models.database import DatabaseManager
from .models.account import Account, AccountRepository, InsufficientFundsError, InvalidAmountError
from .models.transaction import Transaction, TransactionRepository


class LedgerError(Exception):
    """Base exception for ledger operations."""
    pass


class AccountNotFoundError(LedgerError):
    """Raised when an account is not found."""
    pass


class BankLedger:
    """
    Main bank ledger system that manages accounts and transactions.
    
    This class provides a high-level interface for banking operations
    including account management, deposits, withdrawals, and transfers.
    All operations are atomic and maintain data consistency.
    """
    
    def __init__(self, db_path: str = "bank_ledger.db"):
        """
        Initialize the bank ledger with a database.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_manager = DatabaseManager(db_path)
        self.account_repo = AccountRepository(self.db_manager)
        self.transaction_repo = TransactionRepository(self.db_manager)
    
    def create_account(self, name: str, initial_balance: str | Decimal = "0.00") -> int:
        """
        Create a new bank account.
        
        Args:
            name: Account holder's name
            initial_balance: Starting balance as string or Decimal
            
        Returns:
            ID of the created account
            
        Raises:
            ValueError: If name is invalid or account already exists
            InvalidAmountError: If initial balance is negative
        """
        if isinstance(initial_balance, str):
            initial_balance = Decimal(initial_balance)
        
        account_id = self.account_repo.create_account(name, initial_balance)
        
        # Record initial deposit transaction if balance > 0
        if initial_balance > 0:
            transaction = Transaction(
                id=None,
                from_account_id=None,
                to_account_id=account_id,
                amount=initial_balance,
                transaction_type="deposit",
                description=f"Initial deposit for account '{name}'"
            )
            self.transaction_repo.create_transaction(transaction)
        
        return account_id
    
    def get_account(self, account_id: int) -> Account:
        """
        Get account by ID.
        
        Args:
            account_id: ID of the account
            
        Returns:
            Account object
            
        Raises:
            AccountNotFoundError: If account doesn't exist
        """
        account = self.account_repo.get_account_by_id(account_id)
        if not account:
            raise AccountNotFoundError(f"Account with ID {account_id} not found")
        return account
    
    def get_account_by_name(self, name: str) -> Account:
        """
        Get account by name.
        
        Args:
            name: Name of the account holder
            
        Returns:
            Account object
            
        Raises:
            AccountNotFoundError: If account doesn't exist
        """
        account = self.account_repo.get_account_by_name(name)
        if not account:
            raise AccountNotFoundError(f"Account with name '{name}' not found")
        return account
    
    def get_balance(self, account_id: int) -> Decimal:
        """
        Get current balance of an account.
        
        Args:
            account_id: ID of the account
            
        Returns:
            Current balance as Decimal
            
        Raises:
            AccountNotFoundError: If account doesn't exist
        """
        account = self.get_account(account_id)
        return account.balance
    
    def deposit(self, account_id: int, amount: str | Decimal, description: str = "") -> Decimal:
        """
        Deposit money into an account.
        
        Args:
            account_id: ID of the target account
            amount: Amount to deposit as string or Decimal
            description: Optional transaction description
            
        Returns:
            New balance after deposit
            
        Raises:
            AccountNotFoundError: If account doesn't exist
            InvalidAmountError: If amount is not positive
        """
        if isinstance(amount, str):
            amount = Decimal(amount)
        
        with self.db_manager.transaction():
            account = self.get_account(account_id)
            new_balance = account.deposit(amount)
            
            # Update database
            self.account_repo.update_balance(account_id, new_balance)
            
            # Record transaction
            transaction = Transaction(
                id=None,
                from_account_id=None,
                to_account_id=account_id,
                amount=amount,
                transaction_type="deposit",
                description=description or f"Deposit to {account.name}"
            )
            self.transaction_repo.create_transaction(transaction)
            
            return new_balance
    
    def withdraw(self, account_id: int, amount: str | Decimal, description: str = "") -> Decimal:
        """
        Withdraw money from an account.
        
        Args:
            account_id: ID of the source account
            amount: Amount to withdraw as string or Decimal
            description: Optional transaction description
            
        Returns:
            New balance after withdrawal
            
        Raises:
            AccountNotFoundError: If account doesn't exist
            InvalidAmountError: If amount is not positive
            InsufficientFundsError: If amount exceeds available balance
        """
        if isinstance(amount, str):
            amount = Decimal(amount)
        
        with self.db_manager.transaction():
            account = self.get_account(account_id)
            new_balance = account.withdraw(amount)
            
            # Update database
            self.account_repo.update_balance(account_id, new_balance)
            
            # Record transaction
            transaction = Transaction(
                id=None,
                from_account_id=account_id,
                to_account_id=None,
                amount=amount,
                transaction_type="withdrawal",
                description=description or f"Withdrawal from {account.name}"
            )
            self.transaction_repo.create_transaction(transaction)
            
            return new_balance
    
    def transfer(self, from_account_id: int, to_account_id: int, 
                amount: str | Decimal, description: str = "") -> Tuple[Decimal, Decimal]:
        """
        Transfer money between accounts.
        
        Args:
            from_account_id: ID of the source account
            to_account_id: ID of the target account
            amount: Amount to transfer as string or Decimal
            description: Optional transaction description
            
        Returns:
            Tuple of (source_balance, target_balance) after transfer
            
        Raises:
            AccountNotFoundError: If either account doesn't exist
            InvalidAmountError: If amount is not positive
            InsufficientFundsError: If amount exceeds source account balance
            ValueError: If trying to transfer to the same account
        """
        if isinstance(amount, str):
            amount = Decimal(amount)
        
        if from_account_id == to_account_id:
            raise ValueError("Cannot transfer to the same account")
        
        with self.db_manager.transaction():
            from_account = self.get_account(from_account_id)
            to_account = self.get_account(to_account_id)
            
            # Perform the transfer operations
            from_balance = from_account.withdraw(amount)
            to_balance = to_account.deposit(amount)
            
            # Update both accounts in database
            self.account_repo.update_balance(from_account_id, from_balance)
            self.account_repo.update_balance(to_account_id, to_balance)
            
            # Record transaction
            transaction = Transaction(
                id=None,
                from_account_id=from_account_id,
                to_account_id=to_account_id,
                amount=amount,
                transaction_type="transfer",
                description=description or f"Transfer from {from_account.name} to {to_account.name}"
            )
            self.transaction_repo.create_transaction(transaction)
            
            return from_balance, to_balance
    
    def get_account_transactions(self, account_id: int) -> List[Transaction]:
        """
        Get all transactions for an account.
        
        Args:
            account_id: ID of the account
            
        Returns:
            List of transactions involving the account
            
        Raises:
            AccountNotFoundError: If account doesn't exist
        """
        # Verify account exists
        self.get_account(account_id)
        return self.transaction_repo.get_account_transactions(account_id)
    
    def list_accounts(self) -> List[Account]:
        """
        List all accounts in the system.
        
        Returns:
            List of all accounts
        """
        return self.account_repo.get_all_accounts()
    
    def get_total_system_balance(self) -> Decimal:
        """
        Calculate total balance across all accounts.
        
        Returns:
            Sum of all account balances
        """
        accounts = self.list_accounts()
        return sum(account.balance for account in accounts)
    
    def delete_account(self, account_id: int) -> bool:
        """
        Delete an account (only if balance is zero).
        
        Args:
            account_id: ID of the account to delete
            
        Returns:
            True if account was deleted
            
        Raises:
            AccountNotFoundError: If account doesn't exist
            ValueError: If account has non-zero balance
        """
        # Verify account exists
        self.get_account(account_id)
        return self.account_repo.delete_account(account_id)
    
    def close(self):
        """Close database connections."""
        self.db_manager.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close database."""
        self.close()