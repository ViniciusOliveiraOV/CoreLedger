"""Transaction model for CoreLedger."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class Transaction:
    """Represents a transaction in the ledger."""
    
    id: Optional[int]
    from_account_id: Optional[int]
    to_account_id: Optional[int]
    amount: Decimal
    transaction_type: str
    description: str
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate transaction after initialization."""
        if self.amount <= 0:
            raise ValueError("Transaction amount must be positive")
        
        valid_types = ['deposit', 'withdrawal', 'transfer']
        if self.transaction_type not in valid_types:
            raise ValueError(f"Invalid transaction type: {self.transaction_type}")
        
        # Validate account IDs based on transaction type
        if self.transaction_type == 'deposit':
            if self.from_account_id is not None:
                raise ValueError("Deposit should not have from_account_id")
            if self.to_account_id is None:
                raise ValueError("Deposit must have to_account_id")
        
        elif self.transaction_type == 'withdrawal':
            if self.from_account_id is None:
                raise ValueError("Withdrawal must have from_account_id")
            if self.to_account_id is not None:
                raise ValueError("Withdrawal should not have to_account_id")
        
        elif self.transaction_type == 'transfer':
            if self.from_account_id is None or self.to_account_id is None:
                raise ValueError("Transfer must have both from_account_id and to_account_id")
            if self.from_account_id == self.to_account_id:
                raise ValueError("Cannot transfer to the same account")


class TransactionRepository:
    """Repository for managing transactions in the database."""
    
    def __init__(self, db_manager):
        """Initialize with database manager."""
        self.db = db_manager
    
    def create_transaction(self, transaction: Transaction) -> int:
        """Create a new transaction and return its ID."""
        query = """
            INSERT INTO transactions 
            (from_account_id, to_account_id, amount, transaction_type, description)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (
            transaction.from_account_id,
            transaction.to_account_id,
            self.db.decimal_to_str(transaction.amount),
            transaction.transaction_type,
            transaction.description
        )
        return self.db.execute_insert(query, params)
    
    def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Get a transaction by its ID."""
        query = """
            SELECT id, from_account_id, to_account_id, amount, 
                   transaction_type, description, created_at
            FROM transactions
            WHERE id = ?
        """
        row = self.db.execute_query(query, (transaction_id,), fetch_one=True)
        if row:
            return self._row_to_transaction(row)
        return None
    
    def get_account_transactions(self, account_id: int) -> list[Transaction]:
        """Get all transactions for a specific account."""
        query = """
            SELECT id, from_account_id, to_account_id, amount, 
                   transaction_type, description, created_at
            FROM transactions
            WHERE from_account_id = ? OR to_account_id = ?
            ORDER BY created_at DESC
        """
        rows = self.db.execute_query(query, (account_id, account_id))
        return [self._row_to_transaction(row) for row in rows]
    
    def _row_to_transaction(self, row) -> Transaction:
        """Convert database row to Transaction object."""
        return Transaction(
            id=row['id'],
            from_account_id=row['from_account_id'],
            to_account_id=row['to_account_id'],
            amount=self.db.str_to_decimal(row['amount']),
            transaction_type=row['transaction_type'],
            description=row['description'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )