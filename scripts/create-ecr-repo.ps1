# scripts/create-ecr-repo.ps1
# Script para crear repositorio ECR si no existe
# Uso: .\scripts\create-ecr-repo.ps1

$ErrorActionPreference = "Stop"

# Configuración
$AWS_REGION = "us-east-1"
$ECR_REPOSITORY = "eshop-be"

Write-Host ""
Write-Host "🏗️  Creando repositorio ECR: $ECR_REPOSITORY" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Verificar si el repositorio ya existe
Write-Host "🔍 Verificando si el repositorio ya existe..." -ForegroundColor White
$RepoExists = $false

try {
    aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $RepoExists = $true
    }
} catch {
    $RepoExists = $false
}

if ($RepoExists) {
    Write-Host "   [OK] El repositorio ya existe" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📍 URL del repositorio:" -ForegroundColor Cyan
    $RepoInfo = aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION | ConvertFrom-Json
    $RepoUri = $RepoInfo.repositories[0].repositoryUri
    Write-Host "   $RepoUri" -ForegroundColor White
    Write-Host ""
    exit 0
}

# Crear el repositorio
Write-Host "   ℹ️  El repositorio no existe, creando..." -ForegroundColor Yellow
Write-Host ""

try {
    $Result = aws ecr create-repository `
        --repository-name $ECR_REPOSITORY `
        --region $AWS_REGION `
        --image-scanning-configuration scanOnPush=true `
        --encryption-configuration encryptionType=AES256 | ConvertFrom-Json
    
    Write-Host "[OK] Repositorio creado exitosamente!" -ForegroundColor Green
    Write-Host ""
    Write-Host "[*] Detalles del repositorio:" -ForegroundColor Cyan
    Write-Host "   Nombre: $($Result.repository.repositoryName)" -ForegroundColor White
    Write-Host "   URI: $($Result.repository.repositoryUri)" -ForegroundColor White
    Write-Host "   ARN: $($Result.repository.repositoryArn)" -ForegroundColor White
    Write-Host ""
    
    # Configurar lifecycle policy (opcional)
    Write-Host "[*] Configurando lifecycle policy..." -ForegroundColor White
    
    $LifecyclePolicy = @{
        rules = @(
            @{
                rulePriority = 1
                description = "Mantener solo las últimas 10 imágenes"
                selection = @{
                    tagStatus = "any"
                    countType = "imageCountMoreThan"
                    countNumber = 10
                }
                action = @{
                    type = "expire"
                }
            }
        )
    } | ConvertTo-Json -Depth 10
    
    aws ecr put-lifecycle-policy `
        --repository-name $ECR_REPOSITORY `
        --region $AWS_REGION `
        --lifecycle-policy-text $LifecyclePolicy | Out-Null
    
    Write-Host "   [OK] Lifecycle policy configurada (mantiene últimas 10 imágenes)" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
    Write-Host "[OK] CONFIGURACIÓN COMPLETADA" -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
    Write-Host ""
    Write-Host "[*] Próximo paso:" -ForegroundColor Cyan
    Write-Host "   .\scripts\deploy-ecr.ps1" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host "[X] Error al crear el repositorio" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

