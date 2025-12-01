#!/usr/bin/env python
"""
LOCAL TEST SETUP - SmartOps Core v4.0
Prepara todo lo necesario para pruebas en local:
- Virtual environment
- Dependencias
- PostgreSQL + pgvector (Docker)
- FastAPI server
- Validation

Usage:
  python local_test_setup.py

"""

import os
import sys
import subprocess
import platform
from pathlib import Path

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_step(msg):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}⚙️  {msg}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.YELLOW}ℹ️  {msg}{Colors.RESET}")

def run_command(cmd, description):
    """Run a shell command and handle errors"""
    print(f"\n{Colors.YELLOW}→ {description}{Colors.RESET}")
    print(f"  Command: {cmd}\n")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
        if result.returncode == 0:
            print_success(f"{description} completed")
            return True
        else:
            print_error(f"{description} failed with code {result.returncode}")
            return False
    except Exception as e:
        print_error(f"{description} error: {e}")
        return False

def check_command_exists(cmd):
    """Check if a command exists"""
    result = subprocess.run(f"where {cmd}" if platform.system() == "Windows" else f"which {cmd}", 
                          shell=True, capture_output=True)
    return result.returncode == 0

def main():
    print(f"\n{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     LOCAL TEST SETUP - SmartOps Core v4.0                  ║")
    print("║     Setting up everything for local development            ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    # Get OS
    is_windows = platform.system() == "Windows"
    is_macos = platform.system() == "Darwin"
    is_linux = platform.system() == "Linux"
    
    # Step 1: Check Python
    print_step("1. Verificar Python")
    python_version = sys.version.split()[0]
    print_info(f"Python version: {python_version}")
    
    if sys.version_info < (3, 10):
        print_error(f"Python 3.10+ required, you have {python_version}")
        return False
    print_success("Python version OK")
    
    # Step 2: Check Virtual Environment
    print_step("2. Verificar Virtual Environment")
    venv_path = Path(".venv")
    
    if not venv_path.exists():
        print_info("Virtual environment not found, creating...")
        if is_windows:
            cmd = "python -m venv .venv"
        else:
            cmd = "python3 -m venv .venv"
        
        if not run_command(cmd, "Create virtual environment"):
            return False
    else:
        print_success("Virtual environment already exists")
    
    # Step 3: Activate Virtual Environment & Install Requirements
    print_step("3. Instalar Dependencias")
    
    if is_windows:
        pip_cmd = ".venv\\Scripts\\pip"
        python_cmd = ".venv\\Scripts\\python"
    else:
        pip_cmd = ".venv/bin/pip"
        python_cmd = ".venv/bin/python"
    
    # Install root requirements
    print_info("Installing from requirements.txt (root)...")
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Install root requirements"):
        print_error("Failed to install root requirements")
        return False
    
    print_success("All dependencies installed")
    
    # Step 4: Check Docker
    print_step("4. Verificar Docker")
    if check_command_exists("docker"):
        print_success("Docker found")
        print_info("Starting PostgreSQL + pgvector...")
        
        if not run_command("docker-compose up -d postgres", "Start PostgreSQL"):
            print_error("Failed to start PostgreSQL")
            print_info("Continuing anyway - you can start it manually with: docker-compose up -d postgres")
        else:
            print_info("PostgreSQL starting (wait 10 seconds for full startup)")
    else:
        print_error("Docker not found")
        print_info("Please install Docker Desktop and run: docker-compose up -d postgres")
    
    # Step 5: Validation
    print_step("5. Validación del Setup")
    
    if not run_command(f"{python_cmd} setup_validation.py", "Run setup validation"):
        print_error("Validation failed")
        return False
    
    print_success("Setup validation passed!")
    
    # Step 6: Next Steps
    print_step("6. PRÓXIMOS PASOS")
    
    if is_windows:
        activate_cmd = ".venv\\Scripts\\activate"
    else:
        activate_cmd = "source .venv/bin/activate"
    
    print(f"""
{Colors.GREEN}✅ SETUP COMPLETADO - Local Test Environment Ready{Colors.RESET}

{Colors.YELLOW}TERMINAL 1 - Activar FastAPI Server:{Colors.RESET}
  {activate_cmd}
  uvicorn app.main:app --reload --port 8001

{Colors.YELLOW}TERMINAL 2 - Test interactivo:{Colors.RESET}
  {activate_cmd}
  python interactive_demo.py menus/steak_cortes.jpg

{Colors.YELLOW}TERMINAL 3 - Ver logs de DB (opcional):{Colors.RESET}
  docker-compose logs -f postgres

{Colors.YELLOW}Para VPS TUNNEL (desde otra terminal):{Colors.RESET}
  ssh -R 8001:localhost:8001 root@164.92.110.179
  (Esto expone tu local 8001 en el VPS)

{Colors.YELLOW}Documentación:{Colors.RESET}
  - Quick Test: Leer QUICK_START.md
  - Full Guide: Leer ENROLL_SETUP.md
  - Testing:   Leer TESTING_GUIDE.md
  - Endpoints: http://localhost:8001/docs (cuando corre)

{Colors.GREEN}Status: 🟢 READY FOR LOCAL TESTING{Colors.RESET}
""")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
