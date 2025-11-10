"""
FastAPI Backend for CoreLedger Real-time Dashboard - Standalone Version
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import Response as FastAPIResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
import time
try:
    from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except Exception:
    # prometheus_client is optional for local/dev; provide no-op fallbacks so app still runs
    PROMETHEUS_AVAILABLE = False

    class Counter:
        def __init__(self, *args, **kwargs):
            pass

        def labels(self, *args, **kwargs):
            return self

        def inc(self, *args, **kwargs):
            return None

    class Histogram:
        def __init__(self, *args, **kwargs):
            pass

        def labels(self, *args, **kwargs):
            return self

        def observe(self, *args, **kwargs):
            return None

    def generate_latest():
        return b""

    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"
from typing import List, Dict, Any
from datetime import datetime
import uvicorn
import sqlite3
from decimal import Decimal

app = FastAPI(title="CoreLedger API", version="1.0.0")

# Prometheus metrics
REQUEST_COUNT = Counter(
    'coreledger_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram(
    'coreledger_request_latency_seconds', 'Request latency in seconds', ['method', 'endpoint']
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database path
import os
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "multilingual_bank.db")

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

    async def broadcast(self, message: str):
        """Send message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Connection might be closed
                pass

manager = ConnectionManager()

def get_db_connection():
    """Get database connection"""
    if not os.path.exists(DB_PATH):
        # Create database and tables if it doesn't exist
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create accounts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                balance TEXT DEFAULT '0.00',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create transactions table  
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_account_id INTEGER,
                to_account_id INTEGER,
                amount TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (from_account_id) REFERENCES accounts (id),
                FOREIGN KEY (to_account_id) REFERENCES accounts (id)
            )
        """)
        
        # Insert sample accounts
        cursor.execute("INSERT INTO accounts (name, balance) VALUES ('Conta Corrente', '1000.00')")
        cursor.execute("INSERT INTO accounts (name, balance) VALUES ('Poupança', '5000.00')")
        cursor.execute("INSERT INTO accounts (name, balance) VALUES ('Investimentos', '10000.00')")
        
        conn.commit()
        print(f"✅ Database created at: {DB_PATH}")
    else:
        conn = sqlite3.connect(DB_PATH)
    
    conn.row_factory = sqlite3.Row
    return conn

def format_decimal(value):
    """Convert string to float for JSON serialization"""
    try:
        return float(value) if value else 0.0
    except:
        return 0.0

def get_dashboard_data():
    """Get current dashboard data"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Get all accounts
        cursor.execute("SELECT * FROM accounts")
        accounts = cursor.fetchall()
        
        # Calculate totals
        total_balance = sum(format_decimal(account['balance']) for account in accounts)
        total_accounts = len(accounts)
        
        # Get today's transactions
        cursor.execute("""
            SELECT COUNT(*) FROM transactions 
            WHERE date(created_at) = date('now')
        """)
        today_transactions = cursor.fetchone()[0]
        
        # Get month's transactions
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
        
        # Get recent transactions
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
                "amount": format_decimal(row[3]),
                "type": row[4],
                "description": row[5],
                "created_at": row[6],
                "from_name": row[7],
                "to_name": row[8]
            })
        
        return {
            "kpis": {
                "total_balance": total_balance,
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
                        "id": str(account['id']),
                        "name": account['name'],
                        "balance": format_decimal(account['balance']),
                        "created_at": account['created_at']
                    }
                    for account in accounts
                ]
            }
        }
    finally:
        conn.close()

# REST API Endpoints
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = time.time() - start
    try:
        endpoint = request.url.path
        method = request.method
        status = getattr(response, 'status_code', 200)
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(elapsed)
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, http_status=str(status)).inc()
    except Exception:
        pass
    return response

