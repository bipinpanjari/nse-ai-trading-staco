"""
SENSEX Options Pro - Application Entry Point
Simple startup without extra features
"""

if __name__ == "__main__":
    from app import app, socketio
    
    print("""
    ╔═════════════════════════════════════════╗
    ║  SENSEX OPTIONS PRO - v1.0.0            ║
    ║  Professional Trading Platform          ║
    ╚═════════════════════════════════════════╝
    
    🚀 Starting Application...
    📊 Open: http://localhost:5000
    🛑 Press Ctrl+C to stop
    """)
    
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
