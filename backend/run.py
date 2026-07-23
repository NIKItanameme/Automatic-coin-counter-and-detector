import os
import sys
import subprocess
import time

def run_app():
    print("--- [SYSTEM] STARTING SANCHAY-AI PROFESSIONAL SUITE ---")
    
    # 1. Check for dependencies
    print("--- [SYSTEM] CHECKING DEPENDENCIES ---")
    try:
        import fastapi
        import uvicorn
        import ultralytics
    except ImportError:
        print("--- [WARNING] Missing dependencies. Installing... ---")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    # 2. Start Backend
    print("--- [SYSTEM] LAUNCHING FASTAPI SERVER ON http://127.0.0.1:8000 ---")
    print("--- [SYSTEM] DASHBOARD ACCESSIBLE AT THE ROOT URL ---")
    
    backend_script = os.path.join("backend", "main.py")
    
    try:
        # Use uvicorn to run the app
        subprocess.run([sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--port", "8000"])
    except KeyboardInterrupt:
        print("\n--- [SYSTEM] SHUTTING DOWN ---")

if __name__ == "__main__":
    run_app()
