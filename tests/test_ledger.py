"""Tests for BankLedger system."""

import pytest
from decimal import Decimal
from tempfile import NamedTemporaryFile
import os

from src.ledger import BankLedger, AccountNotFoundError, LedgerError
from src.models.account import InsufficientFundsError, InvalidAmountError


class TestBankLedger:
    """Test cases for BankLedger class."""
    
    @pytest.fixture
    def ledger(self):
        """Create a temporary ledger for testing."""
        with NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name
        
        ledger = BankLedger(db_path)
        yield ledger
        
        ledger.close()
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_create_account_valid(self, ledger):
        """Test creating a valid account."""
        account_id = ledger.create_account("John Doe", "100.00")
        assert isinstance(account_id, int)
        assert account_id > 0
        
        account = ledger.get_account(account_id)
        assert account.name == "John Doe"
        assert account.balance == Decimal("100.00")
    
    def test_create_account_zero_balance(self, ledger):
        """Test creating account with zero balance."""
        account_id = ledger.create_account("Jane Doe")
        account = ledger.get_account(account_id)
        assert account.balance == Decimal("0.00")
    
    def test_create_account_with_decimal(self, ledger):
        """Test creating account with Decimal balance."""
        account_id = ledger.create_account("Bob Smith", Decimal("250.75"))
        account = ledger.get_account(account_id)
        assert account.balance == Decimal("250.75")
    
    def test_get_account_nonexistent(self, ledger):
        """Test getting non-existent account raises error."""
        with pytest.raises(AccountNotFoundError, match="Account with ID 999 not found"):
            ledger.get_account(999)
    
    def test_get_account_by_name_existing(self, ledger):
        """Test getting account by name."""
        account_id = ledger.create_account("John Doe", "100.00")
        account = ledger.get_account_by_name("John Doe")
        assert account.id == account_id
        assert account.name == "John Doe"
    
    def test_get_account_by_name_nonexistent(self, ledger):
        """Test getting non-existent account by name raises error."""
        with pytest.raises(AccountNotFoundError, match="Account with name 'Nonexistent' not found"):
            ledger.get_account_by_name("Nonexistent")
    
    def test_get_balance(self, ledger):
        """Test getting account balance."""
        account_id = ledger.create_account("John Doe", "123.45")
        balance = ledger.get_balance(account_id)
        assert balance == Decimal("123.45")
    
    def test_deposit_valid(self, ledger):
        """Test valid deposit operation."""
        account_id = ledger.create_account("John Doe", "100.00")
        new_balance = ledger.deposit(account_id, "50.25")
        
        assert new_balance == Decimal("150.25")
        assert ledger.get_balance(account_id) == Decimal("150.25")
    
    def test_deposit_with_decimal(self, ledger):
        """Test deposit with Decimal amount."""
        account_id = ledger.create_account("John Doe", "100.00")
        new_balance = ledger.deposit(account_id, Decimal("75.50"))
        
        assert new_balance == Decimal("175.50")
    
    def test_deposit_with_description(self, ledger):
        """Test deposit with custom description."""
        account_id = ledger.create_account("John Doe", "100.00")
        ledger.deposit(account_id, "50.00", "Salary deposit")
        
        transactions = ledger.get_account_transactions(account_id)
        # Should have initial deposit + new deposit
        assert len(transactions) == 2
        assert transactions[0].description == "Salary deposit"
    
    def test_deposit_invalid_amount(self, ledger):
        """Test deposit with invalid amount raises error."""
        account_id = ledger.create_account("John Doe", "100.00")
        with pytest.raises(InvalidAmountError, match="Deposit amount must be positive"):
            ledger.deposit(account_id, "0.00")
    
    def test_withdraw_valid(self, ledger):
        """Test valid withdrawal operation."""
        account_id = ledger.create_account("John Doe", "100.00")
        new_balance = ledger.withdraw(account_id, "30.50")
        
        assert new_balance == Decimal("69.50")
        assert ledger.get_balance(account_id) == Decimal("69.50")
    
    def test_withdraw_exact_balance(self, ledger):
        """Test withdrawing exact balance."""
        account_id = ledger.create_account("John Doe", "100.00")
        new_balance = ledger.withdraw(account_id, "100.00")
        
        assert new_balance == Decimal("0.00")
    
    def test_withdraw_insufficient_funds(self, ledger):
        """Test withdrawal with insufficient funds raises error."""
        account_id = ledger.create_account("John Doe", "100.00")
        with pytest.raises(InsufficientFundsError, match="Insufficient funds"):
            ledger.withdraw(account_id, "150.00")
    
    def test_transfer_valid(self, ledger):
        """Test valid transfer between accounts."""
        from_id = ledger.create_account("Alice", "200.00")
        to_id = ledger.create_account("Bob", "100.00")
        
        from_balance, to_balance = ledger.transfer(from_id, to_id, "75.25")
        
        assert from_balance == Decimal("124.75")
        assert to_balance == Decimal("175.25")
        assert ledger.get_balance(from_id) == Decimal("124.75")
        assert ledger.get_balance(to_id) == Decimal("175.25")
    
    def test_transfer_same_account(self, ledger):
        """Test transfer to same account raises error."""
        account_id = ledger.create_account("John Doe", "100.00")
        with pytest.raises(ValueError, match="Cannot transfer to the same account"):
            ledger.transfer(account_id, account_id, "50.00")
    
    def test_transfer_insufficient_funds(self, ledger):
        """Test transfer with insufficient funds raises error."""
        from_id = ledger.create_account("Alice", "50.00")
        to_id = ledger.create_account("Bob", "100.00")
        
        with pytest.raises(InsufficientFundsError, match="Insufficient funds"):
            ledger.transfer(from_id, to_id, "75.00")
    
    def test_transfer_nonexistent_accounts(self, ledger):
        """Test transfer with non-existent accounts raises error."""
        account_id = ledger.create_account("Alice", "100.00")
        
        with pytest.raises(AccountNotFoundError):
            ledger.transfer(account_id, 999, "50.00")
        
        with pytest.raises(AccountNotFoundError):
            ledger.transfer(999, account_id, "50.00")
    
    def test_get_account_transactions(self, ledger):
        """Test getting account transaction history."""
        from_id = ledger.create_account("Alice", "200.00")
        to_id = ledger.create_account("Bob", "100.00")
        
        ledger.deposit(from_id, "50.00", "Bonus")
        ledger.withdraw(from_id, "25.00", "ATM withdrawal")
        ledger.transfer(from_id, to_id, "75.00", "Payment to Bob")
        
        transactions = ledger.get_account_transactions(from_id)
        
        # Should have: initial deposit, bonus deposit, withdrawal, transfer
        assert len(transactions) == 4
        
        # Check transaction types (newest first)
        assert transactions[0].transaction_type == "transfer"
        assert transactions[1].transaction_type == "withdrawal"
        assert transactions[2].transaction_type == "deposit"
        assert transactions[3].transaction_type == "deposit"  # Initial deposit
    
    def test_list_accounts_empty(self, ledger):
        """Test listing accounts when none exist."""
        accounts = ledger.list_accounts()
        assert accounts == []
    
    def test_list_accounts_multiple(self, ledger):
        """Test listing multiple accounts."""
        ledger.create_account("Charlie", "300.00")
        ledger.create_account("Alice", "100.00")
        ledger.create_account("Bob", "200.00")
        
        accounts = ledger.list_accounts()
        assert len(accounts) == 3
        
        # Should be ordered by name
        names = [account.name for account in accounts]
        assert names == ["Alice", "Bob", "Charlie"]
    
    def test_get_total_system_balance(self, ledger):
        """Test calculating total system balance."""
        ledger.create_account("Alice", "100.50")
        ledger.create_account("Bob", "200.25")
        ledger.create_account("Charlie", "300.75")
        
        total = ledger.get_total_system_balance()
        assert total == Decimal("601.50")
    
    def test_get_total_system_balance_after_operations(self, ledger):
        """Test total balance remains consistent after operations."""
        alice_id = ledger.create_account("Alice", "200.00")
        bob_id = ledger.create_account("Bob", "100.00")
        
        initial_total = ledger.get_total_system_balance()
        assert initial_total == Decimal("300.00")
        
        # Transfer doesn't change total
        ledger.transfer(alice_id, bob_id, "50.00")
        assert ledger.get_total_system_balance() == Decimal("300.00")
        
        # Deposit increases total
        ledger.deposit(alice_id, "25.00")
        assert ledger.get_total_system_balance() == Decimal("325.00")
        
        # Withdrawal decreases total
        ledger.withdraw(bob_id, "10.00")
        assert ledger.get_total_system_balance() == Decimal("315.00")
    
    def test_delete_account_zero_balance(self, ledger):
        """Test deleting account with zero balance."""
        account_id = ledger.create_account("John Doe", "0.00")
        result = ledger.delete_account(account_id)
        assert result is True
        
        with pytest.raises(AccountNotFoundError):
            ledger.get_account(account_id)
    
    def test_delete_account_nonzero_balance(self, ledger):
        """Test deleting account with non-zero balance raises error."""
        account_id = ledger.create_account("John Doe", "100.00")
        with pytest.raises(ValueError, match="Cannot delete account with non-zero balance"):
            ledger.delete_account(account_id)
    
    def test_context_manager(self):
        """Test using ledger as context manager."""
        with NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            with BankLedger(db_path) as ledger:
                account_id = ledger.create_account("Test User", "100.00")
                balance = ledger.get_balance(account_id)
                assert balance == Decimal("100.00")
            
            # Verify we can create a new instance with same database
            with BankLedger(db_path) as ledger2:
                account = ledger2.get_account(account_id)
                assert account.name == "Test User"
                assert account.balance == Decimal("100.00")
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)