# Variables de Entorno para AWS App Runner

Configure las siguientes variables de entorno en la configuración de App Runner:

## Django Core
```
SECRET_KEY=django-insecure-!#p#81kh($(j06quz71u_2*&8wye(ix*1!ee247w-%_w^xs^%0
DEBUG=False
ALLOWED_HOSTS=*.awsapprunner.com,*.amazonaws.com,localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=ecommerce.settings
PYTHONUNBUFFERED=1
# Preferible: controlar con RUN_MIGRATIONS / RUN_COLLECTSTATIC (true/false)
# Compatibilidad: SKIP_MIGRATE / SKIP_COLLECTSTATIC también son aceptados
RUN_MIGRATIONS=false
RUN_COLLECTSTATIC=false
```

## Base de Datos PostgreSQL
```
DB_USER=postgres
DB_PASS=postgres
DB_HOST=dbvpay.cfiek6gqkqd5.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=vpayDB
DB_SCHEMA=si2-ecommerce
```

## AWS
```
AWS_REGION=us-east-1
```

## JWT
```
JWT_SECRET_KEY=uagrm123
```

## OpenAI (Opcional - para reportes con IA)
```
OPENAI_API_KEY=sk-proj-YOUR_OPENAI_KEY_HERE
LLM_MODEL=gpt-4o-mini
```

## Notas Importantes

1. **DEBUG**: DEBE estar en `False` en producción
2. **ALLOWED_HOSTS**: Agregar el dominio de App Runner (ej: `abc123.us-east-1.awsapprunner.com`)
3. **Puerto**: Configurado en 1112 (ajustado en la configuración de App Runner)
4. **SKIP_MIGRATE**: Configurar en `true` si la base de datos ya está migrada (evita ejecutar migraciones en cada deploy)
5. **SKIP_COLLECTSTATIC**: Configurar en `true` si no usas archivos estáticos o ya están en S3
6. **Credenciales AWS**: Si usa boto3/S3, asegúrese de configurar IAM Role en App Runner
7. **Base de Datos**: 
   - Verificar que RDS permita conexiones desde App Runner (Security Group)
   - Agregar el Security Group de App Runner al inbound rules de RDS
   - Asegurarse de que el schema `si2-ecommerce` existe en la base de datos

## Pasos para Configurar en App Runner

1. Ir a AWS App Runner Console
2. Seleccionar el servicio
3. Configuration → Edit → Environment Variables
4. Agregar todas las variables listadas arriba
5. Save y Deploy
