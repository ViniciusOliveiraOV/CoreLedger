"""
FastAPI Backend for CoreLedger Real-time Dashboard
Provides REST API and WebSocket endpoints for real-time data streaming
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json
import asyncio
from typing import List, Dict, Any
from datetime import datetime
import uvicorn
import sys
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.database import DatabaseManager
from src.models.account import AccountRepository  
from src.ledger import BankLedger

app = FastAPI(title="CoreLedger API", version="1.0.0")

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
db = DatabaseManager("multilingual_bank.db")
ledger = BankLedger(db)

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        """Send message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Connection might be closed
                pass

manager = ConnectionManager()

# Helper functions
def format_decimal(value):
    """Convert Decimal to float for JSON serialization"""
    return float(value) if value else 0.0

def get_dashboard_data():
    """Get current dashboard data"""
    accounts = ledger.account_repo.get_all_accounts()
    
    # Calculate totals
    total_balance = sum(account.balance for account in accounts)
    total_accounts = len(accounts)
    
    # Get recent transactions
    cursor = db.connection.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM transactions 
        WHERE date(created_at) = date('now')
    """)
    today_transactions = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM transactions 
        WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
    """)
    month_transactions = cursor.fetchone()[0]
    
    # Get transaction types distribution
    cursor.execute("""
        SELECT transaction_type, COUNT(*) as count
        FROM transactions 
        GROUP BY transaction_type
    """)
    transaction_types = [{"type": row[0], "count": row[1]} for row in cursor.fetchall()]
    
    # Get recent transactions for timeline
    cursor.execute("""
        SELECT t.*, a1.name as from_name, a2.name as to_name
        FROM transactions t
        LEFT JOIN accounts a1 ON t.from_account_id = a1.id
        LEFT JOIN accounts a2 ON t.to_account_id = a2.id
        ORDER BY t.created_at DESC
        LIMIT 10
    """)
    recent_transactions = []
    for row in cursor.fetchall():
        recent_transactions.append({
            "id": row[0],
            "from_account_id": row[1],
            "to_account_id": row[2],
            "amount": format_decimal(row[3]) if isinstance(row[3], str) else row[3],
            "type": row[4],
            "description": row[5],
            "created_at": row[6],
            "from_name": row[7],
            "to_name": row[8]
        })
    
    return {
        "kpis": {
            "total_balance": format_decimal(total_balance),
            "total_accounts": total_accounts,
            "today_transactions": today_transactions,
            "month_transactions": month_transactions,
            "timestamp": datetime.now().isoformat()
        },
        "charts": {
            "transaction_types": transaction_types,
            "recent_transactions": recent_transactions,
            "accounts": [
                {
                    "id": str(account.id),
                    "name": account.name,
                    "balance": format_decimal(account.balance),
                    "created_at": account.created_at.isoformat() if account.created_at else None
                }
                for account in accounts
            ]
        }
    }

# REST API Endpoints
@app.get("/")
async def root():
    return {"message": "CoreLedger API is running", "version": "1.0.0"}

@app.get("/api/dashboard")
async def get_dashboard():
    """Get complete dashboard data"""
    return get_dashboard_data()

@app.get("/api/accounts")
async def get_accounts():
    """Get all accounts"""
    accounts = ledger.account_repo.get_all_accounts()
    return [
        {
            "id": str(account.id),
            "name": account.name,
            "balance": format_decimal(account.balance),
            "created_at": account.created_at.isoformat() if account.created_at else None
        }
        for account in accounts
    ]

