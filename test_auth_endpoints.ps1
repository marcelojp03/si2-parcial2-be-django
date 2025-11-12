# Test de endpoints de autenticación de clientes

Write-Host "`n===============================================" -ForegroundColor Cyan
Write-Host "PRUEBAS DE AUTENTICACIÓN - SEPARACIÓN DE ROLES" -ForegroundColor Cyan
Write-Host "===============================================`n" -ForegroundColor Cyan

$baseUrl = "http://127.0.0.1:8000"

# TEST 1: Registrar un cliente nuevo (debe funcionar)
Write-Host "`n[TEST 1] Registrar un cliente nuevo..." -ForegroundColor Yellow
$registerData = @{
    username = "cliente_prueba"
    email = "cliente@ejemplo.com"
    password = "ClientePass123!"
    password2 = "ClientePass123!"
    first_name = "Juan"
    last_name = "Pérez"
    phone = "75512345"
    city = "Santa Cruz"
    country = "Bolivia"
} | ConvertTo-Json

$response = try {
    Invoke-RestMethod -Uri "$baseUrl/api/customers/register/" `
        -Method POST `
        -Body $registerData `
        -ContentType "application/json" `
        -ErrorAction Stop
    Write-Host "✅ Cliente registrado exitosamente" -ForegroundColor Green
    Write-Host "   Username: $($response.username)" -ForegroundColor Gray
    Write-Host "   Email: $($response.email)" -ForegroundColor Gray
    Write-Host "   Nombre: $($response.first_name) $($response.last_name)" -ForegroundColor Gray
    $response
} catch {
    Write-Host "❌ Error al registrar cliente" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# TEST 2: Login con el cliente registrado
Write-Host "`n[TEST 2] Login con el cliente registrado..." -ForegroundColor Yellow
$loginData = @{
    username = "cliente_prueba"
    password = "ClientePass123!"
} | ConvertTo-Json

$tokens = try {
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/api/customers/login/" `
        -Method POST `
        -Body $loginData `
        -ContentType "application/json" `
        -ErrorAction Stop
    Write-Host "✅ Login exitoso" -ForegroundColor Green
    Write-Host "   Access Token (primeros 50 chars): $($loginResponse.access.Substring(0, 50))..." -ForegroundColor Gray
    Write-Host "   Refresh Token (primeros 50 chars): $($loginResponse.refresh.Substring(0, 50))..." -ForegroundColor Gray
    $loginResponse
} catch {
    Write-Host "❌ Error en login" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# TEST 3: Ver perfil del cliente
if ($tokens) {
    Write-Host "`n[TEST 3] Ver perfil del cliente autenticado..." -ForegroundColor Yellow
    try {
        $headers = @{
            "Authorization" = "Bearer $($tokens.access)"
        }
        $profile = Invoke-RestMethod -Uri "$baseUrl/api/customers/profile/" `
            -Method GET `
            -Headers $headers `
            -ErrorAction Stop
        Write-Host "✅ Perfil obtenido exitosamente" -ForegroundColor Green
        Write-Host "   ID: $($profile.id)" -ForegroundColor Gray
        Write-Host "   Usuario: $($profile.user.username)" -ForegroundColor Gray
        Write-Host "   Email: $($profile.email)" -ForegroundColor Gray
        Write-Host "   Nombre: $($profile.first_name) $($profile.last_name)" -ForegroundColor Gray
        Write-Host "   Ciudad: $($profile.city), $($profile.country)" -ForegroundColor Gray
        Write-Host "   Teléfono: $($profile.phone)" -ForegroundColor Gray
    } catch {
        Write-Host "❌ Error al obtener perfil" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
}

# TEST 4: Intentar registrar con email de usuario staff (debe fallar)
Write-Host "`n[TEST 4] Intentar registrar con email de staff (debe FALLAR)..." -ForegroundColor Yellow
Write-Host "   Nota: Primero verificar si existe un usuario staff..." -ForegroundColor Gray

# Crear un usuario staff directamente en la base de datos para la prueba
Write-Host "   Creando usuario staff de prueba..." -ForegroundColor Gray
$createStaffScript = @"
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    staff_user = User.objects.create_user(
        username='admin_test',
        email='admin@ejemplo.com',
        password='AdminPass123!',
        is_staff=True
    )
    print('Staff user created')
except:
    print('Staff user already exists')
"@

& .\venv\Scripts\python.exe manage.py shell -c $createStaffScript | Out-Null

$staffRegisterData = @{
    username = "otro_cliente"
    email = "admin@ejemplo.com"  # Email del staff
    password = "ClientePass123!"
    password2 = "ClientePass123!"
    first_name = "Test"
    last_name = "User"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/customers/register/" `
        -Method POST `
        -Body $staffRegisterData `
        -ContentType "application/json" `
        -ErrorAction Stop
    Write-Host "❌ ERROR: Se permitió registrar con email de staff!" -ForegroundColor Red
} catch {
    $errorResponse = $_.ErrorDetails.Message | ConvertFrom-Json
    if ($errorResponse.email -like "*reserved*") {
        Write-Host "✅ CORRECTO: Se bloqueó el registro con email de staff" -ForegroundColor Green
        Write-Host "   Mensaje: $($errorResponse.email)" -ForegroundColor Gray
    } else {
        Write-Host "⚠️ Se bloqueó pero con mensaje diferente:" -ForegroundColor Yellow
        Write-Host "   $($_.Exception.Message)" -ForegroundColor Gray
    }
}

# TEST 5: Intentar registrar con username de usuario staff (debe fallar)
Write-Host "`n[TEST 5] Intentar registrar con username de staff (debe FALLAR)..." -ForegroundColor Yellow

$staffUsernameData = @{
    username = "admin_test"  # Username del staff
    email = "otro@ejemplo.com"
    password = "ClientePass123!"
    password2 = "ClientePass123!"
    first_name = "Test"
    last_name = "User"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/customers/register/" `
        -Method POST `
        -Body $staffUsernameData `
        -ContentType "application/json" `
        -ErrorAction Stop
    Write-Host "❌ ERROR: Se permitió registrar con username de staff!" -ForegroundColor Red
} catch {
    $errorResponse = $_.ErrorDetails.Message | ConvertFrom-Json
    if ($errorResponse.username -like "*reserved*") {
        Write-Host "✅ CORRECTO: Se bloqueó el registro con username de staff" -ForegroundColor Green
        Write-Host "   Mensaje: $($errorResponse.username)" -ForegroundColor Gray
    } else {
        Write-Host "⚠️ Se bloqueó pero con mensaje diferente:" -ForegroundColor Yellow
        Write-Host "   $($_.Exception.Message)" -ForegroundColor Gray
    }
}

# TEST 6: Logout
if ($tokens) {
    Write-Host "`n[TEST 6] Logout del cliente..." -ForegroundColor Yellow
    $logoutData = @{
        refresh = $tokens.refresh
    } | ConvertTo-Json

    try {
        $headers = @{
            "Authorization" = "Bearer $($tokens.access)"
        }
        Invoke-RestMethod -Uri "$baseUrl/api/customers/logout/" `
            -Method POST `
            -Body $logoutData `
            -Headers $headers `
            -ContentType "application/json" `
            -ErrorAction Stop | Out-Null
        Write-Host "✅ Logout exitoso" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error en logout" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
}

# Cleanup
Write-Host "`n[CLEANUP] Limpiando datos de prueba..." -ForegroundColor Yellow
$cleanupScript = @"
from django.contrib.auth import get_user_model
from customers.models import Customer
User = get_user_model()
try:
    # Eliminar cliente de prueba
    user = User.objects.get(username='cliente_prueba')
    if hasattr(user, 'customer'):
        user.customer.delete()
    user.delete()
    print('Deleted cliente_prueba')
except:
    pass
try:
    # Eliminar staff de prueba
    User.objects.get(username='admin_test').delete()
    print('Deleted admin_test')
except:
    pass
"@

& .\venv\Scripts\python.exe manage.py shell -c $cleanupScript

Write-Host "`n===============================================" -ForegroundColor Cyan
Write-Host "PRUEBAS COMPLETADAS" -ForegroundColor Cyan
Write-Host "===============================================`n" -ForegroundColor Cyan
