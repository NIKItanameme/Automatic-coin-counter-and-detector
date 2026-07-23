import os
import sys
import subprocess

def run_app():
    print("--- [SYSTEM] STARTING SANCHAY-AI PROFESSIONAL SUITE ---")

    print("--- [SYSTEM] CHECKING DEPENDENCIES ---")
    try:
        import fastapi
        import uvicorn
        import ultralytics
    except ImportError:
        print("--- [WARNING] Missing dependencies. Installing... ---")
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            "../requirements.txt"
        ])

    port = os.environ.get("PORT", "8000")

    print(f"--- [SYSTEM] LAUNCHING FASTAPI SERVER ON PORT {port} ---")
    print("--- [SYSTEM] DASHBOARD ACCESSIBLE AT THE ROOT URL ---")

    try:
        subprocess.run([
            sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            "0.0.0.0",
            "--port",
            port
        ])
    except KeyboardInterrupt:
        print("\n--- [SYSTEM] SHUTTING DOWN ---")

if __name__ == "__main__":
    run_app()