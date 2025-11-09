# 🔧 Scripts de Utilidad

Scripts para gestión y mantenimiento de la base de datos.

---

## 📋 **Scripts Disponibles**

### `populate_db.py` ⭐
Pobla la base de datos con datos de demostración para testing y desarrollo.

**Características:**
- Crea datos para todos los módulos
- Relaciones consistentes entre tablas
- Datos realistas y variados
- Idempotente (puede ejecutarse múltiples veces)

**Datos creados:**
- ✅ 6 categorías jerárquicas (Ropa, Electrónica, Hogar, etc.)
- ✅ 4 atributos con 19 valores (Color, Talla, Material, Estilo)
- ✅ 10+ productos con múltiples variantes
- ✅ 3 almacenes (Principal, Norte, Sur)
- ✅ Inventario por almacén
- ✅ 3 roles (Administrador, Vendedor, Cliente)
- ✅ Recursos y permisos RBAC
- ✅ Clientes de ejemplo
- ✅ Pedidos de muestra

**Ejecución:**
```bash
# Asegúrate de tener las migraciones aplicadas
python manage.py migrate

# Ejecutar el script
python scripts/populate_db.py
```

**Salida esperada:**
```
🚀 Iniciando población de la base de datos...

📦 Creando Categorías...
✅ Categorías creadas: 6

🎨 Creando Atributos y Valores...
✅ Atributos creados: 4
✅ Valores de atributos creados: 19

🛍️ Creando Productos y Variantes...
✅ Productos creados: 10
✅ Variantes creadas: 35

🏢 Creando Almacenes...
✅ Almacenes creados: 3

📊 Creando Inventario...
✅ Registros de inventario creados: 105

🔐 Creando Roles y Permisos...
✅ Roles creados: 3
✅ Recursos creados: 10
✅ Permisos asignados

👥 Creando Clientes...
✅ Clientes creados: 5

✨ ¡Base de datos poblada exitosamente!
```

---

### `check_tables.py`
Verifica la estructura de tablas en la base de datos.

**Características:**
- Lista todas las tablas del schema
- Cuenta registros por tabla
- Identifica tablas vacías
- Valida estructura esperada

**Ejecución:**
```bash
python scripts/check_tables.py
```

**Salida esperada:**
```
🔍 Verificando estructura de la base de datos...

Schema: si2-ecommmerce

📋 TABLAS ENCONTRADAS (34 tablas):
------------------------------------------------------------
catalog_category                    6 registros
catalog_product                    10 registros
catalog_productvariant             35 registros
catalog_attribute                   4 registros
catalog_attributevalue             19 registros
...

✅ Base de datos verificada correctamente
```

---

## 🎯 **Casos de Uso**

### 1. **Primer Setup del Proyecto**
```bash
# 1. Aplicar migraciones
python manage.py migrate

# 2. Crear superusuario
python manage.py createsuperuser

# 3. Poblar con datos demo
python scripts/populate_db.py

# 4. Verificar estructura
python scripts/check_tables.py

# 5. Iniciar servidor
python manage.py runserver
```

### 2. **Reset de Datos de Prueba**
```bash
# Limpiar base de datos (CUIDADO en producción)
python manage.py flush --no-input

# Poblar nuevamente
python scripts/populate_db.py
```

### 3. **Verificar Estado de la Base de Datos**
```bash
# Ver tablas y registros
python scripts/check_tables.py

# Ver migraciones aplicadas
python manage.py showmigrations
```

---

## 🔧 **Crear Nuevos Scripts**

### Plantilla para nuevos scripts:
```python
#!/usr/bin/env python
"""
Script para [propósito del script]

Uso:
    python scripts/mi_script.py [argumentos]
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

# Imports después del setup
from catalog.models import Product
from sales.models import Order

def main():
    """Función principal del script"""
    print("🚀 Iniciando script...")
    
    try:
        # Tu lógica aquí
        pass
        
        print("✅ Script completado exitosamente")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 📊 **Scripts Útiles Adicionales (Futuro)**

### `backup_db.py` (Pendiente)
Crea backup de la base de datos.

### `migrate_data.py` (Pendiente)
Migración de datos desde sistemas legacy.

### `generate_reports.py` (Pendiente)
Genera reportes automáticos del sistema.

### `cleanup_old_data.py` (Pendiente)
Limpia datos antiguos según políticas de retención.

---

## ⚠️ **Precauciones**

### **Scripts Destructivos**
Algunos comandos pueden eliminar datos:
```bash
# ⚠️ PELIGROSO - Elimina todos los datos
python manage.py flush

# ⚠️ PELIGROSO - Deshace migraciones
python manage.py migrate app_name zero
```

### **Recomendaciones:**
1. ✅ Hacer backup antes de scripts destructivos
2. ✅ Probar en ambiente de desarrollo primero
3. ✅ Leer el código del script antes de ejecutar
4. ✅ Verificar conexión a la base de datos correcta

---

## 🐳 **Scripts para Docker (Futuro)**

```bash
# docker-compose.yml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ecommerce
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      
  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    depends_on:
      - db
```

---

## 📞 **Troubleshooting**

### Error: "django.setup() already called"
```python
# Solución: No importar modelos antes de django.setup()
# ✅ Correcto:
django.setup()
from catalog.models import Product

# ❌ Incorrecto:
from catalog.models import Product
django.setup()
```

### Error: "No such table"
```bash
# Solución: Aplicar migraciones
python manage.py migrate
```

### Error: "Connection refused"
```bash
# Solución: Verificar variables de entorno
cat .env

# Verificar conexión a DB
python manage.py dbshell
```

---

**🎉 Usa estos scripts para mantener tu base de datos en óptimas condiciones.**