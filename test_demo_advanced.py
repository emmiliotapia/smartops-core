"""
Script de Pruebas Avanzadas - Demo Router
Casos de prueba especiales, validaciones y edge cases

Uso:
    python test_demo_advanced.py [opciones]
"""

import sys
import json
import argparse
from typing import Optional

try:
    import requests
except ImportError:
    print("ERROR: requests no instalado. Instala con: pip install requests")
    sys.exit(1)


class AdvancedTester:
    """Tester para casos avanzados y edge cases"""
    
    def __init__(self, api_url: str = "http://localhost:8001", secret: str = "flash"):
        self.api_url = api_url.rstrip("/")
        self.secret = secret
    
    def print_test(self, name: str):
        print(f"\n{'='*60}")
        print(f"PRUEBA: {name}")
        print(f"{'='*60}\n")
    
    def print_result(self, passed: bool, message: str = ""):
        status = "✅ PASADA" if passed else "❌ FALLIDA"
        print(f"{status} - {message}\n")
    
    # ========================================================================
    # CASOS DE PRUEBA
    # ========================================================================
    
    def test_invalid_secret(self):
        """Prueba: Palabra secreta incorrecta debe retornar 403"""
        self.print_test("Palabra secreta incorrecta (403)")
        
        try:
            payload = {
                "session_id": "00000000-0000-0000-0000-000000000000",
                "secret_word": "wrong_password",
                "save_lead": True
            }
            
            response = requests.post(
                f"{self.api_url}/demo/reset",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 403:
                result = response.json()
                self.print_result(
                    True,
                    f"Error 403 recibido: {result.get('detail', 'N/A')}"
                )
                return True
            else:
                self.print_result(
                    False,
                    f"Se esperaba 403, se recibió {response.status_code}"
                )
                return False
        
        except Exception as e:
            self.print_result(False, f"Excepción: {e}")
            return False
    
    def test_invalid_session_id(self):
        """Prueba: Session_id inválido debe retornar 404"""
        self.print_test("Session ID inválido (404)")
        
        try:
            payload = {
                "session_id": "00000000-0000-0000-0000-000000000000",
                "message": "test"
            }
            
            response = requests.post(
                f"{self.api_url}/demo/message",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 404:
                result = response.json()
                self.print_result(
                    True,
                    f"Error 404 recibido: {result.get('detail', 'N/A')}"
                )
                return True
            else:
                self.print_result(
                    False,
                    f"Se esperaba 404, se recibió {response.status_code}"
                )
                return False
        
        except Exception as e:
            self.print_result(False, f"Excepción: {e}")
            return False
    
    def test_invalid_file_type(self):
        """Prueba: Tipo de archivo no permitido debe retornar 400"""
        self.print_test("Tipo de archivo no permitido (400)")
        
        try:
            # Crear un archivo de prueba con extensión no permitida
            test_file_content = b"Este es un archivo de prueba"
            test_file_path = "/tmp/test_file.txt"
            
            with open(test_file_path, "wb") as f:
                f.write(test_file_content)
            
            with open(test_file_path, "rb") as f:
                files = {
                    "file": ("test_file.txt", f, "text/plain")
                }
                data = {
                    "business_name": "Test Business",
                    "business_type": "test"
                }
                
                response = requests.post(
                    f"{self.api_url}/demo/upload",
                    files=files,
                    data=data,
                    timeout=5
                )
            
            if response.status_code == 400:
                result = response.json()
                self.print_result(
                    True,
                    f"Error 400 recibido: {result.get('detail', 'N/A')}"
                )
                return True
            else:
                self.print_result(
                    False,
                    f"Se esperaba 400, se recibió {response.status_code}"
                )
                return False
        
        except FileNotFoundError:
            self.print_result(False, "No se pudo crear archivo de prueba")
            return False
        except Exception as e:
            self.print_result(False, f"Excepción: {e}")
            return False
    
    def test_empty_message(self):
        """Prueba: Mensaje vacío en /demo/message"""
        self.print_test("Mensaje vacío (validación Pydantic)")
        
        try:
            payload = {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "message": ""  # Mensaje vacío
            }
            
            response = requests.post(
                f"{self.api_url}/demo/message",
                json=payload,
                timeout=5
            )
            
            # Pydantic debe rechazar con 422
            if response.status_code == 422:
                self.print_result(
                    True,
                    "Validación Pydantic correcta (422)"
                )
                return True
            else:
                self.print_result(
                    False,
                    f"Se esperaba 422, se recibió {response.status_code}"
                )
                return False
        
        except Exception as e:
            self.print_result(False, f"Excepción: {e}")
            return False
    
    def test_missing_required_field(self):
        """Prueba: Campo requerido faltante en payload"""
        self.print_test("Campo requerido faltante (422)")
        
        try:
            # Falta session_id
            payload = {
                "message": "test"
            }
            
            response = requests.post(
                f"{self.api_url}/demo/message",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 422:
                self.print_result(
                    True,
                    "Validación de campos correcta (422)"
                )
                return True
            else:
                self.print_result(
                    False,
                    f"Se esperaba 422, se recibió {response.status_code}"
                )
                return False
        
        except Exception as e:
            self.print_result(False, f"Excepción: {e}")
            return False
    
    def test_api_connectivity(self):
        """Prueba: Conectividad básica a la API"""
        self.print_test("Conectividad API (GET /demo/health)")
        
        try:
            response = requests.get(
                f"{self.api_url}/demo/health",
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                self.print_result(
                    True,
                    f"API conectada. Status: {result.get('status')}"
                )
                return True
            else:
                self.print_result(
                    False,
                    f"API respondió con {response.status_code}"
                )
                return False
        
        except requests.exceptions.ConnectionError:
            self.print_result(False, f"No se puede conectar a {self.api_url}")
            return False
        except Exception as e:
            self.print_result(False, f"Excepción: {e}")
            return False
    
    def test_malformed_json(self):
        """Prueba: JSON malformado"""
        self.print_test("JSON malformado (400/422)")
        
        try:
            response = requests.post(
                f"{self.api_url}/demo/message",
                data="invalid json {",
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if response.status_code in [400, 422]:
                self.print_result(
                    True,
                    f"JSON malformado rechazado ({response.status_code})"
                )
                return True
            else:
                self.print_result(
                    False,
                    f"Se esperaba 400/422, se recibió {response.status_code}"
                )
                return False
        
        except Exception as e:
            self.print_result(False, f"Excepción: {e}")
            return False
    
    def test_timeout_behavior(self):
        """Prueba: Comportamiento con timeout"""
        self.print_test("Comportamiento con timeout")
        
        try:
            # Usar timeout muy corto para simular problema de red
            response = requests.get(
                f"{self.api_url}/demo/health",
                timeout=0.001  # 1ms - probablemente timeout
            )
            
            # Si no hace timeout, al menos debe responder
            if response.status_code == 200:
                self.print_result(True, "Respuesta rápida (sin timeout)")
                return True
            else:
                self.print_result(False, f"Status inesperado: {response.status_code}")
                return False
        
        except requests.exceptions.Timeout:
            self.print_result(True, "Timeout capturado correctamente")
            return True
        except Exception as e:
            self.print_result(False, f"Excepción inesperada: {e}")
            return False
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas avanzadas"""
        print(f"\n{'='*60}")
        print("PRUEBAS AVANZADAS - DEMO ROUTER")
        print(f"{'='*60}\n")
        
        tests = [
            ("Conectividad API", self.test_api_connectivity),
            ("Palabra secreta incorrecta", self.test_invalid_secret),
            ("Session ID inválido", self.test_invalid_session_id),
            ("Tipo de archivo no permitido", self.test_invalid_file_type),
            ("Mensaje vacío", self.test_empty_message),
            ("Campo requerido faltante", self.test_missing_required_field),
            ("JSON malformado", self.test_malformed_json),
            ("Comportamiento timeout", self.test_timeout_behavior),
        ]
        
        results = {}
        for test_name, test_func in tests:
            try:
                results[test_name] = test_func()
            except Exception as e:
                print(f"ERROR no manejado en {test_name}: {e}\n")
                results[test_name] = False
        
        # Resumen
        print(f"\n{'='*60}")
        print("RESUMEN DE PRUEBAS AVANZADAS")
        print(f"{'='*60}\n")
        
        passed = sum(1 for v in results.values() if v)
        failed = len(results) - passed
        
        for test_name, result in results.items():
            status = "✅" if result else "❌"
            print(f"{status} {test_name}")
        
        print(f"\nTotal: {passed} PASADAS, {failed} FALLIDAS\n")
        
        return failed == 0


def main():
    parser = argparse.ArgumentParser(
        description="Pruebas avanzadas para Demo Router"
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8001",
        help="URL de la API"
    )
    parser.add_argument(
        "--secret",
        default="flash",
        help="Palabra secreta NEURALIZER"
    )
    
    args = parser.parse_args()
    
    tester = AdvancedTester(api_url=args.api_url, secret=args.secret)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
