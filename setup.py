"""
SmartOps Core - Local Setup Script
Installs dependencies and prepares environment for local testing
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and report status"""
    if description:
        print(f"\n[*] {description}")
    print(f"    Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"[!] ERROR: {description} failed")
        return False
    print(f"[+] {description} OK")
    return True

def main():
    print("\n" + "="*60)
    print("  SmartOps Core - Local Environment Setup")
    print("="*60)
    
    workspace_root = Path(__file__).parent
    os.chdir(workspace_root)
    
    # Step 1: Check Python version
    print("\n[1] Checking Python version...")
    version_info = sys.version_info
    if version_info.major < 3 or version_info.minor < 10:
        print(f"[!] ERROR: Python 3.10+ required (found {version_info.major}.{version_info.minor})")
        sys.exit(1)
    print(f"[+] Python {version_info.major}.{version_info.minor} OK")
    
    # Step 2: Check/Create venv
    print("\n[2] Checking virtual environment...")
    venv_path = workspace_root / ".venv"
    if not venv_path.exists():
        print("[*] Creating virtual environment...")
        run_command(f"{sys.executable} -m venv .venv", "Create venv")
    print("[+] Virtual environment OK")
    
    # Step 3: Upgrade pip
    print("\n[3] Upgrading pip...")
    run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrade pip")
    
    # Step 4: Install requirements
    print("\n[4] Installing requirements...")
    run_command(f"{sys.executable} -m pip install -r requirements.txt", "Install requirements")
    
    # Step 5: Verify installation
    print("\n[5] Verifying installation...")
    packages_to_check = ["fastapi", "uvicorn", "sqlalchemy", "pydantic", "dotenv"]
    check_cmd = f"{sys.executable} -c \"import {', '.join(packages_to_check)}; print('OK')\""
    result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True, timeout=30)
    if "OK" in result.stdout:
        print("[+] All packages installed OK")
    else:
        print("[!] ERROR: Some packages missing")
        sys.exit(1)
    
    # Step 6: Check Docker
    print("\n[6] Checking Docker...")
    result = subprocess.run("docker ps", shell=True, capture_output=True)
    if result.returncode == 0:
        print("[+] Docker OK")
    else:
        print("[!] WARNING: Docker not running (you can start it later)")
    
    # Step 7: Summary
    print("\n" + "="*60)
    print("  Setup Complete!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Start the server:")
    print("     python run_local_test.py")
    print("\n  2. Or test manually:")
    print("     docker-compose up -d postgres")
    print("     uvicorn app.main:app --reload --port 8001")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
