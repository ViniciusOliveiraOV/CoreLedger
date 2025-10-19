"""Integration tests for CoreLedger system."""

import pytest
from decimal import Decimal
from tempfile import NamedTemporaryFile
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.ledger import BankLedger


class TestIntegration:
    """Integration tests for the complete ledger system."""
    
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
    
    def test_complete_banking_scenario(self, ledger):
        """Test a complete banking scenario with multiple operations."""
        # Create accounts
        alice_id = ledger.create_account("Alice Johnson", "1000.00")
        bob_id = ledger.create_account("Bob Smith", "500.00")
        charlie_id = ledger.create_account("Charlie Brown", "0.00")
        
        initial_total = ledger.get_total_system_balance()
        assert initial_total == Decimal("1500.00")
        
        # Alice deposits her salary
        ledger.deposit(alice_id, "2500.00", "Monthly salary")
        assert ledger.get_balance(alice_id) == Decimal("3500.00")
        
        # Bob withdraws some cash
        ledger.withdraw(bob_id, "100.00", "ATM withdrawal")
        assert ledger.get_balance(bob_id) == Decimal("400.00")
        
        # Alice transfers money to Bob and Charlie
        ledger.transfer(alice_id, bob_id, "300.00", "Loan to Bob")
        ledger.transfer(alice_id, charlie_id, "200.00", "Gift to Charlie")
        
        # Check final balances
        assert ledger.get_balance(alice_id) == Decimal("3000.00")
        assert ledger.get_balance(bob_id) == Decimal("700.00")
        assert ledger.get_balance(charlie_id) == Decimal("200.00")
        
        # Total should be initial + Alice's salary - Bob's withdrawal
        final_total = ledger.get_total_system_balance()
        expected_total = initial_total + Decimal("2500.00") - Decimal("100.00")
        assert final_total == expected_total == Decimal("3900.00")
        
        # Verify transaction history
        alice_transactions = ledger.get_account_transactions(alice_id)
        assert len(alice_transactions) == 4  # Initial, salary, 2 transfers
        
        bob_transactions = ledger.get_account_transactions(bob_id)
        assert len(bob_transactions) == 3  # Initial, withdrawal, transfer received
        
        charlie_transactions = ledger.get_account_transactions(charlie_id)
        assert len(charlie_transactions) == 1  # Only transfer received
    
    def test_precision_handling(self, ledger):
        """Test that decimal precision is maintained throughout operations."""
        account_id = ledger.create_account("Precision Test", "0.00")
        
        # Perform operations that might cause precision issues with floats
        ledger.deposit(account_id, "0.01")
        ledger.deposit(account_id, "0.02")
        ledger.deposit(account_id, "0.03")
        
        # 0.01 + 0.02 + 0.03 should exactly equal 0.06
        balance = ledger.get_balance(account_id)
        assert balance == Decimal("0.06")
        
        # Test with more complex precision scenarios
        ledger.deposit(account_id, "10.999")  # Should round to 11.00
        balance = ledger.get_balance(account_id)
        assert balance == Decimal("11.06")
        
        ledger.withdraw(account_id, "1.333")  # Should round to 1.33
        balance = ledger.get_balance(account_id)
        assert balance == Decimal("9.73")
    
    def test_large_number_handling(self, ledger):
        """Test handling of large monetary amounts."""
        account_id = ledger.create_account("Millionaire", "1000000.00")
        
        # Large deposit
        ledger.deposit(account_id, "999999.99")
        balance = ledger.get_balance(account_id)
        assert balance == Decimal("1999999.99")
        
        # Large withdrawal
        ledger.withdraw(account_id, "1500000.50")
        balance = ledger.get_balance(account_id)
        assert balance == Decimal("499999.49")
    
    def test_balance_consistency_after_many_operations(self, ledger):
        """Test that balance remains consistent after many operations."""
        # Create accounts
        accounts = []
        for i in range(5):
            account_id = ledger.create_account(f"User_{i}", "100.00")
            accounts.append(account_id)
        
        initial_total = ledger.get_total_system_balance()
        
        # Perform many random operations
        operations = [
            (ledger.deposit, accounts[0], "10.50"),
            (ledger.withdraw, accounts[1], "5.25"),
            (ledger.transfer, accounts[2], accounts[3], "15.00"),
            (ledger.deposit, accounts[4], "7.75"),
            (ledger.transfer, accounts[0], accounts[4], "20.00"),
            (ledger.withdraw, accounts[3], "3.50"),
            (ledger.deposit, accounts[1], "12.25"),
            (ledger.transfer, accounts[4], accounts[2], "8.00"),
        ]
        
        deposits_total = Decimal("10.50") + Decimal("7.75") + Decimal("12.25")
        withdrawals_total = Decimal("5.25") + Decimal("3.50")
        
        for operation in operations:
            if len(operation) == 3:  # deposit or withdraw
                operation[0](operation[1], operation[2])
            else:  # transfer
                operation[0](operation[1], operation[2], operation[3])
        
        # Total should be initial + deposits - withdrawals
        final_total = ledger.get_total_system_balance()
        expected_total = initial_total + deposits_total - withdrawals_total
        assert final_total == expected_total
        
        # Verify sum of individual balances equals total
        individual_sum = sum(ledger.get_balance(acc_id) for acc_id in accounts)
        assert individual_sum == final_total
    
    def test_concurrent_operations(self, ledger):
        """Test thread safety with concurrent operations."""
        # Create accounts for concurrent testing
        account1_id = ledger.create_account("Account 1", "1000.00")
        account2_id = ledger.create_account("Account 2", "1000.00")
        
        def deposit_worker(account_id, amount_str):
            """Worker function for concurrent deposits."""
            try:
                ledger.deposit(account_id, amount_str)
                return True
            except Exception:
                return False
        
        def transfer_worker(from_id, to_id, amount_str):
            """Worker function for concurrent transfers."""
            try:
                ledger.transfer(from_id, to_id, amount_str)
                return True
            except Exception:
                return False
        
        # Run concurrent operations
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            
            # Submit multiple deposits
            for i in range(20):
                future = executor.submit(deposit_worker, account1_id, "10.00")
                futures.append(future)
            
            # Submit transfers between accounts
            for i in range(10):
                future = executor.submit(transfer_worker, account1_id, account2_id, "5.00")
                futures.append(future)
            
            # Wait for all operations to complete
            results = [future.result() for future in as_completed(futures)]
        
        # Verify that most operations succeeded (some transfers might fail due to timing)
        successful_ops = sum(results)
        assert successful_ops > 25  # At least most operations should succeed
        
        # Verify total balance is still consistent
        total_balance = ledger.get_total_system_balance()
        # Started with 2000, added 20 * 10 = 200 from deposits
        # Transfers don't change total
        assert total_balance == Decimal("2200.00")
    
    def test_error_recovery(self, ledger):
        """Test system behavior after various error conditions."""
        account_id = ledger.create_account("Error Test", "100.00")
        
        # Try invalid operations
        try:
            ledger.withdraw(account_id, "200.00")  # Insufficient funds
        except Exception:
            pass
        
        try:
            ledger.deposit(account_id, "-50.00")  # Invalid amount
        except Exception:
            pass
        
        try:
            ledger.transfer(account_id, 999, "50.00")  # Non-existent account
        except Exception:
            pass
        
        # Verify account state is unchanged after errors
        balance = ledger.get_balance(account_id)
        assert balance == Decimal("100.00")
        
        # Verify system can still perform valid operations
        ledger.deposit(account_id, "25.00")
        assert ledger.get_balance(account_id) == Decimal("125.00")
    
    def test_transaction_atomicity(self, ledger):
        """Test that operations are atomic (all-or-nothing)."""
        from_id = ledger.create_account("From Account", "100.00")
        to_id = ledger.create_account("To Account", "50.00")
        
        initial_from_balance = ledger.get_balance(from_id)
        initial_to_balance = ledger.get_balance(to_id)
        
        # Try transfer that should fail
        try:
            ledger.transfer(from_id, to_id, "150.00")  # Insufficient funds
        except Exception:
            pass
        
        # Balances should be unchanged
        assert ledger.get_balance(from_id) == initial_from_balance
        assert ledger.get_balance(to_id) == initial_to_balance
        
        # Valid transfer should work completely
        ledger.transfer(from_id, to_id, "30.00")
        assert ledger.get_balance(from_id) == Decimal("70.00")
        assert ledger.get_balance(to_id) == Decimal("80.00")
    
    def test_database_persistence(self):
        """Test that data persists across ledger instances."""
        with NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            # Create ledger and add data
            with BankLedger(db_path) as ledger1:
                account_id = ledger1.create_account("Persistent User", "500.00")
                ledger1.deposit(account_id, "100.00")
                ledger1.withdraw(account_id, "50.00")
                
                final_balance = ledger1.get_balance(account_id)
                assert final_balance == Decimal("550.00")
            
            # Create new ledger instance with same database
            with BankLedger(db_path) as ledger2:
                # Data should be persisted
                account = ledger2.get_account(account_id)
                assert account.name == "Persistent User"
                assert account.balance == Decimal("550.00")
                
                # Transaction history should be preserved
                transactions = ledger2.get_account_transactions(account_id)
                assert len(transactions) == 3  # Initial + deposit + withdrawal
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)