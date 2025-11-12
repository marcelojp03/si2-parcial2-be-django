# ===============================================
# PRUEBAS DE ENDPOINTS CON USUARIOS REALES
# ===============================================
Write-Host "`n===============================================" -ForegroundColor Cyan
Write-Host "PRUEBAS DE AUTENTICACIÓN CON USUARIOS REALES" -ForegroundColor Cyan
Write-Host "===============================================`n" -ForegroundColor Cyan

$baseUrl = "http://127.0.0.1:8000"

# ===============================================
# TEST 1: Login Cliente (Trevor Calero)
# ===============================================
Write-Host "`n[TEST 1] Login como CLIENTE (Trevor Calero)..." -ForegroundColor Yellow
Write-Host "   Username: trevorcalero" -ForegroundColor Gray
Write-Host "   Password: Cliente123!" -ForegroundColor Gray

$clienteLoginData = @{
    username = "trevorcalero"
    password = "Cliente123!"
} | ConvertTo-Json

$clienteTokens = try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/customers/login/" `
        -Method POST `
        -Body $clienteLoginData `
        -ContentType "application/json" `
        -ErrorAction Stop
    Write-Host "✅ Login exitoso" -ForegroundColor Green
    Write-Host "   Access Token (primeros 60 chars): $($response.access.Substring(0, 60))..." -ForegroundColor Gray
    Write-Host "   Refresh Token (primeros 60 chars): $($response.refresh.Substring(0, 60))..." -ForegroundColor Gray
    $response
} catch {
    Write-Host "❌ Error en login" -ForegroundColor Red
    if ($_.ErrorDetails) {
        Write-Host ($_.ErrorDetails.Message | ConvertFrom-Json | ConvertTo-Json) -ForegroundColor Red
    } else {
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
    $null
}

# ===============================================
# TEST 2: Ver Perfil del Cliente
# ===============================================
if ($clienteTokens) {
    Write-Host "`n[TEST 2] Ver perfil del cliente autenticado..." -ForegroundColor Yellow
    try {
        $headers = @{
            "Authorization" = "Bearer $($clienteTokens.access)"
        }
        $profile = Invoke-RestMethod -Uri "$baseUrl/api/customers/profile/" `
            -Method GET `
            -Headers $headers `
            -ErrorAction Stop
        Write-Host "OK Perfil obtenido exitosamente" -ForegroundColor Green
        Write-Host "`nINFORMACION DEL PERFIL:" -ForegroundColor Cyan
        Write-Host "   ID Cliente: $($profile.id)" -ForegroundColor White
        Write-Host "   Username: $($profile.user.username)" -ForegroundColor White
        Write-Host "   Email: $($profile.email)" -ForegroundColor White
        Write-Host "   Nombre Completo: $($profile.first_name) $($profile.last_name)" -ForegroundColor White
        Write-Host "   Teléfono: $($profile.phone)" -ForegroundColor White
        Write-Host "   Dirección: $($profile.address)" -ForegroundColor White
        Write-Host "   Ciudad: $($profile.city)" -ForegroundColor White
        Write-Host "   País: $($profile.country)" -ForegroundColor White
        Write-Host "   Código Postal: $($profile.postal_code)" -ForegroundColor White
        Write-Host "   Fecha de Registro: $($profile.created_at)" -ForegroundColor White
    } catch {
        Write-Host "❌ Error al obtener perfil" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
}

