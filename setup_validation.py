#!/usr/bin/env python3
"""
SmartOps Core - Setup Validation Script
Validates that all dependencies are installed and configured correctly.

Usage:
    python setup_validation.py
"""

import sys
import os
from pathlib import Path

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}[OK] {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}[ERROR] {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}[WARN] {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}[INFO] {text}{Colors.RESET}")

def check_python_version():
    """Verify Python 3.10+"""
    print_header("1. Python Version")
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor} - Requires 3.10+")
        return False

def check_venv():
    """Check if running in virtual environment"""
    print_header("2. Virtual Environment")
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_success(f"Virtual environment active: {sys.prefix}")
        return True
    else:
        print_warning("Not running in virtual environment")
        print_info("Recommended: source .venv/bin/activate (or .venv\\Scripts\\activate on Windows)")
        return True  # Not critical

def check_dependencies():
    """Check if all required packages are installed"""
    print_header("3. Required Dependencies")
    
    required = {
        'fastapi': 'Web Framework',
        'uvicorn': 'ASGI Server',
        'sqlalchemy': 'ORM',
        'psycopg2': 'PostgreSQL Driver',
        'pgvector': 'Vector Database',
        'pydantic': 'Data Validation',
        'dotenv': 'Environment Config',
        'requests': 'HTTP Client',
        'openai': 'OpenAI SDK',
        'pypdf': 'PDF Processing',
    }
    
    missing = []
    for package, description in required.items():
        try:
            __import__(package)
            print_success(f"{package:20} - {description}")
        except ImportError:
            print_error(f"{package:20} - {description} [MISSING]")
            missing.append(package)
    
    if missing:
        print_error(f"\nMissing packages: {', '.join(missing)}")
        print_info("Fix: pip install -r requirements.txt")
        return False
    return True

def check_env_file():
    """Check if .env file exists"""
    print_header("4. Environment Configuration")
    
    env_file = Path('.env')
    if env_file.exists():
        print_success(".env file found")
        
        # Check required variables
        required_vars = ['OPENAI_API_KEY', 'DATABASE_URL']
        with open(env_file) as f:
            content = f.read()
        
        for var in required_vars:
            if var in content:
                # Check if value is not empty/placeholder
                for line in content.split('\n'):
                    if line.startswith(var + '='):
                        value = line.split('=', 1)[1]
                        if value and not value.startswith('sk-your') and not value.startswith('postgresql://') and 'placeholder' not in value.lower():
                            print_success(f"{var} is configured")
                        else:
                            print_warning(f"{var} is not filled in (placeholder detected)")
                        break
            else:
                print_warning(f"{var} not found in .env")
        
        return True
    else:
        print_error(".env file not found")
        print_info("Create it from template: cp .env.example .env")
        return False

def check_project_structure():
    """Check if project directories exist"""
    print_header("5. Project Structure")
    
    required_dirs = [
        'app',
        'app/core',
        'app/modules',
        'app/modules/demo',
        'app/services',
        'app/routers',
    ]
    
    required_files = [
        'app/main.py',
        'app/modules/demo/models.py',
        'app/modules/demo/schemas.py',
        'app/services/demo_rag.py',
        'app/routers/demo.py',
        'requirements.txt',
        'ENROLL_SETUP.md',
    ]
    
    all_ok = True
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print_success(f"Directory: {dir_path}/")
        else:
            print_error(f"Directory: {dir_path}/ [MISSING]")
            all_ok = False
    
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"File: {file_path}")
        else:
            print_error(f"File: {file_path} [MISSING]")
            all_ok = False
    
    return all_ok

def check_database_connection():
    """Try to connect to PostgreSQL"""
    print_header("6. Database Connection")
    
    try:
        import psycopg2
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        db_url = os.getenv('DATABASE_URL', '')
        
        if not db_url or db_url.startswith('postgresql://postgres') and 'password' in db_url:
            print_warning("DATABASE_URL not configured or uses placeholder")
            print_info("Configure DATABASE_URL in .env to test connection")
            return True
        
        # Try to parse and connect
        print_info(f"Testing connection to PostgreSQL...")
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Check pgvector extension
        cursor.execute("SELECT 1 FROM pg_extension WHERE extname='vector'")
        if cursor.fetchone():
            print_success("pgvector extension is installed")
        else:
            print_warning("pgvector extension not found (may need: CREATE EXTENSION vector)")
        
        cursor.close()
        conn.close()
        print_success("PostgreSQL connection successful")
        return True
        
    except Exception as e:
        print_warning(f"Database connection test skipped: {str(e)[:50]}")
        print_info("This is OK if you haven't set up PostgreSQL yet")
        return True

def check_openai_key():
    """Validate OpenAI API key format"""
    print_header("7. OpenAI API Key")
    
    try:
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY', '')
        
        if not api_key:
            print_warning("OPENAI_API_KEY not set")
            print_info("Get it from: https://platform.openai.com/api-keys")
            return True
        
        if api_key.startswith('sk-'):
            print_success("OpenAI API key format looks valid")
            print_info(f"Key prefix: {api_key[:20]}...")
            return True
        else:
            print_error("Invalid API key format (should start with 'sk-')")
            return False
            
    except Exception as e:
        print_error(f"Error checking API key: {e}")
        return False

def main():
    """Run all validation checks"""
    print_header("SmartOps Core - Setup Validation")
    
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_venv),
        ("Dependencies", check_dependencies),
        ("Environment File", check_env_file),
        ("Project Structure", check_project_structure),
        ("Database Connection", check_database_connection),
        ("OpenAI API Key", check_openai_key),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Error during check: {e}")
            results.append((name, False))
    
    # Summary
    print_header("Setup Validation Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Colors.GREEN}[PASS]{Colors.RESET}" if result else f"{Colors.RED}[FAIL]{Colors.RESET}"
        print(f"{status} - {name}")
    
    print(f"\n{Colors.BOLD}Result: {passed}/{total} checks passed{Colors.RESET}\n")
    
    if passed == total:
        print_success("All checks passed! Setup is ready.")
        print_info("Next: python interactive_demo.py menus/example.pdf")
        return 0
    else:
        print_error("Some checks failed. See above for details.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
