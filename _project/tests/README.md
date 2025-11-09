# 🧪 Tests del Proyecto

Esta carpeta contiene los scripts de testing y validación del backend.

---

## 📋 **Scripts Disponibles**

### `test_endpoints.py` ⭐
Script principal de testing que valida todos los endpoints de la API.

**Características:**
- Prueba 28 endpoints diferentes
- 5 módulos: System, Catalog, Inventory, Sales, Security, Analytics
- Genera reporte detallado con resultados
- Guarda resultados en JSON
- Códigos de color para visualización rápida

**Ejecución:**
```bash
# Asegúrate de que el servidor esté corriendo en otra terminal
python manage.py runserver

# En otra terminal, ejecuta los tests
python tests/test_endpoints.py
```

**Salida esperada:**
```
================================================================================
PRUEBA DE ENDPOINTS - E-COMMERCE API
Fecha: 2025-11-09 14:07:03
================================================================================

🔧 SYSTEM
--------------------------------------------------------------------------------
✅ OK [GET] /api/healthz/ - Healthcheck del sistema
⚠️  500 [GET] /api/schema/ - Schema OpenAPI
✅ OK [GET] /api/docs/ - Swagger UI

📦 CATALOG
--------------------------------------------------------------------------------
✅ OK [GET] /api/catalog/categories/ - Listar categorías
✅ OK [GET] /api/catalog/products/ - Listar productos
...

================================================================================
RESUMEN
================================================================================
Total de pruebas: 28
Exitosas: 27 (96.4%)
Errores: 1 (3.6%)
```

### `test_fixed.py`
Script enfocado para testing de endpoints específicos que fueron corregidos.

**Uso:**
```bash
python tests/test_fixed.py
```

---

## 📊 **Resultados de Tests**

### `test_results.json`
Archivo JSON con los resultados de la última ejecución de tests.

**Estructura:**
```json
{
  "timestamp": "2025-11-09T14:07:03",
  "total_tests": 28,
  "passed": 27,
  "failed": 1,
  "modules": {
    "system": {"passed": 2, "failed": 1},
    "catalog": {"passed": 8, "failed": 0},
    ...
  },
  "details": [...]
}
```

---

## ✅ **Estado Actual de Tests**

### **Módulos con 100% de éxito:**
- ✅ **CATALOG** - 8/8 endpoints
- ✅ **INVENTORY** - 5/5 endpoints
- ✅ **SALES** - 5/5 endpoints
- ✅ **SECURITY** - 4/4 endpoints
- ✅ **ANALYTICS** - 3/3 endpoints

### **Módulos con errores:**
- ⚠️ **SYSTEM** - 2/3 endpoints
  - `/api/schema/` - Error de configuración drf-spectacular (no afecta funcionalidad)

---

## 🔧 **Agregar Nuevos Tests**

### Plantilla para nuevo endpoint:
```python
def test_new_endpoint():
    """Test para nuevo endpoint"""
    url = f"{BASE_URL}/api/module/endpoint/"
    
    try:
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ OK [GET] {url}")
            return True
        else:
            print(f"⚠️  {response.status_code} [GET] {url}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR [GET] {url} - {str(e)}")
        return False
```

---

## 🎯 **Buenas Prácticas**

1. **Ejecutar tests antes de commit:**
   ```bash
   python tests/test_endpoints.py
   ```

2. **Verificar el servidor esté corriendo:**
   ```bash
   curl http://127.0.0.1:8000/api/healthz/
   ```

3. **Revisar resultados en JSON:**
   ```bash
   cat tests/test_results.json
   ```

4. **Tests automáticos (futuro):**
   ```bash
   python manage.py test
   ```

---

## 📈 **Métricas de Calidad**

- **Cobertura actual:** 96.4% (27/28 endpoints)
- **Tiempo de ejecución:** ~5 segundos
- **Tests automáticos:** Pendiente integración CI/CD

---

## 📞 **Troubleshooting**

### Error: "Connection refused"
```bash
# Solución: Verificar que el servidor esté corriendo
python manage.py runserver
```

### Error: "Module not found"
```bash
# Solución: Activar el entorno virtual
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Tests fallan aleatoriamente
```bash
# Solución: Verificar la base de datos esté poblada
python scripts/populate_db.py
```

---

**🎉 Mantén los tests actualizados para garantizar la calidad del backend.**