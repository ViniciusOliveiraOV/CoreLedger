"""Tests for Account model and AccountRepository."""

import pytest
from decimal import Decimal
from tempfile import NamedTemporaryFile
import os

from src.models.database import DatabaseManager
from src.models.account import Account, AccountRepository, InsufficientFundsError, InvalidAmountError


class TestAccount:
    """Test cases for Account class."""
    
    def test_account_creation_valid(self):
        """Test creating a valid account."""
        account = Account(id=1, name="John Doe", balance=Decimal("100.00"))
        assert account.id == 1
        assert account.name == "John Doe"
        assert account.balance == Decimal("100.00")
    
    def test_account_creation_zero_balance(self):
        """Test creating account with zero balance."""
        account = Account(id=1, name="Jane Doe", balance=Decimal("0.00"))
        assert account.balance == Decimal("0.00")
    
    def test_account_creation_empty_name(self):
        """Test creating account with empty name raises error."""
        with pytest.raises(ValueError, match="Account name cannot be empty"):
            Account(id=1, name="", balance=Decimal("100.00"))
    
    def test_account_creation_negative_balance(self):
        """Test creating account with negative balance raises error."""
        with pytest.raises(ValueError, match="Account balance cannot be negative"):
            Account(id=1, name="John Doe", balance=Decimal("-10.00"))
    
    def test_account_balance_precision(self):
        """Test that balance is properly rounded to 2 decimal places."""
        account = Account(id=1, name="John Doe", balance=Decimal("100.999"))
        assert account.balance == Decimal("101.00")
        
        account = Account(id=1, name="John Doe", balance=Decimal("100.994"))
        assert account.balance == Decimal("100.99")
    
    def test_deposit_valid_amount(self):
        """Test depositing a valid amount."""
        account = Account(id=1, name="John Doe", balance=Decimal("100.00"))
        new_balance = account.deposit(Decimal("50.25"))
        assert new_balance == Decimal("150.25")
        assert account.balance == Decimal("150.25")
    
    def test_deposit_string_amount(self):
        """Test depositing with string amount."""
        account = Account(id=1, name="John Doe", balance=Decimal("100.00"))
        new_balance = account.deposit("50.25")
        assert new_balance == Decimal("150.25")
    
    def test_deposit_zero_amount(self):
        """Test depositing zero amount raises error."""
        account = Account(id=1, name="John Doe", balance=Decimal("100.00"))
        with pytest.raises(InvalidAmountError, match="Deposit amount must be positive"):
            account.deposit(Decimal("0.00"))
    
    def test_deposit_negative_amount(self):
        """Test depositing negative amount raises error."""
        account = Account(id=1, name="John Doe", balance=Decimal("100.00"))
        with pytest.raises(InvalidAmountError, match="Deposit amount must be positive"):
            account.deposit(Decimal("-10.00"))
    
    def test_withdraw_valid_amount(self):
        """Test withdrawing a valid amount."""
        account = Account(id=1, name="John Doe", balance=Decimal("100.00"))
        new_balance = account.withdraw(Decimal("30.50"))
        assert new_balance == Decimal("69.50")
        assert account.balance == Decimal("69.50")
    
    def test_withdraw_exact_balance(self):
        """Test withdrawing exact balance."""
        account = Account(id=1, name="John Doe", balance=Decimal("100.00"))
        new_balance = account.withdraw(Decimal("100.00"))
        assert new_balance == Decimal("0.00")
        assert account.balance == Decimal("0.00")
    
    def test_withdraw_insufficient_funds(self):
        """Test withdrawing more than balance raises error."""
        account = Account(id=1, name="John Doe", balance=Decimal("100.00"))
        with pytest.raises(InsufficientFundsError, match="Insufficient funds"):
            account.withdraw(Decimal("150.00"))
    
    def test_withdraw_zero_amount(self):
        """Test withdrawing zero amount raises error."""
        account = Account(id=1, name="John Doe", balance=Decimal("100.00"))
        with pytest.raises(InvalidAmountError, match="Withdrawal amount must be positive"):
            account.withdraw(Decimal("0.00"))
    
    def test_withdraw_negative_amount(self):
        """Test withdrawing negative amount raises error."""
        account = Account(id=1, name="John Doe", balance=Decimal("100.00"))
        with pytest.raises(InvalidAmountError, match="Withdrawal amount must be positive"):
            account.withdraw(Decimal("-10.00"))
    
    def test_get_balance(self):
        """Test getting account balance."""
        account = Account(id=1, name="John Doe", balance=Decimal("123.45"))
        assert account.get_balance() == Decimal("123.45")
    
    def test_account_string_representation(self):
        """Test string representation of account."""
        account = Account(id=1, name="John Doe", balance=Decimal("100.00"))
        expected = "Account(id=1, name='John Doe', balance=100.00)"
        assert str(account) == expected


