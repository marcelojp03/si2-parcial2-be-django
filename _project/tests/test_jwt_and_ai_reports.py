"""
Script de prueba para JWT y Reportes con IA
Ejecutar: python _project/tests/test_jwt_and_ai_reports.py
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test(name):
    print(f"\n{Colors.BLUE}{'='*80}")
    print(f"TEST: {name}")
    print(f"{'='*80}{Colors.RESET}")

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.YELLOW}ℹ {msg}{Colors.RESET}")


# =============================================================================
# PRUEBAS DE JWT
# =============================================================================

def test_jwt_endpoints():
    """Prueba los endpoints de JWT"""
    
    # 1. Obtener token JWT
    print_test("1. Obtener Token JWT (Login)")
    
    login_data = {
        "username": "admin",
        "password": "admin123"  # Cambia esto según tu usuario
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/token/", json=login_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            tokens = response.json()
            access_token = tokens.get('access')
            refresh_token = tokens.get('refresh')
            
            if access_token:
                print_success("Token de acceso obtenido correctamente")
                print_info(f"Access Token: {access_token[:50]}...")
                print_info(f"Refresh Token: {refresh_token[:50]}...")
                
                # Guardar tokens para siguientes pruebas
                return {
                    'access': access_token,
                    'refresh': refresh_token
                }
            else:
                print_error("No se recibió token de acceso")
                return None
        else:
            print_error(f"Error al obtener token: {response.json()}")
            return None
            
    except Exception as e:
        print_error(f"Excepción: {e}")
        return None


def test_refresh_token(refresh_token):
    """Prueba el refresh de token"""
    print_test("2. Refrescar Token JWT")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/token/refresh/",
            json={"refresh": refresh_token}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            new_tokens = response.json()
            print_success("Token refrescado correctamente")
            print_info(f"Nuevo Access Token: {new_tokens.get('access', '')[:50]}...")
            return new_tokens.get('access')
        else:
            print_error(f"Error al refrescar token: {response.json()}")
            return None
            
    except Exception as e:
        print_error(f"Excepción: {e}")
        return None


def test_verify_token(access_token):
    """Prueba la verificación de token"""
    print_test("3. Verificar Token JWT")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/token/verify/",
            json={"token": access_token}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print_success("Token válido")
        else:
            print_error(f"Token inválido: {response.json()}")
            
    except Exception as e:
        print_error(f"Excepción: {e}")


def test_protected_endpoint(access_token):
    """Prueba acceso a endpoint protegido"""
    print_test("4. Acceso a Endpoint Protegido (/api/auth/me/)")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/auth/me/", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print_success("Acceso autorizado - Usuario obtenido")
        else:
            print_error(f"Acceso denegado: {response.json()}")
            
    except Exception as e:
        print_error(f"Excepción: {e}")


def test_without_token():
    """Prueba acceso sin token (debe fallar)"""
    print_test("5. Acceso sin Token (debe fallar)")
    
    try:
        response = requests.get(f"{BASE_URL}/api/sales/orders/")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print_success("Correctamente bloqueado - Se requiere autenticación")
            print_info("Endpoint /api/sales/orders/ requiere autenticación ✓")
        else:
            print_error(f"Debería estar protegido pero respondió: {response.status_code}")
            
    except Exception as e:
        print_error(f"Excepción: {e}")


# =============================================================================
# PRUEBAS DE REPORTES CON IA
# =============================================================================

def test_ai_report_json(access_token):
    """Prueba reporte con IA - formato JSON"""
    print_test("6. Reporte con IA - Formato JSON")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": "Muéstrame los últimos 5 productos del catálogo con su nombre y precio",
        "format": "json",
        "limit": 5
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/analytics/reports/ai-report/",
            headers=headers,
            json=payload
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            print_success("Reporte generado exitosamente")
            
            if result.get('data'):
                data = result['data']
                print_info(f"SQL generado: {data.get('sql', 'N/A')}")
                print_info(f"Columnas: {data.get('columns', [])}")
                print_info(f"Filas retornadas: {len(data.get('rows', []))}")
                if data.get('interpretation'):
                    print_info(f"Interpretación IA: {data['interpretation']}")
        else:
            print_error(f"Error: {response.json()}")
            
    except Exception as e:
        print_error(f"Excepción: {e}")


def test_ai_report_dry_run(access_token):
    """Prueba generación de SQL sin ejecutar"""
    print_test("7. Reporte con IA - Dry Run (solo SQL)")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": "Dame las ventas del último mes agrupadas por producto",
        "dry_run": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/analytics/reports/ai-report/",
            headers=headers,
            json=payload
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            print_success("SQL generado (no ejecutado)")
            
            if result.get('data', {}).get('sql'):
                print_info(f"SQL: {result['data']['sql']}")
        else:
            print_error(f"Error: {response.json()}")
            
    except Exception as e:
        print_error(f"Excepción: {e}")


def test_ai_report_csv(access_token):
    """Prueba reporte con IA - formato CSV"""
    print_test("8. Reporte con IA - Formato CSV")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": "Lista las categorías del catálogo",
        "format": "csv",
        "limit": 10
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/analytics/reports/ai-report/",
            headers=headers,
            json=payload
        )
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            print_success("CSV generado exitosamente")
            print_info(f"Tamaño del archivo: {len(response.content)} bytes")
            print_info("Primeras líneas del CSV:")
            print(response.text[:500])  # Mostrar primeras líneas
        else:
            print_error(f"Error: {response.text}")
            
    except Exception as e:
        print_error(f"Excepción: {e}")


def test_ai_report_excel(access_token):
    """Prueba reporte con IA - formato Excel"""
    print_test("9. Reporte con IA - Formato Excel")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": "Muéstrame los almacenes disponibles",
        "format": "excel",
        "limit": 10
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/analytics/reports/ai-report/",
            headers=headers,
            json=payload
        )
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            print_success("Excel generado exitosamente")
            print_info(f"Tamaño del archivo: {len(response.content)} bytes")
            
            # Guardar archivo de prueba
            filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print_info(f"Archivo guardado: {filename}")
        else:
            print_error(f"Error: {response.text}")
            
    except Exception as e:
        print_error(f"Excepción: {e}")


def test_ai_report_pdf(access_token):
    """Prueba reporte con IA - formato PDF"""
    print_test("10. Reporte con IA - Formato PDF")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": "Lista los primeros 5 productos",
        "format": "pdf",
        "limit": 5
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/analytics/reports/ai-report/",
            headers=headers,
            json=payload
        )
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            print_success("PDF generado exitosamente")
            print_info(f"Tamaño del archivo: {len(response.content)} bytes")
            
            # Guardar archivo de prueba
            filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print_info(f"Archivo guardado: {filename}")
        else:
            print_error(f"Error: {response.text}")
            
    except Exception as e:
        print_error(f"Excepción: {e}")


def test_ai_report_complex_query(access_token):
    """Prueba con consulta compleja"""
    print_test("11. Reporte con IA - Consulta Compleja")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": "Dame el total de productos por categoría ordenado de mayor a menor",
        "format": "json",
        "limit": 20
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/analytics/reports/ai-report/",
            headers=headers,
            json=payload
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            print_success("Consulta compleja ejecutada exitosamente")
        else:
            print_error(f"Error: {response.json()}")
            
    except Exception as e:
        print_error(f"Excepción: {e}")


# =============================================================================
# MAIN - EJECUTAR TODAS LAS PRUEBAS
# =============================================================================

def main():
    """Ejecuta todas las pruebas"""
    print(f"\n{Colors.BLUE}{'='*80}")
    print("INICIANDO PRUEBAS DE JWT Y REPORTES CON IA")
    print(f"Base URL: {BASE_URL}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}{Colors.RESET}\n")
    
    # ==== PRUEBAS JWT ====
    print(f"\n{Colors.YELLOW}{'='*80}")
    print("SECCIÓN 1: AUTENTICACIÓN JWT")
    print(f"{'='*80}{Colors.RESET}")
    
    # 1. Login y obtener tokens
    tokens = test_jwt_endpoints()
    
    if not tokens:
        print_error("\n⚠️  No se pudieron obtener tokens. Verifica que:")
        print("   1. El servidor esté corriendo en http://127.0.0.1:8000")
        print("   2. Existe un usuario 'admin' con contraseña 'admin123'")
        print("   3. Puedes crear el usuario con: python manage.py createsuperuser")
        return
    
    access_token = tokens['access']
    refresh_token = tokens['refresh']
    
    # 2-5. Otras pruebas JWT
    test_refresh_token(refresh_token)
    test_verify_token(access_token)
    test_protected_endpoint(access_token)
    test_without_token()
    
    # ==== PRUEBAS REPORTES CON IA ====
    print(f"\n{Colors.YELLOW}{'='*80}")
    print("SECCIÓN 2: REPORTES CON IA")
    print(f"{'='*80}{Colors.RESET}")
    
    # 6-11. Pruebas de reportes
    test_ai_report_json(access_token)
    test_ai_report_dry_run(access_token)
    test_ai_report_csv(access_token)
    test_ai_report_excel(access_token)
    test_ai_report_pdf(access_token)
    test_ai_report_complex_query(access_token)
    
    # ==== RESUMEN ====
    print(f"\n{Colors.GREEN}{'='*80}")
    print("PRUEBAS COMPLETADAS")
    print(f"{'='*80}{Colors.RESET}\n")
    
    print("📋 Funcionalidades probadas:")
    print("   ✓ JWT Login (obtener access + refresh token)")
    print("   ✓ JWT Refresh (renovar access token)")
    print("   ✓ JWT Verify (validar token)")
    print("   ✓ Endpoints protegidos con JWT")
    print("   ✓ Reportes con IA - Formato JSON")
    print("   ✓ Reportes con IA - Dry Run (solo SQL)")
    print("   ✓ Reportes con IA - Formato CSV")
    print("   ✓ Reportes con IA - Formato Excel")
    print("   ✓ Reportes con IA - Formato PDF")
    print("   ✓ Consultas complejas con IA")
    
    print("\n📁 Archivos generados:")
    print("   - test_report_*.xlsx (Excel)")
    print("   - test_report_*.pdf (PDF)")
    
    print(f"\n{Colors.BLUE}Siguiente paso: Revisar Swagger UI en http://127.0.0.1:8000/api/docs/{Colors.RESET}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Pruebas interrumpidas por el usuario{Colors.RESET}\n")
    except Exception as e:
        print(f"\n{Colors.RED}Error fatal: {e}{Colors.RESET}\n")
