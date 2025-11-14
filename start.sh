#!/bin/bash
# Script de inicio para App Runner

set -e

echo "🚀 Iniciando aplicación Django..."

# Ejecutar migraciones
echo "📦 Ejecutando migraciones de base de datos..."
python manage.py migrate --noinput

# Colectar archivos estáticos
echo "📁 Colectando archivos estáticos..."
python manage.py collectstatic --noinput

# Iniciar Gunicorn
echo "🌐 Iniciando servidor Gunicorn en puerto 1112..."
exec gunicorn ecommerce.wsgi:application \
    --bind 0.0.0.0:1112 \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
