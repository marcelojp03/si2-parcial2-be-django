# scripts/deploy-ecr.ps1
# Script para deploy de ecommerce-django-be a AWS ECR
# Uso: .\scripts\deploy-ecr.ps1 [tag]

param(
    [string]$Tag = ""
)

$ErrorActionPreference = "Stop"

# Configuración
$AWS_REGION = "us-east-1"
$AWS_ACCOUNT_ID = "851725478821"
$ECR_REPOSITORY = "eshop-be"
$ECR_REGISTRY = "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
$IMAGE_NAME = "$ECR_REGISTRY/$ECR_REPOSITORY"

# Tag por defecto: fecha + commit corto o 'local'
if (-not $Tag) {
    $DateTag = Get-Date -Format "yyyyMMdd"
    try {
        $GitHash = (git rev-parse --short HEAD 2>$null)
        $Tag = "$DateTag-$GitHash"
    } catch {
        $Tag = "$DateTag-local"
    }
}

Write-Host ""
Write-Host "[*] Deploy de ecommerce-django-be a AWS ECR" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "[*] Repository: $ECR_REPOSITORY" -ForegroundColor White
Write-Host "🏷️  Tag: $Tag" -ForegroundColor Yellow
Write-Host "🌍 Region: $AWS_REGION" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Verificar que Docker esté corriendo
Write-Host "🔍 Verificando Docker..." -ForegroundColor White
docker info > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[X] Error: Docker no está corriendo" -ForegroundColor Red
    Write-Host "   Por favor inicia Docker Desktop" -ForegroundColor Yellow
    exit 1
}
Write-Host "   [OK] Docker está corriendo" -ForegroundColor Green
Write-Host ""

# Verificar que AWS CLI esté instalado
Write-Host "🔍 Verificando AWS CLI..." -ForegroundColor White
aws --version > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[X] Error: AWS CLI no está instalado" -ForegroundColor Red
    Write-Host "   Descarga desde: https://aws.amazon.com/cli/" -ForegroundColor Yellow
    exit 1
}
Write-Host "   [OK] AWS CLI instalado" -ForegroundColor Green
Write-Host ""

# 1. Login a ECR
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "[*] Step 1/5: Autenticando con AWS ECR..." -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
$LoginCommand = aws ecr get-login-password --region $AWS_REGION
if ($LASTEXITCODE -ne 0) {
    Write-Host "[X] Error al obtener credenciales de ECR" -ForegroundColor Red
    Write-Host "   Verifica tus credenciales AWS con: aws configure" -ForegroundColor Yellow
    exit 1
}
$LoginCommand | docker login --username AWS --password-stdin $ECR_REGISTRY
if ($LASTEXITCODE -ne 0) {
    Write-Host "[X] Error al hacer login en ECR" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Login exitoso en ECR" -ForegroundColor Green
Write-Host ""

# 2. Build de la imagen
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🔨 Step 2/5: Construyendo imagen Docker..." -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "   Esto puede tomar varios minutos..." -ForegroundColor Yellow
Write-Host ""

docker build -t "${ECR_REPOSITORY}:${Tag}" .
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[X] Error al construir la imagen" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[OK] Imagen construida exitosamente" -ForegroundColor Green
Write-Host ""

# Taggear imagen
Write-Host "🏷️  Taggeando imagen..." -ForegroundColor White
docker tag "${ECR_REPOSITORY}:${Tag}" "${IMAGE_NAME}:${Tag}"
docker tag "${ECR_REPOSITORY}:${Tag}" "${IMAGE_NAME}:latest"
Write-Host "   [OK] Tags aplicados: ${Tag}, latest" -ForegroundColor Green
Write-Host ""

# 3. Push de la imagen con tag específico
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📤 Step 3/5: Subiendo imagen con tag ${Tag}..." -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

docker push "${IMAGE_NAME}:${Tag}"
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[X] Error al subir imagen con tag" -ForegroundColor Red
    exit 1
}
Write-Host ""
Write-Host "[OK] Imagen ${Tag} subida exitosamente" -ForegroundColor Green
Write-Host ""

# 4. Push de latest
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📤 Step 4/5: Actualizando imagen :latest..." -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

docker push "${IMAGE_NAME}:latest"
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[X] Error al subir imagen latest" -ForegroundColor Red
    exit 1
}
Write-Host ""
Write-Host "[OK] Imagen latest actualizada exitosamente" -ForegroundColor Green
Write-Host ""

# 5. Limpieza local (opcional)
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🧹 Step 5/5: Limpiando imágenes locales antiguas..." -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
docker image prune -f | Out-Null
Write-Host "[OK] Limpieza completada" -ForegroundColor Green
Write-Host ""

# Resumen final
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "[OK] DEPLOY COMPLETADO EXITOSAMENTE!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Imágenes disponibles en ECR:" -ForegroundColor Cyan
Write-Host "   🏷️  ${IMAGE_NAME}:${Tag}" -ForegroundColor Yellow
Write-Host "   🏷️  ${IMAGE_NAME}:latest" -ForegroundColor Yellow
Write-Host ""
Write-Host "[*] Comandos útiles:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   # Pull de la imagen:" -ForegroundColor White
Write-Host "   docker pull ${IMAGE_NAME}:${Tag}" -ForegroundColor Gray
Write-Host ""
Write-Host "   # Ejecutar localmente:" -ForegroundColor White
Write-Host "   docker run -p 8000:8000 --env-file .env ${IMAGE_NAME}:${Tag}" -ForegroundColor Gray
Write-Host ""
Write-Host "   # Ver en AWS Console:" -ForegroundColor White
Write-Host "   https://console.aws.amazon.com/ecr/repositories/private/${AWS_ACCOUNT_ID}/${ECR_REPOSITORY}" -ForegroundColor Gray
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""

