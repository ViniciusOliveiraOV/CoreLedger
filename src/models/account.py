"""Account model for CoreLedger."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional


class InsufficientFundsError(Exception):
    """Raised when attempting to withdraw more than available balance."""
    pass


class InvalidAmountError(Exception):
    """Raised when an invalid amount is provided for operations."""
    pass


@dataclass
class Account:
    """Represents a bank account."""
    
    id: Optional[int]
    name: str
    balance: Decimal
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate account after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("Account name cannot be empty")
        
        if self.balance < 0:
            raise ValueError("Account balance cannot be negative")
        
        # Ensure balance has proper decimal precision (2 decimal places)
        self.balance = self.balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def deposit(self, amount: Decimal) -> Decimal:
        """
        Deposit money into the account.
        
        Args:
            amount: Amount to deposit
            
        Returns:
            New balance after deposit
            
        Raises:
            InvalidAmountError: If amount is not positive
        """
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        
        if amount <= 0:
            raise InvalidAmountError("Deposit amount must be positive")
        
        # Ensure amount has proper decimal precision
        amount = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        self.balance += amount
        return self.balance
    
    def withdraw(self, amount: Decimal) -> Decimal:
        """
        Withdraw money from the account.
        
        Args:
            amount: Amount to withdraw
            
        Returns:
            New balance after withdrawal
            
        Raises:
            InvalidAmountError: If amount is not positive
            InsufficientFundsError: If amount exceeds available balance
        """
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be positive")
        
        # Ensure amount has proper decimal precision
        amount = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        if amount > self.balance:
            raise InsufficientFundsError(
                f"Insufficient funds. Available: {self.balance}, Requested: {amount}"
            )
        
        self.balance -= amount
        return self.balance
    
    def get_balance(self) -> Decimal:
        """Get current account balance."""
        return self.balance
    
    def __str__(self) -> str:
        """String representation of the account."""
        return f"Account(id={self.id}, name='{self.name}', balance={self.balance})"


class AccountRepository:
    """Repository for managing accounts in the database."""
    
    def __init__(self, db_manager):
        """Initialize with database manager."""
        self.db = db_manager
    
    def create_account(self, name: str, initial_balance: Decimal = Decimal('0.00')) -> int:
        """
        
        Create a new account and return its ID.
        
        Args:
            name: Account holder's name
            initial_balance: Starting balance (default: 0.00)
            
        Returns:
            ID of the created account
            
        Raises:
            ValueError: If name is empty or initial_balance is negative
        """
        # Create account object for validation
        account = Account(id=None, name=name, balance=initial_balance)
        
        query = """
            INSERT INTO accounts (name, balance)
            VALUES (?, ?)
        """
        params = (account.name, self.db.decimal_to_str(account.balance))
        
        try:
            return self.db.execute_insert(query, params)
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError(f"Account with name '{name}' already exists")
            raise
    
    def get_account_by_id(self, account_id: int) -> Optional[Account]:
        """Get an account by its ID."""
        query = """
            SELECT id, name, balance, created_at
            FROM accounts
            WHERE id = ?
        """
        row = self.db.execute_query(query, (account_id,), fetch_one=True)
        if row:
            return self._row_to_account(row)
        return None
    
    def get_account_by_name(self, name: str) -> Optional[Account]:
        """Get an account by name."""
        query = """
            SELECT id, name, balance, created_at
            FROM accounts
            WHERE name = ?
        """
        row = self.db.execute_query(query, (name,), fetch_one=True)
        if row:
            return self._row_to_account(row)
        return None
    
    def update_balance(self, account_id: int, new_balance: Decimal):
        """Update an account's balance."""
        if new_balance < 0:
            raise ValueError("Account balance cannot be negative")
        
        # Ensure proper decimal precision
        new_balance = new_balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        query = """
            UPDATE accounts
            SET balance = ?
            WHERE id = ?
        """
        params = (self.db.decimal_to_str(new_balance), account_id)
        self.db.execute_query(query, params)
    
    def get_all_accounts(self) -> list[Account]:
        """Get all accounts."""
        query = """
            SELECT id, name, balance, created_at
            FROM accounts
            ORDER BY name
        """
        rows = self.db.execute_query(query)
        return [self._row_to_account(row) for row in rows]
    
    def delete_account(self, account_id: int) -> bool:
        """
        Delete an account if it has zero balance.
        
        Args:
            account_id: ID of the account to delete
            
        Returns:
            True if account was deleted, False otherwise
            
        Raises:
            ValueError: If account has non-zero balance
        """
        account = self.get_account_by_id(account_id)
        if not account:
            return False
        
        if account.balance != 0:
            raise ValueError("Cannot delete account with non-zero balance")
        
        query = "DELETE FROM accounts WHERE id = ?"
        self.db.execute_query(query, (account_id,))
        return True
    
    def _row_to_account(self, row) -> Account:
        """Convert database row to Account object."""
        return Account(
            id=row['id'],
            name=row['name'],
            balance=self.db.str_to_decimal(row['balance']),
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )