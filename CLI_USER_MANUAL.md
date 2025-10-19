# 🏦 CoreLedger Interactive CLI User Manual

## Overview
The CoreLedger Interactive CLI provides a complete terminal-based interface for managing bank accounts with all the features of a simple banking system.

## Getting Started

### Quick Launch Options
```bash
# Method 1: Direct CLI
python interactive_cli.py

# Method 2: Demo with sample data  
python demo_interactive.py

# Method 3: Windows batch file
start_bank.bat

# Method 4: Custom database
python interactive_cli.py my_bank.db
```

### First Time Setup
1. The system will create a new SQLite database automatically
2. Start by creating your first account (Option 1)
3. Add some initial balance during account creation
4. You're ready to perform banking operations!

## 📋 Main Menu Options

### 1. 👤 Create New Account
- Enter account holder's name (required)
- Set initial balance (optional, defaults to $0.00)
- System validates inputs and prevents duplicates
- Returns unique account ID for tracking

**Example Flow:**
```
Enter account holder name: John Doe
Enter initial balance (or press Enter for $0.00): 1000.00
✅ Account created successfully!
   Account ID: 1
   Name: John Doe
   Initial Balance: $1000.00
```

### 2. 💰 Make Deposit
- Select target account from list
- Enter deposit amount (must be positive)
- Add optional description for tracking
- System updates balance and records transaction

**Safety Features:**
- Validates positive amounts only
- Prevents invalid decimal inputs
- Automatic precision rounding to 2 decimal places

### 3. 💸 Make Withdrawal
- Select source account from list
- Shows current balance before withdrawal
- Enter withdrawal amount
- System prevents overdrafts automatically
- Add optional description

**Safety Features:**
- Real-time balance checking
- Insufficient funds protection
- Clear error messages

### 4. 🔄 Transfer Money
- Select FROM account (source)
- Select TO account (destination, different from source)
- Enter transfer amount
- Review transfer summary
- Confirm before processing
- Both accounts updated atomically

**Safety Features:**
- Prevents self-transfers
- Atomic operations (all-or-nothing)
- Balance verification before transfer
- Confirmation step for large amounts

### 5. 💳 View Account Details
- Select account to view
- Shows complete account information:
  - Account ID and name
  - Current balance
  - Creation date
  - Last 5 transactions with descriptions

### 6. 📊 View All Accounts
- Complete overview of all accounts
- Formatted table with:
  - Account ID
  - Account holder name  
  - Current balance
  - Creation date
- Shows total system balance
- Account count summary

### 7. 📜 View Transaction History
- Select account to view history
- Complete chronological transaction list
- Shows transaction type, amount, and description
- Formatted for easy reading
- Transaction counter

**Transaction Types:**
- `DEPOSIT +` - Money added to account
- `WITHDRAW -` - Money removed from account  
- `SENT -` - Money transferred out
- `RECEIVED +` - Money transferred in

### 8. 🗑️ Delete Account
- Select account to delete
- **Safety**: Only accounts with $0.00 balance can be deleted
- Shows account details before deletion
- Requires confirmation
- Permanent action (cannot be undone)

### 9. 🚪 Exit
- Shows session summary
- Displays total accounts and balance
- Confirms data has been saved
- Safe exit with cleanup

## 💡 Tips & Best Practices

### Input Guidelines
- **Amounts**: Can include or omit dollar sign ($)
- **Decimals**: Automatic rounding to 2 decimal places
- **Names**: Cannot be empty or whitespace only
- **Descriptions**: Optional but recommended for tracking

### Error Handling
- All operations are validated before processing
- Clear error messages explain what went wrong
- System prevents data corruption
- Use Ctrl+C to safely cancel operations

### Data Safety
- All data automatically saved to SQLite database
- ACID transactions ensure consistency
- Thread-safe operations
- Automatic database creation and initialization

## 🎯 Common Usage Patterns

### Setting Up New Bank System
1. Create multiple accounts with initial balances
2. Verify setup with "View All Accounts"
3. Test with small transactions first

### Daily Banking Operations
1. Check balances with "View Account Details"
2. Make deposits/withdrawals as needed
3. Use transfers for moving money between accounts
4. Review transaction history periodically

### Account Management
1. Create accounts as needed
2. Use descriptive names for easy identification
3. Delete unused accounts after withdrawing funds
4. Regular balance verification

## 🔧 Advanced Features

### Database Management
- Each database file is independent
- Can run multiple instances with different databases
- Database files are portable (SQLite format)
- Automatic backup by copying `.db` files

### Decimal Precision
- Uses Python's `decimal.Decimal` for accuracy
- No floating-point errors (0.1 + 0.2 = 0.3 exactly)
- Automatic rounding to currency precision
- Handles large amounts safely

### Error Recovery
- Invalid operations don't affect account balances
- System maintains consistency even after errors
- Can retry operations safely
- No partial transactions

## 🚨 Important Notes

### Security
- No authentication implemented (single-user system)
- Database files store data in plain text
- Suitable for personal use or development
- Not recommended for production banking

### Limitations
- Single currency support (no exchange rates)
- No interest calculations
- No scheduled transactions
- No account types (checking/savings)

### Data Persistence
- All changes saved immediately
- Database file created in current directory
- Safe to exit and restart anytime
- Data survives system restarts

## 🆘 Troubleshooting

### Common Issues
1. **Import Errors**: Ensure you're in the CoreLedger directory
2. **Permission Errors**: Check write permissions for database file
3. **Invalid Amounts**: Use numbers only (with optional decimal point)
4. **Account Not Found**: Use "View All Accounts" to see available accounts

### Getting Help
- Use the verification script: `python examples/verify_system.py`
- Check the main README.md for setup instructions
- Review example scripts in the `examples/` directory

---

**Happy Banking! 🏦💰**