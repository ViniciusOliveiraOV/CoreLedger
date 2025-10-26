"""
Manual Test Script - Start API Only
"""

import uvicorn
import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

if __name__ == "__main__":
    print("🚀 CoreLedger API - Manual Test Mode")
    print("📊 API: http://localhost:8000")
    print("📋 Docs: http://localhost:8000/docs")
    print("🔌 WebSocket: ws://localhost:8000/ws")
    print("=" * 50)
    
    try:
        from api.standalone_api import app
        print("✅ API imported successfully!")
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")