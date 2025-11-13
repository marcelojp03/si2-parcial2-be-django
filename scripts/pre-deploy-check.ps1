# scripts/pre-deploy-check.ps1
# Script de verificación pre-deploy
# Verifica que todo esté listo para deploy a ECR

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "🔍 PRE-DEPLOY CHECK - ecommerce-django-be" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

$AllChecksPass = $true

# Check 1: Docker
Write-Host "1️⃣  Verificando Docker..." -ForegroundColor White
docker info > $null 2>&1
if ($LASTEXITCODE -eq 0) {
    $DockerVersion = docker --version
    Write-Host "   ✅ Docker instalado: $DockerVersion" -ForegroundColor Green
} else {
    Write-Host "   ❌ Docker no está corriendo" -ForegroundColor Red
    $AllChecksPass = $false
}
Write-Host ""

# Check 2: AWS CLI
Write-Host "2️⃣  Verificando AWS CLI..." -ForegroundColor White
aws --version > $null 2>&1
if ($LASTEXITCODE -eq 0) {
    $AwsVersion = aws --version
    Write-Host "   ✅ AWS CLI instalado: $AwsVersion" -ForegroundColor Green
} else {
    Write-Host "   ❌ AWS CLI no está instalado" -ForegroundColor Red
    $AllChecksPass = $false
}
Write-Host ""

# Check 3: AWS Credentials
Write-Host "3️⃣  Verificando credenciales AWS..." -ForegroundColor White
try {
    $Identity = aws sts get-caller-identity 2>&1 | ConvertFrom-Json
    Write-Host "   ✅ Credenciales válidas" -ForegroundColor Green
    Write-Host "      Account: $($Identity.Account)" -ForegroundColor Gray
    Write-Host "      User: $($Identity.Arn)" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ Credenciales AWS no configuradas o inválidas" -ForegroundColor Red
    Write-Host "      Ejecuta: aws configure" -ForegroundColor Yellow
    $AllChecksPass = $false
}
Write-Host ""

# Check 4: Dockerfile existe
Write-Host "4️⃣  Verificando Dockerfile..." -ForegroundColor White
if (Test-Path "Dockerfile") {
    Write-Host "   ✅ Dockerfile encontrado" -ForegroundColor Green
} else {
    Write-Host "   ❌ Dockerfile no encontrado" -ForegroundColor Red
    $AllChecksPass = $false
}
Write-Host ""

# Check 5: requirements.txt existe
Write-Host "5️⃣  Verificando requirements.txt..." -ForegroundColor White
if (Test-Path "requirements.txt") {
    $ReqCount = (Get-Content "requirements.txt" | Where-Object { $_ -match '\S' }).Count
    Write-Host "   ✅ requirements.txt encontrado ($ReqCount paquetes)" -ForegroundColor Green
} else {
    Write-Host "   ❌ requirements.txt no encontrado" -ForegroundColor Red
    $AllChecksPass = $false
}
Write-Host ""

# Check 6: .dockerignore existe
Write-Host "6️⃣  Verificando .dockerignore..." -ForegroundColor White
if (Test-Path ".dockerignore") {
    Write-Host "   ✅ .dockerignore encontrado" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  .dockerignore no encontrado (recomendado)" -ForegroundColor Yellow
}
Write-Host ""

# Check 7: ECR Repository
Write-Host "7️⃣  Verificando repositorio ECR..." -ForegroundColor White
$ECR_REPOSITORY = "eshop-be"
$AWS_REGION = "us-east-1"
try {
    aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Repositorio ECR existe: $ECR_REPOSITORY" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Repositorio ECR no existe" -ForegroundColor Yellow
        Write-Host "      Ejecuta: .\scripts\create-ecr-repo.ps1" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️  No se pudo verificar repositorio ECR" -ForegroundColor Yellow
}
Write-Host ""

# Check 8: Git status
Write-Host "8️⃣  Verificando Git..." -ForegroundColor White
try {
    $GitStatus = git status --porcelain 2>&1
    $GitBranch = git rev-parse --abbrev-ref HEAD 2>&1
    
    if ($GitStatus) {
        Write-Host "   ⚠️  Tienes cambios sin commitear en branch: $GitBranch" -ForegroundColor Yellow
        Write-Host "      Considera hacer commit antes del deploy" -ForegroundColor Yellow
    } else {
        Write-Host "   ✅ Working tree limpio en branch: $GitBranch" -ForegroundColor Green
    }
} catch {
    Write-Host "   ℹ️  No es un repositorio Git" -ForegroundColor Gray
}
Write-Host ""

# Check 9: Espacio en disco
Write-Host "9️⃣  Verificando espacio en disco..." -ForegroundColor White
$Drive = (Get-Location).Drive.Name
$DiskInfo = Get-PSDrive $Drive
$FreeGB = [math]::Round($DiskInfo.Free / 1GB, 2)
if ($FreeGB -gt 5) {
    Write-Host "   ✅ Espacio disponible: ${FreeGB} GB" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Poco espacio disponible: ${FreeGB} GB" -ForegroundColor Yellow
}
Write-Host ""

# Resumen final
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

if ($AllChecksPass) {
    Write-Host "✅ TODAS LAS VERIFICACIONES PASARON" -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Listo para deploy. Ejecuta:" -ForegroundColor Cyan
    Write-Host "   .\scripts\deploy-ecr.ps1" -ForegroundColor White
    Write-Host ""
    exit 0
} else {
    Write-Host "❌ ALGUNAS VERIFICACIONES FALLARON" -ForegroundColor Red
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Red
    Write-Host ""
    Write-Host "⚠️  Por favor corrige los errores antes del deploy" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
