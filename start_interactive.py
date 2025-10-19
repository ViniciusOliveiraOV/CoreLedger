"""
Demo script to showcase the interactive CLI features.

This script demonstrates various operations you can perform
with the interactive CLI interface.
"""

import os
import sys

def main():
    print("🏦 CoreLedger Interactive CLI Demo")
    print("=" * 50)
    print()
    print("The interactive CLI provides a complete terminal-based")
    print("interface for managing your bank accounts.")
    print()
    print("🎯 Features Available:")
    print("• Create new accounts with initial balances")
    print("• Make deposits and withdrawals")
    print("• Transfer money between accounts")
    print("• View detailed account information")
    print("• See complete transaction history")
    print("• List all accounts with balances")
    print("• Delete accounts (when balance is zero)")
    print("• Automatic data persistence in SQLite")
    print()
    print("💡 How to use:")
    print("1. Run: python interactive_cli.py [database_name.db]")
    print("2. Follow the menu-driven interface")
    print("3. All operations are validated for safety")
    print("4. Data is automatically saved")
    print()
    print("🔧 Sample Commands:")
    print("python interactive_cli.py                    # Uses default database")
    print("python interactive_cli.py my_bank.db         # Uses custom database")
    print()
    print("📝 Example Session Flow:")
    print("1. Create Account -> Enter name and initial balance")
    print("2. Make Deposit -> Select account and enter amount")
    print("3. Transfer Money -> Select from/to accounts and amount")
    print("4. View All Accounts -> See complete summary")
    print("5. View Transaction History -> See all operations")
    print()
    
    # Ask if user wants to start interactive session
    try:
        response = input("🚀 Start interactive session now? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            print("\n🎯 Starting CoreLedger Interactive CLI...")
            print("(Use Ctrl+C to exit at any time)\n")
            
            # Import and start the CLI
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
            from interactive_cli import BankCLI
            
            cli = BankCLI("demo_bank.db")
            cli.start()
        else:
            print("\n👋 Run 'python interactive_cli.py' when you're ready!")
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except ImportError:
        print("\n❌ Could not import CLI. Make sure you're in the CoreLedger directory.")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()