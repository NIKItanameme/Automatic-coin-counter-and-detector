import os
import sys
import subprocess

def run_app():
    port = os.environ.get("PORT", "8000")

    print(f"Starting server on port {port}...")

    subprocess.run([
        sys.executable,
        "-m",
        "uvicorn",
        "main:app",
        "--host",
        "0.0.0.0",
        "--port",
        port
    ], check=True)

if __name__ == "__main__":
    run_app()