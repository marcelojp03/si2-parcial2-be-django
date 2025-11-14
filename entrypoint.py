#!/usr/bin/env python
"""
Script de inicio para App Runner
Maneja migraciones y collectstatic con mejor logging
"""
import os
import sys
import subprocess

def run_command(cmd, description):
    """Ejecuta comando y muestra logs"""
    print(f"\n{'='*60}")
    print(f"🔵 {description}")
    print(f"{'='*60}")
    print(f"Comando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ ÉXITO")
        if result.stdout:
            print(f"STDOUT:\n{result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR (Exit Code: {e.returncode})")
        if e.stdout:
            print(f"STDOUT:\n{e.stdout}")
        if e.stderr:
            print(f"STDERR:\n{e.stderr}")
        return False

def main():
    print("\n" + "="*60)
    print("🚀 INICIANDO APLICACIÓN DJANGO")
    print("="*60)
    
    # Verificar variables de entorno críticas
    print("\n📋 Variables de entorno:")
    env_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DEBUG', 'DJANGO_SETTINGS_MODULE']
    for var in env_vars:
        value = os.environ.get(var, 'NO CONFIGURADA')
        # Ocultar passwords
        if 'PASS' in var or 'KEY' in var:
            value = '***' if value != 'NO CONFIGURADA' else value
        print(f"  {var}: {value}")
    
    # Ejecutar collectstatic (opcional, controlado por variable de entorno)
    # Uso: RUN_COLLECTSTATIC=true/false (por compatibilidad aceptamos SKIP_COLLECTSTATIC también)
    run_collectstatic_env = os.environ.get('RUN_COLLECTSTATIC')
    if run_collectstatic_env is None:
        # Compatibilidad retroactiva con SKIP_COLLECTSTATIC
        run_collectstatic = not (os.environ.get('SKIP_COLLECTSTATIC', 'false').lower() == 'true')
    else:
        run_collectstatic = run_collectstatic_env.lower() in ('1', 'true', 'yes')

    # Ejecutar migraciones (opcional, controlado por variable de entorno)
    run_migrations_env = os.environ.get('RUN_MIGRATIONS')
    if run_migrations_env is None:
        run_migrations = not (os.environ.get('SKIP_MIGRATE', 'false').lower() == 'true')
    else:
        run_migrations = run_migrations_env.lower() in ('1', 'true', 'yes')

    # Antes de collectstatic, asegurar que STATIC_ROOT exista (si está definido)
    static_root = os.environ.get('STATIC_ROOT')
    if not static_root:
        try:
            # Intentar obtener desde django settings si disponibles
            from django.conf import settings as _dj_settings
            static_root = getattr(_dj_settings, 'STATIC_ROOT', None)
        except Exception:
            static_root = None

    if run_collectstatic:
        if static_root:
            try:
                os.makedirs(static_root, exist_ok=True)
                print(f"✅ Asegurado STATIC_ROOT en: {static_root}")
            except Exception as e:
                print(f"⚠️ No se pudo crear STATIC_ROOT '{static_root}': {e}")

        if not run_command(
            ['python', 'manage.py', 'collectstatic', '--noinput'],
            'Recolectando archivos estáticos'
        ):
            print("⚠️ Collectstatic falló, continuando según configuración")
    else:
        print("ℹ️ RUN_COLLECTSTATIC está deshabilitado; omitiendo collectstatic")

    if run_migrations:
        if not run_command(
            ['python', 'manage.py', 'migrate', '--noinput'],
            'Ejecutando migraciones de base de datos'
        ):
            print("❌ Migraciones fallaron - ABORTANDO")
            sys.exit(1)
    else:
        print("ℹ️ RUN_MIGRATIONS está deshabilitado; omitiendo migrate")
    
    # Iniciar Gunicorn
    print("\n" + "="*60)
    print("🌐 INICIANDO GUNICORN EN PUERTO 1112")
    print("="*60)
    
    os.execvp('gunicorn', [
        'gunicorn',
        'ecommerce.wsgi:application',
        '--bind', '0.0.0.0:1112',
        '--workers', '2',
        '--threads', '4',
        '--timeout', '120',
        '--access-logfile', '-',
        '--error-logfile', '-',
        '--log-level', 'info',
        '--capture-output',
        '--enable-stdio-inheritance'
    ])

if __name__ == '__main__':
    main()
