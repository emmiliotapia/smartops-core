#!/usr/bin/env python3
"""
════════════════════════════════════════════════════════════════════════════
SmartOps Core - Local Test Launcher (Cross-Platform)
FastAPI + PostgreSQL + pgvector - All-in-one local development environment
════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from dotenv import load_dotenv

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'═' * 65}{Colors.ENDC}")
    print(f"{Colors.CYAN}{Colors.BOLD}  {text}{Colors.ENDC}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'═' * 65}{Colors.ENDC}\n")

def print_ok(text):
    print(f"{Colors.GREEN}[✓]{Colors.ENDC} {text}")

def print_error(text):
    print(f"{Colors.RED}[✗]{Colors.ENDC} {text}")

def print_warn(text):
    print(f"{Colors.YELLOW}[⚠]{Colors.ENDC} {text}")

def print_info(text):
    print(f"{Colors.BLUE}[ℹ]{Colors.ENDC} {text}")

def run_command(cmd, check=False, shell=False, capture=False):
    """Execute a command and return result"""
    try:
        if capture:
            result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        else:
            result = subprocess.run(cmd, shell=shell, check=check)
            return result.returncode, "", ""
    except FileNotFoundError as e:
        return 1, "", str(e)
    except Exception as e:
        return 1, "", str(e)

def main():
    print_header("SmartOps Core - Local Test Launcher")
    
    workspace_root = Path(__file__).parent
    os.chdir(workspace_root)
    
    # ════════════════════════════════════════════════════════════════
    # 1. CHECK VIRTUAL ENVIRONMENT
    # ════════════════════════════════════════════════════════════════
    
    print_info("Checking virtual environment...")
    
    if sys.platform == "win32":
        venv_python = workspace_root / ".venv" / "Scripts" / "python.exe"
    else:
        venv_python = workspace_root / ".venv" / "bin" / "python"
    
    if not venv_python.exists():
        print_error("Virtual environment not found")
        print_info("Run first-time setup:")
        print(f"{Colors.GREEN}  python local_test_setup.py{Colors.ENDC}\n")
        sys.exit(1)
    
    print_ok("Virtual environment found")
    
    # ════════════════════════════════════════════════════════════════
    # 2. CHECK DEPENDENCIES
    # ════════════════════════════════════════════════════════════════
    
    print_info("Checking required packages...")
    
    packages = ["fastapi", "uvicorn", "sqlalchemy", "pydantic", "python-dotenv", "pgvector"]
    test_code = f"import {', '.join(packages)}"
    
    returncode, _, _ = run_command([str(venv_python), "-c", test_code], capture=True)
    
    if returncode != 0:
        print_error("Required packages not installed")
        print_info("Run first-time setup:")
        print(f"{Colors.GREEN}  python local_test_setup.py{Colors.ENDC}\n")
        sys.exit(1)
    
    print_ok("All required packages installed")
    
    # ════════════════════════════════════════════════════════════════
    # 3. START POSTGRESQL IN DOCKER
    # ════════════════════════════════════════════════════════════════
    
    print_info("Checking Docker and PostgreSQL...")
    
    # Check if Docker is available
    returncode, _, _ = run_command(["docker", "ps"], capture=True)
    docker_available = returncode == 0
    
    if docker_available:
        print_ok("Docker is available")
        
        # Check if PostgreSQL is running
        returncode, stdout, _ = run_command(
            ["docker", "ps", "--filter", "name=postgres", "--quiet"],
            capture=True,
            shell=False
        )
        
        pg_running = bool(stdout.strip())
        
        if not pg_running:
            print_info("Starting PostgreSQL + pgvector in Docker...")
            returncode, _, stderr = run_command(["docker-compose", "up", "-d", "postgres"], capture=True)
            
            if returncode == 0:
                print_ok("PostgreSQL started")
                print_info("Waiting 15 seconds for PostgreSQL to initialize...")
                time.sleep(15)
            else:
                print_warn("Docker compose failed")
                print_warn("PostgreSQL may not start correctly")
        else:
            print_ok("PostgreSQL is already running")
    else:
        print_warn("Docker not available or not running")
        print_info("You may need to start PostgreSQL manually:")
        print(f"{Colors.GREEN}  docker-compose up -d postgres{Colors.ENDC}")
    
    # ════════════════════════════════════════════════════════════════
    # 4. TEST DATABASE CONNECTION
    # ════════════════════════════════════════════════════════════════
    
    print_info("Testing database connection...")
    
    test_db_code = """
import os
from dotenv import load_dotenv
try:
    from sqlalchemy import create_engine, text
    load_dotenv()
    db_url = os.getenv('DATABASE_URL', 'postgresql://root:password@localhost:5433/smartops_core')
    engine = create_engine(db_url, pool_pre_ping=True, connect_args={'timeout': 5})
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('OK')
except Exception as e:
    print(f'FAIL:{str(e)[:40]}')
"""
    
    returncode, stdout, _ = run_command([str(venv_python), "-c", test_db_code], capture=True)
    
    if "OK" in stdout:
        print_ok("Database connection successful")
    else:
        print_warn("Database connection failed (this may be OK if Docker is still starting)")
        if "FAIL:" in stdout:
            print(f"        {stdout.split(':')[1]}")
    
    # ════════════════════════════════════════════════════════════════
    # 5. LOAD ENVIRONMENT
    # ════════════════════════════════════════════════════════════════
    
    print_info("Loading environment variables...")
    
    env_file = workspace_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print_ok(".env file loaded")
    else:
        print_warn(".env file not found (using defaults)")
    
    # ════════════════════════════════════════════════════════════════
    # 6. LAUNCH FASTAPI SERVER
    # ════════════════════════════════════════════════════════════════
    
    print_header("✓ READY TO START FASTAPI")
    
    print(f"{Colors.CYAN}📍 FastAPI will run on:{Colors.ENDC}")
    print(f"   {Colors.GREEN}http://localhost:8001{Colors.ENDC}")
    print()
    print(f"{Colors.CYAN}📍 Documentation:{Colors.ENDC}")
    print(f"   {Colors.GREEN}http://localhost:8001/docs{Colors.ENDC} (Interactive)")
    print(f"   {Colors.GREEN}http://localhost:8001/redoc{Colors.ENDC} (ReDoc)")
    print()
    print(f"{Colors.YELLOW}QUICK TEST COMMANDS:{Colors.ENDC}")
    print(f"   {Colors.GREEN}curl http://localhost:8001/{Colors.ENDC}")
    print(f"   {Colors.GREEN}curl http://localhost:8001/semantic-engine/health{Colors.ENDC}")
    print()
    print(f"{Colors.YELLOW}Press Ctrl+C to stop the server{Colors.ENDC}")
    print()
    
    # Start uvicorn server
    uvicorn_cmd = [
        str(venv_python),
        "-m",
        "uvicorn",
        "app.main:app",
        "--reload",
        "--port", "8001",
        "--host", "0.0.0.0"
    ]
    
    try:
        run_command(uvicorn_cmd, check=False)
    except KeyboardInterrupt:
        print_info("Server stopped by user")
    except Exception as e:
        print_error(f"Error running server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
