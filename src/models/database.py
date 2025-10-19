"""Database management for CoreLedger."""

import sqlite3
import threading
from contextlib import contextmanager
from decimal import Decimal
from typing import Optional


class DatabaseManager:
    """Manages SQLite database connections and operations."""
    
    def __init__(self, db_path: str):
        """Initialize database manager with given database path."""
        self.db_path = db_path
        self._local = threading.local()
        self._init_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(
                self.db_path, 
                check_same_thread=False
            )
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    
    def _init_database(self):
        """Initialize database tables."""
        with self.transaction() as conn:
            # Create accounts table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    balance TEXT NOT NULL DEFAULT '0.00',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create transactions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_account_id INTEGER,
                    to_account_id INTEGER,
                    amount TEXT NOT NULL,
                    transaction_type TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (from_account_id) REFERENCES accounts (id),
                    FOREIGN KEY (to_account_id) REFERENCES accounts (id)
                )
            """)
            
            # Create indexes for better performance
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_transactions_from_account 
                ON transactions(from_account_id)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_transactions_to_account 
                ON transactions(to_account_id)
            """)
    
    def execute_query(self, query: str, params: tuple = (), fetch_one: bool = False):
        """Execute a query and return results."""
        with self.transaction() as conn:
            cursor = conn.execute(query, params)
            if fetch_one:
                return cursor.fetchone()
            return cursor.fetchall()
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute an insert query and return the last row ID."""
        with self.transaction() as conn:
            cursor = conn.execute(query, params)
            return cursor.lastrowid
    
    def decimal_to_str(self, value: Decimal) -> str:
        """Convert Decimal to string for storage."""
        return str(value)
    
    def str_to_decimal(self, value: str) -> Decimal:
        """Convert string to Decimal from storage."""
        return Decimal(value)
    
    def close(self):
        """Close database connections."""
        if hasattr(self._local, 'connection'):
            self._local.connection.close()