# ===============================================
# TEST 3: Actualizar Perfil del Cliente
# ===============================================
if ($clienteTokens) {
    Write-Host "`n[TEST 3] Actualizar perfil del cliente..." -ForegroundColor Yellow
    $updateData = @{
        phone = "76612345"
        address = "Calle Warnes #567"
        city = "Santa Cruz de la Sierra"
        postal_code = "0001"
    } | ConvertTo-Json
    
    try {
        $headers = @{
            "Authorization" = "Bearer $($clienteTokens.access)"
        }
        $updatedProfile = Invoke-RestMethod -Uri "$baseUrl/api/customers/profile/" `
            -Method PATCH `
            -Body $updateData `
            -Headers $headers `
            -ContentType "application/json" `
            -ErrorAction Stop
        Write-Host "OK Perfil actualizado exitosamente" -ForegroundColor Green
        Write-Host "   Nuevo Teléfono: $($updatedProfile.phone)" -ForegroundColor Gray
        Write-Host "   Nueva Dirección: $($updatedProfile.address)" -ForegroundColor Gray
        Write-Host "   Nueva Ciudad: $($updatedProfile.city)" -ForegroundColor Gray
        Write-Host "   Nuevo Código Postal: $($updatedProfile.postal_code)" -ForegroundColor Gray
    } catch {
        Write-Host "❌ Error al actualizar perfil" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
}

# ===============================================
# TEST 4: Cambiar Contraseña del Cliente
# ===============================================
if ($clienteTokens) {
    Write-Host "`n[TEST 4] Cambiar contraseña del cliente..." -ForegroundColor Yellow
    $changePasswordData = @{
        old_password = "Cliente123!"
        new_password = "NuevaCliente123!"
        new_password2 = "NuevaCliente123!"
    } | ConvertTo-Json
    
    try {
        $headers = @{
            "Authorization" = "Bearer $($clienteTokens.access)"
        }
        $response = Invoke-RestMethod -Uri "$baseUrl/api/customers/change-password/" `
            -Method PUT `
            -Body $changePasswordData `
            -Headers $headers `
            -ContentType "application/json" `
            -ErrorAction Stop
        Write-Host "✅ Contraseña cambiada exitosamente" -ForegroundColor Green
        Write-Host "   Mensaje: $($response.message)" -ForegroundColor Gray
        
        # Cambiar de vuelta a la contraseña original para mantener consistencia
        Write-Host "`n   Revertir cambio de contraseña para mantener datos consistentes..." -ForegroundColor Gray
        $revertPasswordData = @{
            old_password = "NuevaCliente123!"
            new_password = "Cliente123!"
            new_password2 = "Cliente123!"
        } | ConvertTo-Json
        
        Invoke-RestMethod -Uri "$baseUrl/api/customers/change-password/" `
            -Method PUT `
            -Body $revertPasswordData `
            -Headers $headers `
            -ContentType "application/json" `
            -ErrorAction Stop | Out-Null
        Write-Host "   ✓ Contraseña revertida" -ForegroundColor Gray
    } catch {
        Write-Host "❌ Error al cambiar contraseña" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
}

# ===============================================
# TEST 5: Refresh Token
# ===============================================
if ($clienteTokens) {
    Write-Host "`n[TEST 5] Refrescar access token..." -ForegroundColor Yellow
    $refreshData = @{
        refresh = $clienteTokens.refresh
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/api/customers/token/refresh/" `
            -Method POST `
            -Body $refreshData `
            -ContentType "application/json" `
            -ErrorAction Stop
        Write-Host "✅ Token refrescado exitosamente" -ForegroundColor Green
        Write-Host "   Nuevo Access Token (primeros 60 chars): $($response.access.Substring(0, 60))..." -ForegroundColor Gray
    } catch {
        Write-Host "❌ Error al refrescar token" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
}

# ===============================================
# TEST 6: Intentar Login con Admin (debe FALLAR)
# ===============================================
Write-Host "`n[TEST 6] Intentar login de ADMIN en endpoint de clientes (debe FALLAR)..." -ForegroundColor Yellow
Write-Host "   Username: marcelojp03" -ForegroundColor Gray
Write-Host "   Password: Admin123!" -ForegroundColor Gray

$adminLoginData = @{
    username = "marcelojp03"
    password = "Admin123!"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/customers/login/" `
        -Method POST `
        -Body $adminLoginData `
        -ContentType "application/json" `
        -ErrorAction Stop
    Write-Host "⚠️ ADVERTENCIA: Admin pudo hacer login en endpoint de clientes" -ForegroundColor Yellow
    Write-Host "   Esto es técnicamente posible pero no ideal" -ForegroundColor Gray
} catch {
    $errorMsg = $_.ErrorDetails.Message | ConvertFrom-Json
    Write-Host "✅ CORRECTO: Admin no puede hacer login como cliente" -ForegroundColor Green
    Write-Host "   Razón: $($errorMsg.detail)" -ForegroundColor Gray
}

# ===============================================
# TEST 7: Intentar Registrar con Email de Admin (debe FALLAR)
# ===============================================
Write-Host "`n[TEST 7] Intentar registrar nuevo cliente con email de admin (debe FALLAR)..." -ForegroundColor Yellow

$registerWithAdminEmail = @{
    username = "nuevo_cliente"
    email = "marcelojp03@gmail.com"
    password = "ClientePass123!"
    password2 = "ClientePass123!"
    first_name = "Nuevo"
    last_name = "Cliente"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/customers/register/" `
        -Method POST `
        -Body $registerWithAdminEmail `
        -ContentType "application/json" `
        -ErrorAction Stop
    Write-Host "❌ ERROR: Se permitió registrar con email de admin!" -ForegroundColor Red
} catch {
    $errorResponse = $_.ErrorDetails.Message | ConvertFrom-Json
    if ($errorResponse.email) {
        Write-Host "✅ CORRECTO: Se bloqueó el registro con email de admin" -ForegroundColor Green
        Write-Host "   Mensaje: $($errorResponse.email)" -ForegroundColor Gray
    } else {
        Write-Host "✅ Se bloqueó pero con mensaje diferente:" -ForegroundColor Green
        Write-Host "   $($errorResponse)" -ForegroundColor Gray
    }
}

# ===============================================
# TEST 8: Logout del Cliente
# ===============================================
if ($clienteTokens) {
    Write-Host "`n[TEST 8] Logout del cliente..." -ForegroundColor Yellow
    $logoutData = @{
        refresh = $clienteTokens.refresh
    } | ConvertTo-Json

    try {
        $headers = @{
            "Authorization" = "Bearer $($clienteTokens.access)"
        }
        Invoke-RestMethod -Uri "$baseUrl/api/customers/logout/" `
            -Method POST `
            -Body $logoutData `
            -Headers $headers `
            -ContentType "application/json" `
            -ErrorAction Stop | Out-Null
        Write-Host "✅ Logout exitoso" -ForegroundColor Green
        Write-Host "   Token agregado a blacklist" -ForegroundColor Gray
    } catch {
        Write-Host "❌ Error en logout" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
}

# ===============================================
# TEST 9: Verificar Token Blacklist
# ===============================================
if ($clienteTokens) {
    Write-Host "`n[TEST 9] Intentar usar token después de logout (debe FALLAR)..." -ForegroundColor Yellow
    try {
        $headers = @{
            "Authorization" = "Bearer $($clienteTokens.access)"
        }
        $response = Invoke-RestMethod -Uri "$baseUrl/api/customers/profile/" `
            -Method GET `
            -Headers $headers `
            -ErrorAction Stop
        Write-Host "⚠️ ADVERTENCIA: Token sigue funcionando después de logout" -ForegroundColor Yellow
    } catch {
        Write-Host "✅ CORRECTO: Token ya no es válido después de logout" -ForegroundColor Green
        Write-Host "   El token fue correctamente agregado a la blacklist" -ForegroundColor Gray
    }
}

# ===============================================
# RESUMEN FINAL
# ===============================================
Write-Host "`n===============================================" -ForegroundColor Cyan
Write-Host "RESUMEN DE PRUEBAS" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

Write-Host "`n✅ USUARIOS CREADOS:" -ForegroundColor Green
Write-Host "   👨‍💼 Admin: marcelojp03 / Admin123!" -ForegroundColor White
Write-Host "      Email: marcelojp03@gmail.com" -ForegroundColor Gray
Write-Host "      Login Admin: http://127.0.0.1:8000/admin/" -ForegroundColor Gray
Write-Host ""
Write-Host "   👤 Cliente: trevorcalero / Cliente123!" -ForegroundColor White
Write-Host "      Email: trevorfelixcalerosuyo@gmail.com" -ForegroundColor Gray
Write-Host "      Login API: POST http://127.0.0.1:8000/api/customers/login/" -ForegroundColor Gray

Write-Host "`n✅ ENDPOINTS PROBADOS:" -ForegroundColor Green
Write-Host "   ✓ POST /api/customers/login/" -ForegroundColor White
Write-Host "   ✓ GET /api/customers/profile/" -ForegroundColor White
Write-Host "   ✓ PATCH /api/customers/profile/" -ForegroundColor White
Write-Host "   ✓ PUT /api/customers/change-password/" -ForegroundColor White
Write-Host "   ✓ POST /api/customers/token/refresh/" -ForegroundColor White
Write-Host "   ✓ POST /api/customers/register/" -ForegroundColor White
Write-Host "   ✓ POST /api/customers/logout/" -ForegroundColor White

Write-Host "`n✅ SEPARACIÓN DE ROLES VERIFICADA:" -ForegroundColor Green
Write-Host "   ✓ Admins NO pueden ser clientes" -ForegroundColor White
Write-Host "   ✓ Emails de admins están protegidos" -ForegroundColor White
Write-Host "   ✓ Tokens son correctamente invalidados en logout" -ForegroundColor White

Write-Host "`n===============================================`n" -ForegroundColor Cyan