@app.post("/api/accounts")
async def create_account(account_data: dict):
    """Create a new account"""
    try:
        name = account_data.get("name")
        initial_balance = account_data.get("initial_balance", 0)
        
        if not name:
            raise HTTPException(status_code=400, detail="Account name is required")
        
        account = ledger.create_account(name, initial_balance)
        
        # Broadcast update to all connected clients
        dashboard_data = get_dashboard_data()
        await manager.broadcast(json.dumps({
            "type": "dashboard_update",
            "data": dashboard_data
        }))
        
        return {
            "id": str(account.id),
            "name": account.name,
            "balance": format_decimal(account.balance),
            "created_at": account.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transactions/deposit")
async def deposit(transaction_data: dict):
    """Make a deposit"""
    try:
        account_id = transaction_data.get("account_id")
        amount = float(transaction_data.get("amount", 0))
        description = transaction_data.get("description", "")
        
        if not account_id or amount <= 0:
            raise HTTPException(status_code=400, detail="Valid account_id and amount required")
        
        success = ledger.deposit(account_id, amount, description)
        
        if success:
            # Broadcast update to all connected clients
            dashboard_data = get_dashboard_data()
            await manager.broadcast(json.dumps({
                "type": "dashboard_update",
                "data": dashboard_data
            }))
            
            return {"success": True, "message": "Deposit successful"}
        else:
            raise HTTPException(status_code=400, detail="Deposit failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transactions/withdrawal")
async def withdrawal(transaction_data: dict):
    """Make a withdrawal"""
    try:
        account_id = transaction_data.get("account_id")
        amount = float(transaction_data.get("amount", 0))
        description = transaction_data.get("description", "")
        
        if not account_id or amount <= 0:
            raise HTTPException(status_code=400, detail="Valid account_id and amount required")
        
        success = ledger.withdraw(account_id, amount, description)
        
        if success:
            # Broadcast update to all connected clients
            dashboard_data = get_dashboard_data()
            await manager.broadcast(json.dumps({
                "type": "dashboard_update",
                "data": dashboard_data
            }))
            
            return {"success": True, "message": "Withdrawal successful"}
        else:
            raise HTTPException(status_code=400, detail="Insufficient funds or withdrawal failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transactions/transfer")
async def transfer(transaction_data: dict):
    """Make a transfer between accounts"""
    try:
        from_account_id = transaction_data.get("from_account_id")
        to_account_id = transaction_data.get("to_account_id")
        amount = float(transaction_data.get("amount", 0))
        description = transaction_data.get("description", "")
        
        if not from_account_id or not to_account_id or amount <= 0:
            raise HTTPException(status_code=400, detail="Valid account IDs and amount required")
        
        success = ledger.transfer(from_account_id, to_account_id, amount, description)
        
        if success:
            # Broadcast update to all connected clients
            dashboard_data = get_dashboard_data()
            await manager.broadcast(json.dumps({
                "type": "dashboard_update",
                "data": dashboard_data
            }))
            
            return {"success": True, "message": "Transfer successful"}
        else:
            raise HTTPException(status_code=400, detail="Transfer failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial dashboard data
        dashboard_data = get_dashboard_data()
        await websocket.send_text(json.dumps({
            "type": "dashboard_update",
            "data": dashboard_data
        }))
        
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            # Echo back for now, could handle specific client requests
            await websocket.send_text(f"Echo: {data}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Real-time data simulator (for testing)
@app.post("/api/simulate/random-transaction")
async def simulate_random_transaction():
    """Simulate a random transaction for testing real-time updates"""
    import random
    
    accounts = ledger.account_repo.get_all_accounts()
    if len(accounts) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 accounts for simulation")
    
    # Random transaction type
    transaction_types = ["deposit", "withdrawal", "transfer"]
    trans_type = random.choice(transaction_types)
    amount = round(random.uniform(10, 500), 2)
    
    try:
        if trans_type == "deposit":
            account = random.choice(accounts)
            ledger.deposit(account.id, amount, "Simulated deposit")
        elif trans_type == "withdrawal":
            account = random.choice(accounts)
            ledger.withdraw(account.id, amount, "Simulated withdrawal")
        else:  # transfer
            from_acc = random.choice(accounts)
            to_acc = random.choice([acc for acc in accounts if acc.id != from_acc.id])
            ledger.transfer(from_acc.id, to_acc.id, amount, "Simulated transfer")
        
        # Broadcast update
        dashboard_data = get_dashboard_data()
        await manager.broadcast(json.dumps({
            "type": "dashboard_update",
            "data": dashboard_data
        }))
        
        return {"success": True, "transaction_type": trans_type, "amount": amount}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)