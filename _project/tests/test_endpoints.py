"""
Script para probar todos los endpoints de la API.
Genera un reporte de estado de todos los módulos.
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(method, url, data=None, description=""):
    """Prueba un endpoint y retorna el resultado"""
    full_url = f"{BASE_URL}{url}"
    try:
        if method == "GET":
            response = requests.get(full_url, timeout=5)
        elif method == "POST":
            response = requests.post(full_url, json=data, timeout=5)
        
        status = "✅ OK" if response.status_code in [200, 201] else f"⚠️  {response.status_code}"
        return {
            "status": status,
            "code": response.status_code,
            "description": description,
            "url": url,
            "method": method
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "❌ ERROR",
            "code": 0,
            "description": description,
            "url": url,
            "method": method,
            "error": "No se pudo conectar al servidor"
        }
    except Exception as e:
        return {
            "status": "❌ ERROR",
            "code": 0,
            "description": description,
            "url": url,
            "method": method,
            "error": str(e)
        }

def main():
    print("=" * 80)
    print("PRUEBA DE ENDPOINTS - E-COMMERCE API")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    results = []
    
    # ========================
    # SYSTEM
    # ========================
    print("\n🔧 SYSTEM")
    print("-" * 80)
    
    tests = [
        ("GET", "/api/healthz/", None, "Healthcheck del sistema"),
        ("GET", "/api/schema/", None, "Schema OpenAPI"),
        ("GET", "/api/docs/", None, "Swagger UI"),
    ]
    
    for method, url, data, desc in tests:
        result = test_endpoint(method, url, data, desc)
        results.append(result)
        print(f"{result['status']} [{result['method']}] {result['url']} - {result['description']}")
    
    # ========================
    # CATALOG
    # ========================
    print("\n📦 CATALOG")
    print("-" * 80)
    
    tests = [
        ("GET", "/api/catalog/categories/", None, "Listar categorías"),
        ("GET", "/api/catalog/categories/1/", None, "Detalle de categoría"),
        ("GET", "/api/catalog/attributes/", None, "Listar atributos"),
        ("GET", "/api/catalog/attributes/1/", None, "Detalle de atributo"),
        ("GET", "/api/catalog/products/", None, "Listar productos"),
        ("GET", "/api/catalog/products/?featured=true", None, "Productos destacados"),
        ("GET", "/api/catalog/products/?category=1", None, "Productos por categoría"),
        ("GET", "/api/catalog/products/?search=camisa", None, "Búsqueda de productos"),
    ]
    
    for method, url, data, desc in tests:
        result = test_endpoint(method, url, data, desc)
        results.append(result)
        print(f"{result['status']} [{result['method']}] {result['url']} - {result['description']}")
    
    # ========================
    # INVENTORY
    # ========================
    print("\n📊 INVENTORY")
    print("-" * 80)
    
    tests = [
        ("GET", "/api/inventory/warehouses/", None, "Listar almacenes"),
        ("GET", "/api/inventory/warehouses/1/", None, "Detalle de almacén"),
        ("GET", "/api/inventory/inventory/", None, "Listar inventario"),
        ("GET", "/api/inventory/inventory/?warehouse=1", None, "Inventario por almacén"),
        ("GET", "/api/inventory/inventory/?low_stock=true", None, "Stock bajo"),
    ]
    
    for method, url, data, desc in tests:
        result = test_endpoint(method, url, data, desc)
        results.append(result)
        print(f"{result['status']} [{result['method']}] {result['url']} - {result['description']}")
    
    # ========================
    # SALES
    # ========================
    print("\n🛒 SALES")
    print("-" * 80)
    
    tests = [
        ("GET", "/api/sales/customers/", None, "Listar clientes"),
        ("GET", "/api/sales/addresses/", None, "Listar direcciones"),
        ("GET", "/api/sales/carts/", None, "Listar carritos"),
        ("GET", "/api/sales/orders/", None, "Listar pedidos"),
        ("GET", "/api/sales/orders/?status=CREATED", None, "Pedidos por estado"),
    ]
    
    for method, url, data, desc in tests:
        result = test_endpoint(method, url, data, desc)
        results.append(result)
        print(f"{result['status']} [{result['method']}] {result['url']} - {result['description']}")
    
    # ========================
    # SECURITY
    # ========================
    print("\n🔐 SECURITY")
    print("-" * 80)
    
    tests = [
        ("GET", "/api/auth/users/", None, "Listar usuarios"),
        ("GET", "/api/auth/roles/", None, "Listar roles"),
        ("GET", "/api/auth/resources/", None, "Listar recursos"),
        ("GET", "/api/auth/permissions/", None, "Listar permisos"),
    ]
    
    for method, url, data, desc in tests:
        result = test_endpoint(method, url, data, desc)
        results.append(result)
        print(f"{result['status']} [{result['method']}] {result['url']} - {result['description']}")
    
    # ========================
    # ANALYTICS
    # ========================
    print("\n📈 ANALYTICS")
    print("-" * 80)
    
    tests = [
        ("GET", "/api/analytics/sales/", None, "Listar hechos de ventas"),
        ("GET", "/api/analytics/forecasts/", None, "Listar modelos de forecast"),
        ("GET", "/api/analytics/reports/", None, "Listar reportes"),
    ]
    
    for method, url, data, desc in tests:
        result = test_endpoint(method, url, data, desc)
        results.append(result)
        print(f"{result['status']} [{result['method']}] {result['url']} - {result['description']}")
    
    # ========================
    # RESUMEN
    # ========================
    print("\n" + "=" * 80)
    print("RESUMEN")
    print("=" * 80)
    
    total = len(results)
    success = len([r for r in results if r['code'] in [200, 201]])
    errors = len([r for r in results if r['code'] not in [200, 201]])
    
    print(f"Total de pruebas: {total}")
    print(f"Exitosas: {success} ({success/total*100:.1f}%)")
    print(f"Errores: {errors} ({errors/total*100:.1f}%)")
    
    # Guardar resultados
    with open('test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total': total,
            'success': success,
            'errors': errors,
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nResultados guardados en: test_results.json")
    
    return success == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
