"""
Verification script to test all CoreLedger functionality.

This script runs a comprehensive test of all features to ensure 
the system is working correctly.
"""

import sys
import os
from decimal import Decimal

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ledger import BankLedger
from models.account import InsufficientFundsError, InvalidAmountError


def test_basic_operations():
    """Test basic account operations."""
    print("Testing basic operations...")
    
    with BankLedger(":memory:") as ledger:
        # Test account creation
        alice_id = ledger.create_account("Alice", "1000.00")
        bob_id = ledger.create_account("Bob", "500.00")
        
        assert ledger.get_balance(alice_id) == Decimal("1000.00")
        assert ledger.get_balance(bob_id) == Decimal("500.00")
        
        # Test deposit
        ledger.deposit(alice_id, "200.50")
        assert ledger.get_balance(alice_id) == Decimal("1200.50")
        
        # Test withdrawal
        ledger.withdraw(bob_id, "100.00")
        assert ledger.get_balance(bob_id) == Decimal("400.00")
        
        # Test transfer
        ledger.transfer(alice_id, bob_id, "300.00")
        assert ledger.get_balance(alice_id) == Decimal("900.50")
        assert ledger.get_balance(bob_id) == Decimal("700.00")
        
        print("✓ Basic operations passed")


def test_error_handling():
    """Test error conditions."""
    print("Testing error handling...")
    
    with BankLedger(":memory:") as ledger:
        account_id = ledger.create_account("Test", "100.00")
        
        # Test insufficient funds
        try:
            ledger.withdraw(account_id, "200.00")
            assert False, "Should have raised InsufficientFundsError"
        except InsufficientFundsError:
            pass
        
        # Test negative amounts
        try:
            ledger.deposit(account_id, "-50.00")
            assert False, "Should have raised InvalidAmountError"
        except InvalidAmountError:
            pass
        
        # Test same account transfer
        try:
            ledger.transfer(account_id, account_id, "50.00")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
        
        print("✓ Error handling passed")


def test_precision():
    """Test decimal precision."""
    print("Testing decimal precision...")
    
    with BankLedger(":memory:") as ledger:
        account_id = ledger.create_account("Precision", "0.00")
        
        # Test precision with small amounts
        ledger.deposit(account_id, "0.01")
        ledger.deposit(account_id, "0.02")
        ledger.deposit(account_id, "0.03")
        
        balance = ledger.get_balance(account_id)
        assert balance == Decimal("0.06"), f"Expected 0.06, got {balance}"
        
        # Test rounding
        ledger.deposit(account_id, "10.999")  # Should round to 11.00
        balance = ledger.get_balance(account_id)
        assert balance == Decimal("11.06"), f"Expected 11.06, got {balance}"
        
        print("✓ Precision handling passed")


def test_balance_consistency():
    """Test that total balance is always conserved."""
    print("Testing balance consistency...")
    
    with BankLedger(":memory:") as ledger:
        # Create multiple accounts
        accounts = []
        for i in range(5):
            account_id = ledger.create_account(f"User{i}", "100.00")
            accounts.append(account_id)
        
        initial_total = ledger.get_total_system_balance()
        assert initial_total == Decimal("500.00")
        
        # Perform various operations
        ledger.deposit(accounts[0], "50.00")  # +50
        ledger.withdraw(accounts[1], "25.00")  # -25
        ledger.transfer(accounts[2], accounts[3], "30.00")  # no net change
        
        final_total = ledger.get_total_system_balance()
        expected_total = initial_total + Decimal("50.00") - Decimal("25.00")
        
        assert final_total == expected_total, f"Expected {expected_total}, got {final_total}"
        
        print("✓ Balance consistency passed")


def test_transaction_history():
    """Test transaction recording."""
    print("Testing transaction history...")
    
    with BankLedger(":memory:") as ledger:
        alice_id = ledger.create_account("Alice", "500.00")
        bob_id = ledger.create_account("Bob", "300.00")
        
        # Perform operations
        ledger.deposit(alice_id, "100.00", "Salary")
        ledger.withdraw(alice_id, "50.00", "ATM")
        ledger.transfer(alice_id, bob_id, "75.00", "Payment")
        
        # Check Alice's transaction history
        alice_transactions = ledger.get_account_transactions(alice_id)
        assert len(alice_transactions) >= 4  # Initial + 3 operations
        
        # Check transaction types
        transaction_types = [t.transaction_type for t in alice_transactions]
        assert "deposit" in transaction_types
        assert "withdrawal" in transaction_types
        assert "transfer" in transaction_types
        
        print("✓ Transaction history passed")


def run_verification():
    """Run all verification tests."""
    print("=" * 50)
    print("CoreLedger Verification Tests")
    print("=" * 50)
    
    tests = [
        test_basic_operations,
        test_error_handling,
        test_precision,
        test_balance_consistency,
        test_transaction_history,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
    
    print("-" * 50)
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! CoreLedger is working correctly.")
        return True
    else:
        print(f"\n❌ {failed} tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)