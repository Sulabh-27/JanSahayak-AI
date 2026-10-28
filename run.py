"""
JanSahayak AI — Main Unified Runner
Runs the FastAPI Backend & Serves the Modern React Frontend at http://localhost:8000
"""
import os
import sys
import webbrowser
import uvicorn

def main():
    print("=" * 70)
    print("🏛️  JanSahayak AI — जनसहायक AI (v2.0 Production MVP)")
    print("   AI-Assisted Government Application Review System")
    print("   Madhya Pradesh Revenue & Public Service Portal")
    print("=" * 70)
    print("🚀 Starting Unified Server at: http://localhost:8000")
    print("👤 Demo Officer Credentials:")
    print("   Username: officer")
    print("   Password: jansahayak2024")
    print("=" * 70)

    # Automatically open default browser after small delay
    if os.getenv("NO_BROWSER") != "1":
        import threading
        import time
        def open_browser():
            time.sleep(1.2)
            try:
                webbrowser.open("http://localhost:8000")
            except Exception:
                pass
        threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    main()
