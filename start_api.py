"""
Simple API starter for CoreLedger Real-time Dashboard
"""

import uvicorn
import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

if __name__ == "__main__":
    print("🚀 Starting CoreLedger API...")
    print("📊 Dashboard will be available at: http://localhost:8000")
    print("🔌 WebSocket endpoint: ws://localhost:8000/ws")
    print("📋 API Documentation: http://localhost:8000/docs")
    print("=" * 50)
    
    try:
        # Import and run the app
        from api.standalone_api import app
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except Exception as e:
        print(f"❌ Error starting API: {e}")
        import traceback
        traceback.print_exc()