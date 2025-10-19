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
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables and protection triggers."""
        cursor = self.connection.cursor()
        
        # Create accounts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                balance TEXT NOT NULL DEFAULT '0.00',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_account_id TEXT,
                to_account_id TEXT,
                amount TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (from_account_id) REFERENCES accounts (id),
                FOREIGN KEY (to_account_id) REFERENCES accounts (id)
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_from_account 
            ON transactions(from_account_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_to_account 
            ON transactions(to_account_id)
        """)
        
        self.connection.commit()
        
        # Initialize protection triggers
        self._init_protection_triggers()
    
    def _init_protection_triggers(self):
        """Initialize database protection triggers."""
        triggers_manager = DatabaseTriggersManager(self.connection)
        triggers_manager.create_all_protection_triggers()
    
    def execute_query(self, query: str, params: tuple = (), fetch_one: bool = False):
        """Execute a query and return results."""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        if fetch_one:
            return cursor.fetchone()
        return cursor.fetchall()
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute an insert query and return the last row ID."""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor.lastrowid
    
    def close(self):
        """Close database connection."""
        if hasattr(self, 'connection'):
            self.connection.close()
    
    def str_to_decimal(self, value: str) -> Decimal:
        """Convert string to Decimal for precise calculations."""
        return Decimal(value)
    
    def decimal_to_str(self, value: Decimal) -> str:
        """Convert Decimal to string for database storage."""
        return str(value)


class DatabaseTriggersManager:
    """
    Manages database triggers for business rule enforcement.
    
    This class provides methods to create, manage, and test database triggers
    that enforce business rules at the database level.
    """
    
    def __init__(self, connection):
        """Initialize the triggers manager with a database connection"""
        self.connection = connection
    
    def create_account_deletion_prevention_trigger(self):
        """
        Create a trigger that prevents deletion of accounts with non-zero balances.
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS prevent_delete_nonzero_balance
            BEFORE DELETE ON accounts
            FOR EACH ROW
            WHEN CAST(OLD.balance AS REAL) != 0.0
            BEGIN
                SELECT RAISE(ABORT, 'Cannot delete account with non-zero balance. Current balance: ' || OLD.balance);
            END;
        """)
        self.connection.commit()
    
    def create_negative_balance_prevention_trigger(self):
        """
        Create a trigger that prevents accounts from having negative balances.
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS prevent_negative_balance
            BEFORE UPDATE OF balance ON accounts
            FOR EACH ROW
            WHEN CAST(NEW.balance AS REAL) < 0.0
            BEGIN
                SELECT RAISE(ABORT, 'Account balance cannot be negative. Attempted balance: ' || NEW.balance);
            END;
        """)
        self.connection.commit()
    
    def create_transaction_consistency_trigger(self):
        """
        Create a trigger that validates transaction amounts are positive.
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS validate_transaction_amount
            BEFORE INSERT ON transactions
            FOR EACH ROW
            WHEN CAST(NEW.amount AS REAL) <= 0.0
            BEGIN
                SELECT RAISE(ABORT, 'Transaction amount must be positive. Attempted amount: ' || NEW.amount);
            END;
        """)
        self.connection.commit()
    
    def create_all_protection_triggers(self):
        """Create all protection triggers for comprehensive data integrity."""
        self.create_account_deletion_prevention_trigger()
        self.create_negative_balance_prevention_trigger()
        self.create_transaction_consistency_trigger()
    
    def list_triggers(self):
        """List all triggers currently in the database."""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT name, sql FROM sqlite_master 
            WHERE type = 'trigger'
            ORDER BY name
        """)
        return [{'name': row[0], 'sql': row[1]} for row in cursor.fetchall()]
    
    def drop_trigger(self, trigger_name: str):
        """Drop a specific trigger from the database."""
        cursor = self.connection.cursor()
        cursor.execute(f"DROP TRIGGER IF EXISTS {trigger_name}")
        self.connection.commit()
    
    def drop_all_protection_triggers(self):
        """Remove all protection triggers from the database"""
        triggers = [
            'prevent_delete_nonzero_balance',
            'prevent_negative_balance', 
            'validate_transaction_amount'
        ]
        
        for trigger in triggers:
            try:
                self.drop_trigger(trigger)
            except Exception:
                pass
    
    def test_triggers(self):
        """Test all protection triggers to ensure they're working correctly."""
        from decimal import Decimal
        
        cursor = self.connection.cursor()
        test_results = {}
        
        # Test 1: Account deletion prevention
        try:
            test_id = "trigger_test_account"
            cursor.execute("INSERT INTO accounts (id, name, balance) VALUES (?, ?, ?)",
                         (test_id, "Test Account", str(Decimal('100.00'))))
            
            try:
                cursor.execute("DELETE FROM accounts WHERE id = ?", (test_id,))
                test_results['deletion_prevention'] = False
            except Exception as e:
                if "Cannot delete account with non-zero balance" in str(e):
                    test_results['deletion_prevention'] = True
                else:
                    test_results['deletion_prevention'] = False
                self.connection.rollback()
            
            # Clean up
            cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", 
                         (str(Decimal('0.00')), test_id))
            cursor.execute("DELETE FROM accounts WHERE id = ?", (test_id,))
            self.connection.commit()
            
        except Exception:
            test_results['deletion_prevention'] = False
            self.connection.rollback()
        
        # Test 2: Negative balance prevention
        try:
            test_id = "trigger_test_account2"
            cursor.execute("INSERT INTO accounts (id, name, balance) VALUES (?, ?, ?)",
                         (test_id, "Test Account 2", str(Decimal('50.00'))))
            
            try:
                cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?",
                             (str(Decimal('-10.00')), test_id))
                test_results['negative_balance_prevention'] = False
            except Exception as e:
                if "Account balance cannot be negative" in str(e):
                    test_results['negative_balance_prevention'] = True
                else:
                    test_results['negative_balance_prevention'] = False
                self.connection.rollback()
            
            # Clean up
            cursor.execute("DELETE FROM accounts WHERE id = ?", (test_id,))
            self.connection.commit()
            
        except Exception:
            test_results['negative_balance_prevention'] = False
            self.connection.rollback()
        
        return test_results