# 📁 Carpeta del Proyecto

Esta carpeta contiene toda la **documentación, tests, scripts y recursos** del proyecto.

---

## 📂 **Contenido**

### 📚 `docs/` - Documentación
Toda la documentación del proyecto:
- **API_DOCUMENTATION.md** - Documentación completa de la API
- **API_QUICK_REFERENCE.md** - Referencia rápida
- **ANGULAR_FRONTEND_GUIDE.md** - Guía para Angular
- **FRONTEND_COMPONENTS_GUIDE.md** - Componentes frontend
- **DATABASE_SCHEMA.md** - Esquema de base de datos
- **PROJECT_STRUCTURE.md** - Estructura del proyecto
- Y más...

📖 **[Ver índice completo](docs/README.md)**

---

### 🧪 `tests/` - Testing
Scripts para probar el backend:
- **test_endpoints.py** - Prueba 28 endpoints
- **test_fixed.py** - Tests específicos
- **test_results.json** - Últimos resultados

🧪 **[Ver guía de tests](tests/README.md)**

---

### 🔧 `scripts/` - Scripts de Utilidad
Scripts para mantenimiento:
- **populate_db.py** - Poblar base de datos con datos demo
- **check_tables.py** - Verificar estructura de BD

🔧 **[Ver guía de scripts](scripts/README.md)**

---

### 📦 `fixtures/` - Datos de Prueba
Fixtures y datos de demostración en JSON/YAML

---

## 🚀 **Uso Rápido**

```bash
# Ver documentación
cd _project/docs
start README.md

# Ejecutar tests
python _project/tests/test_endpoints.py

# Poblar base de datos
python _project/scripts/populate_db.py

# Verificar tablas
python _project/scripts/check_tables.py
```

---

## 🎯 **¿Por qué esta carpeta?**

Para mantener la raíz del proyecto **limpia y enfocada**:
- ✅ Raíz solo tiene los módulos Django (catalog, sales, etc.)
- ✅ Toda la documentación en un solo lugar
- ✅ Tests y scripts organizados
- ✅ Más fácil de navegar y entender

---

**📍 Volver a la raíz:** [../README.md](../README.md)