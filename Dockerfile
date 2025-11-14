# Dockerfile para ecommerce-django-be
# Multi-stage build para optimizar tamaño de imagen

# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar paquetes Python
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Instalar solo dependencias runtime necesarias
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias Python instaladas desde builder
COPY --from=builder /root/.local /root/.local

# Copiar código de la aplicación
COPY . .

# Asegurar que los scripts de Python estén en PATH
ENV PATH=/root/.local/bin:$PATH

# Variables de entorno para Django
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=ecommerce.settings

# Crear directorio para static files
RUN mkdir -p /app/staticfiles

# Exponer puerto configurado
EXPOSE 1112

# Usar script Python para mejor logging y manejo de errores
CMD ["python", "entrypoint.py"]
