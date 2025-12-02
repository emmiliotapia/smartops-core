"""
SmartOps Core - Local Test Launcher
Starts FastAPI with PostgreSQL + pgvector
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def main():
    print("\n" + "="*70)
    print("  SmartOps Core - Local Test Launcher")
    print("  FastAPI + PostgreSQL + pgvector")
    print("="*70 + "\n")
    
    workspace = Path(__file__).parent
    os.chdir(workspace)
    
    # Check packages
    print("[*] Checking packages...")
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pydantic
        from dotenv import load_dotenv
        print("[+] All packages OK\n")
    except ImportError as e:
        print(f"[!] ERROR: Missing package: {e}")
        print("[*] Run setup first: python setup.py")
        sys.exit(1)
    
    # Check Docker and PostgreSQL
    print("[*] Checking Docker...")
    result = subprocess.run("docker ps --filter name=postgres --quiet", 
                          shell=True, capture_output=True, text=True)
    
    if not result.stdout.strip():
        print("[*] Starting PostgreSQL container...")
        result = subprocess.run("docker-compose up -d postgres", 
                              shell=True, capture_output=True)
        if result.returncode == 0:
            print("[+] PostgreSQL started")
            print("[*] Waiting 15 seconds for PostgreSQL to initialize...")
            time.sleep(15)
        else:
            print("[!] WARNING: Could not start PostgreSQL")
    else:
        print("[+] PostgreSQL already running")
    
    # Load environment
    print("\n[*] Loading environment...")
    env_file = workspace / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print("[+] .env loaded")
    else:
        print("[!] WARNING: .env not found")
    
    # Start FastAPI
    print("\n" + "="*70)
    print("✓ READY TO START FASTAPI")
    print("="*70)
    print("\n📍 FastAPI will run on: http://localhost:8001")
    print("📍 Swagger UI:         http://localhost:8001/docs")
    print("📍 ReDoc:              http://localhost:8001/redoc")
    print("\n  Quick test commands:")
    print("    curl http://localhost:8001/")
    print("    curl http://localhost:8001/semantic-engine/health")
    print("\n  Press Ctrl+C to stop\n")
    print("="*70 + "\n")
    
    # Launch uvicorn
    cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--reload",
        "--port", "8001",
        "--host", "0.0.0.0"
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n[*] Server stopped")

if __name__ == "__main__":
    main()
