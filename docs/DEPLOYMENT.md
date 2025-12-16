# Docker & AWS ECR Deployment Guide

## Docker Files

### Available Dockerfiles:

1. **`Dockerfile`** - Development
   - Uses Django `runserver`
   - Ideal for testing
   
2. **`Dockerfile.prod`** - Production
   - Uses Gunicorn (4 workers, 2 threads)
   - Non-root user (security)
   - Healthcheck included

## Deploy to AWS ECR

### Prerequisitos

- Docker Desktop instalado y corriendo
- AWS CLI instalado y configurado
- Credenciales AWS configuradas (`aws configure`)

### Uso del script de deploy

```powershell
# Deploy con tag automático (fecha + git hash)
.\scripts\deploy-ecr.ps1

# Deploy con tag personalizado
.\scripts\deploy-ecr.ps1 -Tag "v1.0.0"
.\scripts\deploy-ecr.ps1 -Tag "production"
.\scripts\deploy-ecr.ps1 -Tag "staging"
```

### ¿Qué hace el script?

1. Verifica que Docker y AWS CLI estén instalados
2. Se autentica con AWS ECR
3. 🔨 Construye la imagen Docker
4. 🏷️ Aplica tags (específico + latest)
5. 📤 Sube la imagen a ECR
6. 🧹 Limpia imágenes locales antiguas

### Configuración ECR

```powershell
AWS_REGION = "us-east-1"
AWS_ACCOUNT_ID = "851725478821"
ECR_REPOSITORY = "eshop-be"
```

## 🐳 Testing local con Docker

### Build local

```powershell
# Desarrollo
docker build -t eshop-be:dev .

# Producción
docker build -f Dockerfile.prod -t eshop-be:prod .
```

### Ejecutar localmente

```powershell
# Con variables de entorno desde .env
docker run -p 8000:8000 --env-file .env eshop-be:dev

# Con variables específicas
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  -e AWS_ACCESS_KEY_ID="your-key" \
  -e AWS_SECRET_ACCESS_KEY="your-secret" \
  eshop-be:dev
```

### Pull desde ECR

```powershell
# Autenticarse
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 851725478821.dkr.ecr.us-east-1.amazonaws.com

# Pull de la imagen
docker pull 851725478821.dkr.ecr.us-east-1.amazonaws.com/eshop-be:latest

# Ejecutar
docker run -p 8000:8000 --env-file .env 851725478821.dkr.ecr.us-east-1.amazonaws.com/eshop-be:latest
```

## Variables de entorno necesarias

Asegúrate de que tu `.env` o las variables de entorno contengan:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# AWS S3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1

# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=.amazonaws.com,localhost,127.0.0.1

# Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Troubleshooting

### Error: Docker no está corriendo
```
Solución: Inicia Docker Desktop
```

### Error: AWS CLI no instalado
```
Solución: Descarga desde https://aws.amazon.com/cli/
```

### Error: Credenciales AWS inválidas
```powershell
# Configura tus credenciales
aws configure

# Verifica
aws sts get-caller-identity
```

### Error: No se puede conectar a ECR
```powershell
# Verifica que el repositorio existe
aws ecr describe-repositories --repository-names eshop-be --region us-east-1

# Si no existe, créalo
aws ecr create-repository --repository-name eshop-be --region us-east-1
```

## Comandos útiles

```powershell
# Ver imágenes locales
docker images | Select-String "eshop-be"

# Ver imágenes en ECR
aws ecr list-images --repository-name eshop-be --region us-east-1

# Eliminar imagen local
docker rmi eshop-be:dev

# Logs del contenedor
docker logs -f <container-id>

# Entrar al contenedor
docker exec -it <container-id> bash

# Ver tamaño de imagen
docker images eshop-be --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
```

## 🌐 URLs de AWS Console

- **ECR Repository**: https://console.aws.amazon.com/ecr/repositories/private/851725478821/eshop-be
- **ECS Clusters**: https://console.aws.amazon.com/ecs/v2/clusters
- **CloudWatch Logs**: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups

## Notas

- Las imágenes en ECR se mantienen indefinidamente (configura lifecycle policies si necesitas limpieza automática)
- El tag `latest` siempre apunta a la última imagen subida
- Los tags con fecha+hash permiten rollback fácil
- Para producción, usa `Dockerfile.prod` que incluye Gunicorn y mejores prácticas de seguridad