@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return FastAPIResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/healthz")
def healthz():
    """Simple healthcheck: DB connectivity and WS connection count"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        return {"status": "ok", "db": "ok", "ws_connections": len(manager.active_connections)}
    except Exception as e:
        return {"status": "fail", "error": str(e)}
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
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts")
        accounts = cursor.fetchall()
        
        return [
            {
                "id": str(account['id']),
                "name": account['name'],
                "balance": format_decimal(account['balance']),
                "created_at": account['created_at']
            }
            for account in accounts
        ]
    finally:
        conn.close()

@app.post("/api/accounts")
async def create_account(account_data: dict):
    """Create a new account"""
    try:
        name = account_data.get("name")
        initial_balance = account_data.get("initial_balance", 0)
        
        if not name:
            raise HTTPException(status_code=400, detail="Account name is required")
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO accounts (name, balance, created_at) 
                VALUES (?, ?, datetime('now'))
            """, (name, str(Decimal(str(initial_balance)))))
            conn.commit()
            
            account_id = cursor.lastrowid
            
            # Broadcast update
            dashboard_data = get_dashboard_data()
            await manager.broadcast(json.dumps({
                "type": "dashboard_update",
                "data": dashboard_data
            }))
            
            return {
                "id": account_id,
                "name": name,
                "balance": float(initial_balance),
                "created_at": datetime.now().isoformat()
            }
        finally:
            conn.close()
            
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
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Get current balance
            cursor.execute("SELECT balance FROM accounts WHERE id = ?", (account_id,))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Account not found")
            
            current_balance = Decimal(row[0])
            new_balance = current_balance + Decimal(str(amount))
            
            # Update balance
            cursor.execute("""
                UPDATE accounts SET balance = ? WHERE id = ?
            """, (str(new_balance), account_id))
            
            # Record transaction
            cursor.execute("""
                INSERT INTO transactions (to_account_id, amount, transaction_type, description, created_at)
                VALUES (?, ?, 'deposit', ?, datetime('now'))
            """, (account_id, str(Decimal(str(amount))), description))
            
            conn.commit()
            
            # Broadcast update
            dashboard_data = get_dashboard_data()
            await manager.broadcast(json.dumps({
                "type": "dashboard_update",
                "data": dashboard_data
            }))
            
            return {"success": True, "message": "Deposit successful"}
            
        finally:
            conn.close()
            
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
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Get current balance
            cursor.execute("SELECT balance FROM accounts WHERE id = ?", (account_id,))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Account not found")
            
            current_balance = Decimal(row[0])
            if current_balance < Decimal(str(amount)):
                raise HTTPException(status_code=400, detail="Insufficient funds")
            
            new_balance = current_balance - Decimal(str(amount))
            
            # Update balance
            cursor.execute("""
                UPDATE accounts SET balance = ? WHERE id = ?
            """, (str(new_balance), account_id))
            
            # Record transaction
            cursor.execute("""
                INSERT INTO transactions (from_account_id, amount, transaction_type, description, created_at)
                VALUES (?, ?, 'withdrawal', ?, datetime('now'))
            """, (account_id, str(Decimal(str(amount))), description))
            
            conn.commit()
            
            # Broadcast update
            dashboard_data = get_dashboard_data()
            await manager.broadcast(json.dumps({
                "type": "dashboard_update",
                "data": dashboard_data
            }))
            
            return {"success": True, "message": "Withdrawal successful"}
            
        finally:
            conn.close()
            
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
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Get both account balances
            cursor.execute("SELECT balance FROM accounts WHERE id = ?", (from_account_id,))
            from_row = cursor.fetchone()
            if not from_row:
                raise HTTPException(status_code=404, detail="From account not found")
            
            cursor.execute("SELECT balance FROM accounts WHERE id = ?", (to_account_id,))
            to_row = cursor.fetchone()
            if not to_row:
                raise HTTPException(status_code=404, detail="To account not found")
            
            from_balance = Decimal(from_row[0])
            to_balance = Decimal(to_row[0])
            transfer_amount = Decimal(str(amount))
            
            if from_balance < transfer_amount:
                raise HTTPException(status_code=400, detail="Insufficient funds")
            
            # Update balances
            cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", 
                         (str(from_balance - transfer_amount), from_account_id))
            cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", 
                         (str(to_balance + transfer_amount), to_account_id))
            
            # Record transaction
            cursor.execute("""
                INSERT INTO transactions (from_account_id, to_account_id, amount, transaction_type, description, created_at)
                VALUES (?, ?, ?, 'transfer', ?, datetime('now'))
            """, (from_account_id, to_account_id, str(transfer_amount), description))
            
            conn.commit()
            
            # Broadcast update
            dashboard_data = get_dashboard_data()
            await manager.broadcast(json.dumps({
                "type": "dashboard_update", 
                "data": dashboard_data
            }))
            
            return {"success": True, "message": "Transfer successful"}
            
        finally:
            conn.close()
            
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
        
        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            # Echo back for now
            await websocket.send_text(f"Echo: {data}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Simulation endpoint for testing
@app.post("/api/simulate/random-transaction")
async def simulate_random_transaction():
    """Simulate a random transaction for testing real-time updates"""
    import random
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts")
        accounts = cursor.fetchall()
        
        if len(accounts) < 1:
            raise HTTPException(status_code=400, detail="Need at least 1 account for simulation")
        
        # Random transaction
        transaction_types = ["deposit", "withdrawal"]
        if len(accounts) >= 2:
            transaction_types.append("transfer")
            
        trans_type = random.choice(transaction_types)
        amount = round(random.uniform(10, 100), 2)
        
        if trans_type == "deposit":
            account = random.choice(accounts)
            current_balance = Decimal(account['balance'])
            new_balance = current_balance + Decimal(str(amount))
            
            cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", 
                         (str(new_balance), account['id']))
            cursor.execute("""
                INSERT INTO transactions (to_account_id, amount, transaction_type, description, created_at)
                VALUES (?, ?, 'deposit', 'Simulated deposit', datetime('now'))
            """, (account['id'], str(Decimal(str(amount)))))
            
        elif trans_type == "withdrawal":
            # Find account with sufficient funds
            eligible_accounts = [acc for acc in accounts if Decimal(acc['balance']) >= Decimal(str(amount))]
            if not eligible_accounts:
                # Default to deposit if no eligible accounts
                account = random.choice(accounts)
                current_balance = Decimal(account['balance'])
                new_balance = current_balance + Decimal(str(amount))
                
                cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", 
                             (str(new_balance), account['id']))
                cursor.execute("""
                    INSERT INTO transactions (to_account_id, amount, transaction_type, description, created_at)
                    VALUES (?, ?, 'deposit', 'Simulated deposit (no funds for withdrawal)', datetime('now'))
                """, (account['id'], str(Decimal(str(amount)))))
                trans_type = "deposit"
            else:
                account = random.choice(eligible_accounts)
                current_balance = Decimal(account['balance'])
                new_balance = current_balance - Decimal(str(amount))
                
                cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", 
                             (str(new_balance), account['id']))
                cursor.execute("""
                    INSERT INTO transactions (from_account_id, amount, transaction_type, description, created_at)
                    VALUES (?, ?, 'withdrawal', 'Simulated withdrawal', datetime('now'))
                """, (account['id'], str(Decimal(str(amount)))))
        
        else:  # transfer
            from_acc = random.choice(accounts)
            to_acc = random.choice([acc for acc in accounts if acc['id'] != from_acc['id']])
            
            from_balance = Decimal(from_acc['balance'])
            to_balance = Decimal(to_acc['balance'])
            
            # Reduce amount if insufficient funds
            if from_balance < Decimal(str(amount)):
                amount = float(from_balance * Decimal('0.5'))  # Transfer 50% of available funds
                if amount < 1:
                    amount = 1.0
            
            transfer_amount = Decimal(str(amount))
            
            cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", 
                         (str(from_balance - transfer_amount), from_acc['id']))
            cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", 
                         (str(to_balance + transfer_amount), to_acc['id']))
            cursor.execute("""
                INSERT INTO transactions (from_account_id, to_account_id, amount, transaction_type, description, created_at)
                VALUES (?, ?, ?, 'transfer', 'Simulated transfer', datetime('now'))
            """, (from_acc['id'], to_acc['id'], str(transfer_amount)))
        
        conn.commit()
        
        # Broadcast update
        dashboard_data = get_dashboard_data()
        await manager.broadcast(json.dumps({
            "type": "dashboard_update",
            "data": dashboard_data
        }))
        
        return {"success": True, "transaction_type": trans_type, "amount": amount}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Starting CoreLedger API...")
    print("📊 Dashboard will be available at: http://localhost:8000")
    print("🔌 WebSocket endpoint: ws://localhost:8000/ws")
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()