class TestAccountRepository:
    """Test cases for AccountRepository class."""
    
    @pytest.fixture
    def db_manager(self):
        """Create a temporary database for testing."""
        with NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name
        
        db = DatabaseManager(db_path)
        yield db
        
        db.close()
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def account_repo(self, db_manager):
        """Create AccountRepository with test database."""
        return AccountRepository(db_manager)
    
    def test_create_account_valid(self, account_repo):
        """Test creating a valid account."""
        account_id = account_repo.create_account("John Doe", Decimal("100.00"))
        assert isinstance(account_id, int)
        assert account_id > 0
    
    def test_create_account_zero_balance(self, account_repo):
        """Test creating account with zero balance."""
        account_id = account_repo.create_account("Jane Doe")
        account = account_repo.get_account_by_id(account_id)
        assert account.balance == Decimal("0.00")
    
    def test_create_account_duplicate_name(self, account_repo):
        """Test creating account with duplicate name raises error."""
        account_repo.create_account("John Doe", Decimal("100.00"))
        with pytest.raises(ValueError, match="Account with name 'John Doe' already exists"):
            account_repo.create_account("John Doe", Decimal("200.00"))
    
    def test_get_account_by_id_existing(self, account_repo):
        """Test getting existing account by ID."""
        account_id = account_repo.create_account("John Doe", Decimal("100.00"))
        account = account_repo.get_account_by_id(account_id)
        
        assert account is not None
        assert account.id == account_id
        assert account.name == "John Doe"
        assert account.balance == Decimal("100.00")
    
    def test_get_account_by_id_nonexistent(self, account_repo):
        """Test getting non-existent account by ID returns None."""
        account = account_repo.get_account_by_id(999)
        assert account is None
    
    def test_get_account_by_name_existing(self, account_repo):
        """Test getting existing account by name."""
        account_id = account_repo.create_account("John Doe", Decimal("100.00"))
        account = account_repo.get_account_by_name("John Doe")
        
        assert account is not None
        assert account.id == account_id
        assert account.name == "John Doe"
        assert account.balance == Decimal("100.00")
    
    def test_get_account_by_name_nonexistent(self, account_repo):
        """Test getting non-existent account by name returns None."""
        account = account_repo.get_account_by_name("Nonexistent User")
        assert account is None
    
    def test_update_balance_valid(self, account_repo):
        """Test updating account balance."""
        account_id = account_repo.create_account("John Doe", Decimal("100.00"))
        account_repo.update_balance(account_id, Decimal("250.75"))
        
        updated_account = account_repo.get_account_by_id(account_id)
        assert updated_account.balance == Decimal("250.75")
    
    def test_update_balance_negative(self, account_repo):
        """Test updating balance to negative value raises error."""
        account_id = account_repo.create_account("John Doe", Decimal("100.00"))
        with pytest.raises(ValueError, match="Account balance cannot be negative"):
            account_repo.update_balance(account_id, Decimal("-10.00"))
    
    def test_get_all_accounts_empty(self, account_repo):
        """Test getting all accounts when none exist."""
        accounts = account_repo.get_all_accounts()
        assert accounts == []
    
    def test_get_all_accounts_multiple(self, account_repo):
        """Test getting all accounts with multiple accounts."""
        id1 = account_repo.create_account("Alice", Decimal("100.00"))
        id2 = account_repo.create_account("Bob", Decimal("200.00"))
        id3 = account_repo.create_account("Charlie", Decimal("300.00"))
        
        accounts = account_repo.get_all_accounts()
        assert len(accounts) == 3
        
        # Should be ordered by name
        names = [account.name for account in accounts]
        assert names == ["Alice", "Bob", "Charlie"]
    
    def test_delete_account_zero_balance(self, account_repo):
        """Test deleting account with zero balance."""
        account_id = account_repo.create_account("John Doe", Decimal("0.00"))
        result = account_repo.delete_account(account_id)
        assert result is True
        
        deleted_account = account_repo.get_account_by_id(account_id)
        assert deleted_account is None
    
    def test_delete_account_nonzero_balance(self, account_repo):
        """Test deleting account with non-zero balance raises error."""
        account_id = account_repo.create_account("John Doe", Decimal("100.00"))
        with pytest.raises(ValueError, match="Cannot delete account with non-zero balance"):
            account_repo.delete_account(account_id)
    
    def test_delete_nonexistent_account(self, account_repo):
        """Test deleting non-existent account returns False."""
        result = account_repo.delete_account(999)
        assert result is False