#!/usr/bin/env python
"""
VPS TUNNEL SETUP - SmartOps Core
Establece conexión SSH Reverse Tunnel con el VPS

El tunnel expone:
  Tu local 8001 (FastAPI) → VPS 8001 (accesible para n8n/Waha)

Usage:
  Windows PowerShell:
    python vps_tunnel_setup.py

  macOS/Linux:
    python3 vps_tunnel_setup.py

"""

import os
import sys
import subprocess
import platform
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def print_header():
    print(f"\n{Colors.CYAN}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     VPS TUNNEL SETUP - SmartOps Core                       ║")
    print("║     Reverse SSH Tunnel para desarrollo remoto              ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")

def print_step(msg):
    print(f"\n{Colors.BLUE}→ {msg}{Colors.RESET}")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.YELLOW}ℹ️  {msg}{Colors.RESET}")

def print_command(cmd):
    print(f"\n{Colors.CYAN}Command:{Colors.RESET}")
    print(f"  {cmd}")

def check_ssh():
    """Check if SSH is available"""
    try:
        subprocess.run(["ssh", "-V"], capture_output=True, timeout=5)
        return True
    except:
        return False

def show_options():
    """Show available tunnel options"""
    print(f"\n{Colors.YELLOW}OPCIÓN 1: REVERSE TUNNEL (Recomendado){Colors.RESET}")
    print_command("ssh -R 8001:localhost:8001 -N root@164.92.110.179")
    print("""
  Esto expone:
    Tu local 8001 → VPS puerto 8001
  
  Ventajas:
    ✅ No necesitas abrir puertos
    ✅ Seguro (SSH autenticado)
    ✅ Persistente (manténlo abierto)
  
  Uso:
    1. Abre esta terminal
    2. Espera que diga "Tunnel established"
    3. Tu FastAPI estará en: http://164.92.110.179:8001/docs
  
  Para detener: Ctrl+C
""")
    
    print(f"\n{Colors.YELLOW}OPCIÓN 2: LOCAL FORWARD (Para testing local){Colors.RESET}")
    print_command("ssh -L 8001:164.92.110.179:8001 -N root@164.92.110.179")
    print("""
  Esto permite acceder a VPS desde tu local:
    Accede a: http://localhost:8001 (que es VPS)
  
  Nota: Esto es lo opuesto - acceso VPS desde local
""")
    
    print(f"\n{Colors.YELLOW}OPCIÓN 3: FULL DOCKER COMPOSE (RECOMENDADO PARA PROD){Colors.RESET}")
    print("""
  Ver: docker-compose.yml
  
  Comando:
    docker-compose up -d app
  
  Esto lanza:
    - FastAPI en puerto 8001
    - PostgreSQL en puerto 5432
    - Todo en Docker
""")

