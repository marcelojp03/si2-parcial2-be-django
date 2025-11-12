# Test de autenticación con usuarios reales
$baseUrl = "http://127.0.0.1:8000"

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "PRUEBAS CON USUARIOS REALES" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# TEST 1: Login Cliente
Write-Host "[TEST 1] Login como cliente Trevor Calero..." -ForegroundColor Yellow

$loginData = @{
    username = "trevorcalero"
    password = "Cliente123!"
} | ConvertTo-Json

try {
    $tokens = Invoke-RestMethod -Uri "$baseUrl/api/customers/login/" `
        -Method POST `
        -Body $loginData `
        -ContentType "application/json"
    
    Write-Host "OK Login exitoso" -ForegroundColor Green
    Write-Host "Access token: $($tokens.access.Substring(0, 50))..." -ForegroundColor Gray
    
    # TEST 2: Ver perfil
    Write-Host "`n[TEST 2] Ver perfil..." -ForegroundColor Yellow
    $headers = @{ "Authorization" = "Bearer $($tokens.access)" }
    
    $profile = Invoke-RestMethod -Uri "$baseUrl/api/customers/profile/" `
        -Method GET `
        -Headers $headers
    
    Write-Host "OK Perfil obtenido" -ForegroundColor Green
    Write-Host "ID: $($profile.id)" -ForegroundColor White
    Write-Host "Username: $($profile.user.username)" -ForegroundColor White
    Write-Host "Email: $($profile.email)" -ForegroundColor White
    Write-Host "Nombre: $($profile.first_name) $($profile.last_name)" -ForegroundColor White
    Write-Host "Telefono: $($profile.phone)" -ForegroundColor White
    Write-Host "Ciudad: $($profile.city), $($profile.country)" -ForegroundColor White
    
    # TEST 3: Actualizar perfil
    Write-Host "`n[TEST 3] Actualizar telefono..." -ForegroundColor Yellow
    $updateData = @{ phone = "77788899" } | ConvertTo-Json
    
    $updated = Invoke-RestMethod -Uri "$baseUrl/api/customers/profile/" `
        -Method PATCH `
        -Body $updateData `
        -Headers $headers `
        -ContentType "application/json"
    
    Write-Host "OK Telefono actualizado: $($updated.phone)" -ForegroundColor Green
    
    # TEST 4: Refresh token
    Write-Host "`n[TEST 4] Refresh token..." -ForegroundColor Yellow
    $refreshData = @{ refresh = $tokens.refresh } | ConvertTo-Json
    
    $newToken = Invoke-RestMethod -Uri "$baseUrl/api/customers/token/refresh/" `
        -Method POST `
        -Body $refreshData `
        -ContentType "application/json"
    
    Write-Host "OK Token refrescado: $($newToken.access.Substring(0, 50))..." -ForegroundColor Green
    
    # TEST 5: Logout
    Write-Host "`n[TEST 5] Logout..." -ForegroundColor Yellow
    $logoutData = @{ refresh = $tokens.refresh } | ConvertTo-Json
    
    Invoke-RestMethod -Uri "$baseUrl/api/customers/logout/" `
        -Method POST `
        -Body $logoutData `
        -Headers $headers `
        -ContentType "application/json" | Out-Null
    
    Write-Host "OK Logout exitoso" -ForegroundColor Green
    
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails) {
        Write-Host $_.ErrorDetails.Message -ForegroundColor Red
    }
}

# TEST 6: Intentar login con admin (debe fallar)
Write-Host "`n[TEST 6] Intentar login con admin (debe fallar)..." -ForegroundColor Yellow
$adminLogin = @{
    username = "marcelojp03"
    password = "Admin123!"
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "$baseUrl/api/customers/login/" `
        -Method POST `
        -Body $adminLogin `
        -ContentType "application/json" | Out-Null
    Write-Host "ADVERTENCIA: Admin pudo hacer login" -ForegroundColor Yellow
} catch {
    Write-Host "OK Admin no puede hacer login como cliente" -ForegroundColor Green
}

# TEST 7: Intentar registrar con email de admin
Write-Host "`n[TEST 7] Intentar registrar con email de admin..." -ForegroundColor Yellow
$badRegister = @{
    username = "test_user"
    email = "marcelojp03@gmail.com"
    password = "Test123!"
    password2 = "Test123!"
    first_name = "Test"
    last_name = "User"
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "$baseUrl/api/customers/register/" `
        -Method POST `
        -Body $badRegister `
        -ContentType "application/json" | Out-Null
    Write-Host "ERROR: Se permitio registrar con email de admin" -ForegroundColor Red
} catch {
    Write-Host "OK Email de admin esta protegido" -ForegroundColor Green
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "RESUMEN" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "`nUSUARIOS CREADOS:" -ForegroundColor White
Write-Host "  Admin: marcelojp03 / Admin123!" -ForegroundColor Gray
Write-Host "  Email: marcelojp03@gmail.com" -ForegroundColor Gray
Write-Host "  Panel: http://127.0.0.1:8000/admin/`n" -ForegroundColor Gray
Write-Host "  Cliente: trevorcalero / Cliente123!" -ForegroundColor Gray
Write-Host "  Email: trevorfelixcalerosuyo@gmail.com" -ForegroundColor Gray
Write-Host "  API: http://127.0.0.1:8000/api/customers/login/" -ForegroundColor Gray
Write-Host "`n============================================`n" -ForegroundColor Cyan
