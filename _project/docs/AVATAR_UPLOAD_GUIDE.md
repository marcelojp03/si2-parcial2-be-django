# Guía de Subida de Avatares

## Endpoint de Subida de Avatar

**URL:** `POST /api/customers/upload-avatar/`  
**Autenticación:** JWT Bearer Token (Required)  
**Content-Type:** `application/json`

### Descripción
Permite a usuarios autenticados (clientes y admins) subir su foto de perfil. La imagen se almacena en AWS S3 y se genera una URL firmada con validez de 7 días.

---

## Formato de la Petición

### Headers
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Body (JSON)
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "extension": "jpg"
}
```

**Campos:**
- `image` (requerido): Imagen en formato base64. Puede incluir el prefijo `data:image/{type};base64,` o solo el string base64.
- `extension` (opcional): Extensión del archivo (`jpg`, `png`, `webp`, `gif`). Por defecto: `jpg`

**Restricciones:**
- Tamaño máximo: 5MB
- Formatos soportados: JPG, PNG, WEBP, GIF

---

## Respuestas

### Éxito (200 OK)
```json
{
  "message": "Avatar uploaded successfully",
  "avatar_url": "https://si2-proyectos.s3.amazonaws.com/si2-ecommerce-images/user-8/20251111-222530_75e53f10_avatar.png?AWSAccessKeyId=...",
  "avatar_s3_bucket": "si2-proyectos",
  "avatar_s3_key": "si2-ecommerce-images/user-8/20251111-222530_75e53f10_avatar.png",
  "user": {
    "id": 8,
    "username": "trevorcalero",
    "email": "trevorfelixcalerosuyo@gmail.com",
    "first_name": "Trevor",
    "last_name": "Calero",
    "phone": "",
    "avatar": "https://si2-proyectos.s3.amazonaws.com/...",
    "avatar_s3_key": "si2-ecommerce-images/user-8/...",
    "avatar_s3_bucket": "si2-proyectos",
    "is_staff": false,
    "is_superuser": false
  }
}
```

### Errores

#### 400 Bad Request - Sin imagen
```json
{
  "error": "Image data is required"
}
```

#### 400 Bad Request - Imagen inválida
```json
{
  "error": "Invalid base64 image data: ..."
}
```

#### 400 Bad Request - Imagen muy grande
```json
{
  "error": "Image too large. Maximum size is 5MB, got 7.3MB"
}
```

#### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 500 Internal Server Error - Fallo en S3
```json
{
  "error": "Failed to upload avatar: ..."
}
```

---

## Ejemplo de Uso (JavaScript/TypeScript)

### Con Fetch API
```javascript
async function uploadAvatar(file, accessToken) {
  // Convertir archivo a base64
  const reader = new FileReader();
  
  return new Promise((resolve, reject) => {
    reader.onload = async () => {
      const base64Image = reader.result; // Incluye el prefijo data:image/...
      
      // Extraer extensión del archivo
      const extension = file.name.split('.').pop().toLowerCase();
      
      try {
        const response = await fetch('http://127.0.0.1:8000/api/customers/upload-avatar/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            image: base64Image,
            extension: extension
          })
        });
        
        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.error || 'Upload failed');
        }
        
        const data = await response.json();
        resolve(data);
      } catch (error) {
        reject(error);
      }
    };
    
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

// Uso:
const fileInput = document.getElementById('avatarInput');
const file = fileInput.files[0];
const token = localStorage.getItem('access_token');

uploadAvatar(file, token)
  .then(data => {
    console.log('Avatar uploaded:', data.avatar_url);
    // Actualizar UI con la nueva imagen
    document.getElementById('userAvatar').src = data.avatar_url;
  })
  .catch(error => {
    console.error('Error uploading avatar:', error);
  });
```

### Con Axios
```javascript
import axios from 'axios';

async function uploadAvatar(file, accessToken) {
  // Convertir archivo a base64
  const toBase64 = (file) => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = error => reject(error);
  });

  try {
    const base64Image = await toBase64(file);
    const extension = file.name.split('.').pop().toLowerCase();
    
    const response = await axios.post(
      'http://127.0.0.1:8000/api/customers/upload-avatar/',
      {
        image: base64Image,
        extension: extension
      },
      {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    return response.data;
  } catch (error) {
    console.error('Error uploading avatar:', error.response?.data || error.message);
    throw error;
  }
}

// Uso con React
function AvatarUploader() {
  const [uploading, setUploading] = useState(false);
  
  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validar tamaño
    if (file.size > 5 * 1024 * 1024) {
      alert('El archivo es muy grande. Máximo 5MB.');
      return;
    }
    
    // Validar tipo
    if (!['image/jpeg', 'image/png', 'image/webp', 'image/gif'].includes(file.type)) {
      alert('Formato no soportado. Use JPG, PNG, WEBP o GIF.');
      return;
    }
    
    setUploading(true);
    
    try {
      const token = localStorage.getItem('access_token');
      const result = await uploadAvatar(file, token);
      console.log('Avatar uploaded successfully:', result);
      // Actualizar estado de la aplicación
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setUploading(false);
    }
  };
  
  return (
    <div>
      <input 
        type="file" 
        accept="image/jpeg,image/png,image/webp,image/gif"
        onChange={handleFileChange}
        disabled={uploading}
      />
      {uploading && <p>Subiendo...</p>}
    </div>
  );
}
```

---

## Notas Importantes

1. **URL Firmada**: La URL del avatar es temporal (7 días de validez). Después de ese tiempo, necesitas regenerar la URL o usar los campos `avatar_s3_bucket` y `avatar_s3_key` para generar una nueva.

2. **Almacenamiento**: Las imágenes se guardan en:
   - Bucket: `si2-proyectos`
   - Path: `si2-ecommerce-images/user-{user_id}/{timestamp}_{uuid}_avatar.{extension}`

3. **Reintentos**: El sistema intenta subir la imagen hasta 3 veces con backoff exponencial en caso de error.

4. **Metadatos**: Cada imagen incluye metadatos:
   - `product_sku`: `user-{user_id}` (para organización)
   - `uploaded_at`: Timestamp de subida
   - `original_filename`: `avatar`

5. **Perfil**: Después de subir el avatar, los campos se actualizan automáticamente en el perfil del usuario:
   - `avatar`: URL firmada
   - `avatar_s3_bucket`: Nombre del bucket
   - `avatar_s3_key`: Clave del objeto en S3

6. **Actualización del Login**: Al hacer login, el campo `avatar` se incluye en la respuesta dentro del objeto `user`.

---

## Testing con PowerShell

```powershell
# 1. Login
$body = @{username='tu@email.com'; password='tuPassword'} | ConvertTo-Json
$login = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/customers/login/" -Method POST -ContentType "application/json" -Body $body
$token = $login.tokens.access

# 2. Subir avatar (imagen de prueba 1x1 pixel)
$testImage = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
$uploadBody = @{image=$testImage; extension='png'} | ConvertTo-Json
$result = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/customers/upload-avatar/" -Method POST -Headers @{Authorization="Bearer $token"; "Content-Type"="application/json"} -Body $uploadBody

# 3. Ver perfil actualizado
$profile = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/customers/profile/" -Headers @{Authorization="Bearer $token"}
Write-Host "Avatar URL: $($profile.avatar)"
```

---

## Endpoints Relacionados

- `GET /api/customers/profile/` - Ver perfil (incluye avatar)
- `PUT /api/customers/profile/` - Actualizar perfil completo
- `PATCH /api/customers/profile/` - Actualizar perfil parcialmente
- `POST /api/customers/login/` - Login (respuesta incluye avatar en user)
