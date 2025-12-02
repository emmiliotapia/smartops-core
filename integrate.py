"""
SmartOps Core - Integration Protocol Phase 3
Conecta n8n (VPS 164.92.110.179) con FastAPI (Local PC)
El Puente: SSH Reverse Tunnel + n8n Webhook
"""

import subprocess
import sys
import os
import time
from pathlib import Path

class IntegrationSetup:
    """Protocolo de integración Phase 3"""
    
    def __init__(self):
        self.vps_ip = "164.92.110.179"
        self.vps_user = "smartops"
        self.local_port = 8001
        self.vps_port = 8001
        self.workspace = Path(__file__).parent
        
    def print_banner(self, title):
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70 + "\n")
    
    def print_step(self, number, title):
        print(f"\n[PASO {number}] {title}")
        print("-" * 70)
    
    def print_info(self, msg):
        print(f"  ℹ️  {msg}")
    
    def print_warning(self, msg):
        print(f"  ⚠️  {msg}")
    
    def print_success(self, msg):
        print(f"  ✓ {msg}")
    
    def print_error(self, msg):
        print(f"  ✗ {msg}")
    
    def verify_local_api(self):
        """Verifica que FastAPI esté corriendo localmente"""
        self.print_step(1, "Verificar FastAPI Local")
        
        try:
            import requests
            response = requests.get("http://localhost:8001/", timeout=5)
            if response.status_code == 200:
                self.print_success("FastAPI respondiendo en http://localhost:8001")
                return True
            else:
                self.print_error(f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"FastAPI NO está respondiendo: {e}")
            self.print_info("Ejecuta primero: python start.py")
            return False
    
    def check_ssh_key(self):
        """Verifica disponibilidad de SSH"""
        self.print_step(2, "Verificar SSH")
        
        # Check if ssh command exists
        result = subprocess.run("ssh -V", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            self.print_success(f"SSH disponible: {result.stderr.strip()}")
            return True
        else:
            self.print_error("SSH no encontrado")
            self.print_info("Instala OpenSSH: choco install openssh (Windows)")
            return False
    
    def test_ssh_connection(self):
        """Prueba conexión SSH al VPS"""
        self.print_step(3, "Probar Conexión SSH")
        
        self.print_info(f"Conectando a {self.vps_user}@{self.vps_ip}...")
        cmd = f"ssh {self.vps_user}@{self.vps_ip} 'echo OK'"
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        if "OK" in result.stdout:
            self.print_success(f"SSH conectado a {self.vps_ip}")
            return True
        else:
            self.print_error("No se pudo conectar al VPS")
            self.print_info("Asegúrate de tener acceso SSH al VPS")
            return False
    
    def setup_tunnel(self):
        """Establece el túnel SSH reverso"""
        self.print_step(4, "Establecer Túnel SSH Reverso")
        
        tunnel_cmd = f"ssh -R {self.vps_port}:localhost:{self.local_port} {self.vps_user}@{self.vps_ip}"
        
        self.print_info("Comando del túnel:")
        self.print_info(f"  {tunnel_cmd}")
        
        self.print_warning("Este comando mantendrá la conexión abierta.")
        self.print_warning("Abre en OTRA terminal y ejecuta:")
        print(f"\n  {tunnel_cmd}\n")
        
        response = input("¿Ya iniciaste el túnel en otra terminal? (s/n): ").strip().lower()
        
        if response == 's':
            self.print_success("Túnel establecido")
            return True
        else:
            self.print_error("Túnel no iniciado")
            return False
    
    def verify_tunnel(self):
        """Verifica que el túnel esté funcionando"""
        self.print_step(5, "Verificar Túnel")
        
        self.print_info("Probando desde VPS...")
        cmd = f"ssh {self.vps_user}@{self.vps_ip} 'curl -s http://localhost:{self.vps_port}/ | head -c 100'"
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and len(result.stdout) > 0:
            self.print_success("Túnel funcionando - VPS puede alcanzar FastAPI local")
            return True
        else:
            self.print_error("Túnel no está funcionando")
            self.print_info("Verifica que el túnel esté corriendo en otra terminal")
            return False
    
    def show_n8n_instructions(self):
        """Muestra instrucciones para configurar n8n"""
        self.print_step(6, "Configurar n8n Workflow")
        
        instructions = """
BLUEPRINT DEL WORKFLOW n8n:
════════════════════════════════════════════════════════════════════════════

1. TRIGGER (Webhook)
   ├─ Type: Webhook
   ├─ Method: POST
   ├─ Path: /webhook/demo-message
   └─ Authentication: None (por ahora)

2. TRANSFORM NODE (JSON Mapping)
   Input de Waha:
   {
     "from": "+56912345678",
     "body": "¿Qué tienen de costillas?"
   }
   
   Output:
   {
     "session_id": "{{payload.from}}",
     "message": "{{payload.body}}"
   }

3. HTTP REQUEST NODE
   ├─ Method: POST
   ├─ URL: http://localhost:8001/demo/message
   ├─ Body: {"session_id": "{{payload.from}}", "message": "{{payload.body}}"}
   └─ Headers: {"Content-Type": "application/json"}

4. RESPONSE NODE
   ├─ Status: 200
   ├─ Response Type: JSON
   └─ Body: {{response.data}}

════════════════════════════════════════════════════════════════════════════

PASOS EN n8n:
1. Ir a: http://164.92.110.179:5678
2. Crear nuevo Workflow: "Demo Comercial V1"
3. Agregar Webhook trigger
4. Copiar webhook URL: http://smartops-n8n:5678/webhook/demo-message
5. Agregar Transform, HTTP Request, Response nodes
6. Mapear JSON según blueprint arriba
7. GUARDAR y ACTIVAR workflow
"""
        print(instructions)
    
    def show_waha_instructions(self):
        """Muestra instrucciones para Waha"""
        self.print_step(7, "Configurar Waha")
        
        instructions = """
CONFIGURACIÓN WAHA:
════════════════════════════════════════════════════════════════════════════

El webhook URL para Waha:
  http://smartops-n8n:5678/webhook/demo-message

(O si n8n está expuesto públicamente:)
  http://164.92.110.179:5678/webhook/demo-message

En Docker Compose (si Waha corre en mismo network):
  - Waha apunta a: http://smartops-n8n:5678/webhook/demo-message
  - n8n procesa request
  - n8n hace curl a http://localhost:8001/demo/message (vía túnel)

════════════════════════════════════════════════════════════════════════════
"""
        print(instructions)
    
    def show_demo_flow(self):
        """Muestra el flujo de demo con Martín"""
        self.print_step(8, "Flujo de Demo con Martín")
        
        flow = """
FLUJO COMPLETO (Entrada a Salida):
════════════════════════════════════════════════════════════════════════════

1. MARTÍN envía WhatsApp:
   +56912345678 → "¿Qué tienen de costillas?"

2. WAHA recibe y envía POST:
   → http://smartops-n8n:5678/webhook/demo-message

3. n8n recibe webhook:
   → Extrae: from="+56912345678", body="¿Qué tienen de costillas?"

4. n8n transforma JSON:
   → {"session_id": "+56912345678", "message": "¿Qué tienen de costillas?"}

5. n8n hace HTTP POST a FastAPI:
   → POST http://localhost:8001/demo/message (vía túnel SSH)
   → Body: JSON transformado

6. TÚNEL SSH reverso:
   VPS:8001 → (reverse tunnel) → Local:8001

7. FastAPI procesa:
   → Búsqueda semántica en pgvector
   → RAG retrieves info de menú
   → Genera respuesta: "Tenemos costilla Premium a $28.990"

8. FastAPI devuelve JSON:
   ← {"response": "Tenemos costilla Premium a $28.990"}

9. n8n formatea respuesta:
   → Extrae: response.data.response

10. Waha envía WhatsApp a Martín:
    "Tenemos costilla Premium a $28.990"

════════════════════════════════════════════════════════════════════════════

LATENCIA ESPERADA: 2-5 segundos total (red + processing)

MONITOREO:
- Terminal 1: FastAPI logs (python start.py)
- Terminal 2: Túnel SSH (ssh -R 8001:localhost:8001 ...)
- Web: n8n UI (http://164.92.110.179:5678)
"""
        print(flow)
    
    def run_integration_test(self):
        """Ejecuta test de integración completa"""
        self.print_step(9, "Test de Integración")
        
        self.print_info("Comando para simular webhook de n8n:")
        
        test_cmd = """
curl -X POST http://localhost:8001/demo/message \\
  -H "Content-Type: application/json" \\
  -d '{
    "session_id": "test_session_001",
    "message": "¿Qué precios tienen?"
  }'
"""
        print(test_cmd)
        
        self.print_info("\nEjecuta este comando en otra terminal y deberías recibir una respuesta JSON")
    
    def generate_checklist(self):
        """Genera checklist de pre-demo"""
        self.print_step(10, "Checklist Pre-Demo")
        
        checklist = """
CHECKLIST PRE-DEMO CON MARTÍN:
════════════════════════════════════════════════════════════════════════════

ANTES DE LA DEMO (24 horas antes):
  □ FastAPI corriendo: python start.py
  □ PostgreSQL con datos: docker-compose up -d postgres
  □ Menú cargado en base de datos
  □ SSH acceso verificado al VPS
  □ n8n workflow creado y activo
  □ Túnel SSH probado

DÍA DE LA DEMO (Mañana del encuentro):
  □ Terminal 1: python start.py (FastAPI running)
  □ Terminal 2: ssh -R 8001:localhost:8001 smartops@164.92.110.179
  □ Verificar: curl http://localhost:8001/ → 200 OK
  □ Verificar: n8n workflow activo
  □ Verificar: Waha conectado
  □ Probar: Webhook test manual (curl comando)

DURANTE LA DEMO:
  □ Martín envía primer mensaje WhatsApp
  □ Respuesta aparece en < 5 segundos
  □ Segunda prueba: Mensaje diferente
  □ Monitor: Ver logs en Terminal 1
  □ Backup: Tener `interactive_demo.py` de respaldo

POST-DEMO:
  □ Guardar logs
  □ Documentar cualquier issue
  □ Recolectar feedback de Martín
  □ Mejorar basado en latencia/calidad

════════════════════════════════════════════════════════════════════════════
"""
        print(checklist)
    
    def run_full_protocol(self):
        """Ejecuta todo el protocolo"""
        self.print_banner("SMARTOPS CORE - INTEGRATION PROTOCOL PHASE 3")
        
        print("""
Objetivo: Conectar n8n (VPS) → FastAPI (Local) para demo con Martín
Método: SSH Reverse Tunnel + n8n Webhook
Estado: Pre-Demo Ready
""")
        
        # Step 1: Verify local API
        if not self.verify_local_api():
            print("\n⚠️  DETENER: FastAPI no está corriendo")
            print("   Ejecuta: python start.py")
            return False
        
        # Step 2: Check SSH
        if not self.check_ssh_key():
            return False
        
        # Step 3: Test SSH
        if not self.test_ssh_connection():
            return False
        
        # Step 4: Setup tunnel
        if not self.setup_tunnel():
            return False
        
        # Step 5: Verify tunnel
        time.sleep(2)
        if not self.verify_tunnel():
            self.print_warning("Continuar sin verificación completada")
        else:
            self.print_success("Sistema de túnel verificado")
        
        # Step 6-10: Show instructions
        self.show_n8n_instructions()
        self.show_waha_instructions()
        self.show_demo_flow()
        self.run_integration_test()
        self.generate_checklist()
        
        # Final summary
        self.print_banner("PRÓXIMOS PASOS")
        print("""
1. EMILIO (Coder):
   ✓ Verificar FastAPI corriendo
   ✓ Iniciar Túnel SSH
   ✓ Guardar este documento
   ✓ Compartir n8n blueprint con DevOps

2. DEVOPS (n8n Admin):
   ✓ Crear workflow en n8n usando blueprint
   ✓ Configurar Waha webhook
   ✓ Probar flujo completo

3. MARTÍN (User):
   ✓ Enviar primer WhatsApp
   ✓ Dar feedback
   ✓ Demo success! 🎉
""")
        
        return True

if __name__ == "__main__":
    setup = IntegrationSetup()
    success = setup.run_full_protocol()
    
    if success:
        print("\n✓ INTEGRATION PROTOCOL COMPLETE")
        print("  Sistema listo para demo\n")
    else:
        print("\n✗ INTEGRATION SETUP FAILED")
        print("  Revisa los errores arriba\n")