def setup_tunnel():
    """Guide for tunnel setup"""
    is_windows = platform.system() == "Windows"
    is_macos = platform.system() == "Darwin"
    
    print_header()
    
    print(f"\n{Colors.CYAN}Requisitos:{Colors.RESET}")
    print("  1. SSH instalado (incluido en Windows 10+, macOS, Linux)")
    print("  2. Acceso SSH a VPS: root@164.92.110.179")
    print("  3. FastAPI corriendo en localhost:8001")
    
    if not check_ssh():
        print_error("SSH no encontrado en el sistema")
        print_info("Por favor instala SSH:")
        if is_windows:
            print_info("  Windows 10+: SSH viene incluido")
            print_info("  Windows <10: Descarga de https://www.putty.org/")
        elif is_macos:
            print_info("  macOS: SSH ya está incluido")
        else:
            print_info("  Linux: apt-get install openssh-client")
        return False
    
    print_success("SSH encontrado")
    
    print_step("Configuración del Túnel")
    
    show_options()
    
    print_step("PASO A PASO - OPCIÓN 1 (RECOMENDADA)")
    print(f"""
{Colors.GREEN}PASO 1: Asegúrate que FastAPI corre en local{Colors.RESET}
  Terminal 1:
    .venv\\Scripts\\activate  (Windows) o source .venv/bin/activate (Mac/Linux)
    uvicorn app.main:app --reload --port 8001
  
  Verifica: http://localhost:8001/docs (debe abrir Swagger)

{Colors.GREEN}PASO 2: Abre NUEVA terminal y establece tunnel{Colors.RESET}
  Terminal 2:
    ssh -R 8001:localhost:8001 -N root@164.92.110.179

{Colors.GREEN}PASO 3: Cuando pida contraseña{Colors.RESET}
  Ingresa: La contraseña SSH del VPS
  (Te la pasé por privado)

{Colors.GREEN}PASO 4: Si todo está bien{Colors.RESET}
  ✅ La terminal se queda abierta sin mensaje (eso es normal)
  ✅ Tu FastAPI es accesible en: http://164.92.110.179:8001/docs
  ✅ n8n/Waha puede conectarse a http://164.92.110.179:8001/demo/...

{Colors.GREEN}PASO 5: Para detener{Colors.RESET}
  Presiona: Ctrl+C en la terminal de túnel
""")
    
    print_step("TROUBLESHOOTING")
    print(f"""
{Colors.YELLOW}Problema: "Connection refused"{Colors.RESET}
  → Verifica que FastAPI corre en local puerto 8001
  
{Colors.YELLOW}Problema: "Permission denied"{Colors.RESET}
  → Verifica credenciales SSH (pídeme si no los tienes)
  
{Colors.YELLOW}Problema: "Bad local forward specification"{Colors.RESET}
  → Copia bien el comando, sin espacios extra
  
{Colors.YELLOW}Problema: Terminal se queda en blanco{Colors.RESET}
  → Eso es NORMAL, significa túnel activo ✅
""")
    
    print_step("DIAGRAMA")
    print(f"""
{Colors.CYAN}Tu Máquina               VPS (164.92.110.179)
──────────────             ─────────────────────────
│                          │
├─ FastAPI ────────────────┤─ Puerto 8001 (expuesto)
│  (localhost:8001)        │
│                          │
n8n/Waha puede conectar a:
  http://164.92.110.179:8001/demo/upload
  http://164.92.110.179:8001/demo/message
  http://164.92.110.179:8001/demo/reset

{Colors.CYAN}VPS puede ver tu código como si estuviera en VPS{Colors.RESET}
""")
    
    print_step("VERIFICAR TÚNEL")
    print(f"""
Desde otra terminal (en VPS o local):
  
  curl http://164.92.110.179:8001/docs
  
Debe devolver: HTML de Swagger UI
""")
    
    print_success("Guía de setup completada")
    print_info("Sigue los pasos arriba para establecer túnel")
    print_info("Mantén la terminal del túnel abierta mientras desarrollas")
    
    return True

def quick_start():
    """Quick command for copy-paste"""
    print(f"\n{Colors.CYAN}═══════════════════════════════════════════════════════════{Colors.RESET}")
    print(f"{Colors.GREEN}COPIA Y PEGA (Quick Start):{Colors.RESET}")
    print(f"{Colors.CYAN}═══════════════════════════════════════════════════════════{Colors.RESET}\n")
    
    is_windows = platform.system() == "Windows"
    
    if is_windows:
        print(f"{Colors.YELLOW}En PowerShell (Terminal 1 - FastAPI):{Colors.RESET}")
        print(f"""
{Colors.CYAN}.venv\\Scripts\\activate
uvicorn app.main:app --reload --port 8001{Colors.RESET}
""")
    else:
        print(f"{Colors.YELLOW}En Terminal 1 (FastAPI):{Colors.RESET}")
        print(f"""
{Colors.CYAN}source .venv/bin/activate
uvicorn app.main:app --reload --port 8001{Colors.RESET}
""")
    
    print(f"{Colors.YELLOW}En Terminal 2 (SSH Tunnel):{Colors.RESET}")
    print(f"""
{Colors.CYAN}ssh -R 8001:localhost:8001 -N root@164.92.110.179{Colors.RESET}

(Cuando te pida password, ingresa tu contraseña SSH)
""")
    
    print(f"{Colors.YELLOW}En Terminal 3 (Test - opcional):{Colors.RESET}")
    print(f"""
{Colors.CYAN}source .venv/bin/activate  (o .venv\\Scripts\\activate)
python interactive_demo.py menus/steak_cortes.jpg{Colors.RESET}
""")
    
    print(f"\n{Colors.GREEN}✅ Listo. FastAPI disponible en:{Colors.RESET}")
    print(f"  Local:   http://localhost:8001/docs")
    print(f"  VPS:     http://164.92.110.179:8001/docs")
    print(f"  n8n puede conectar a puerto 8001 del VPS")

if __name__ == "__main__":
    setup_tunnel()
    quick_start()
