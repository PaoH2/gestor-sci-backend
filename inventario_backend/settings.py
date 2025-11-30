"""
Django settings for inventario_backend project.
"""
import os
import dj_database_url # Necesario para la conexión a bases de datos en la nube
from datetime import timedelta
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-hlgsr(owluv-ct5murng%bnbs*p)bp7__pa%6ialhs#c!&bzz1'

# -------------------------------------------------------------
# 1. CONFIGURACIÓN DE DESPLIEGUE (Render)
# -------------------------------------------------------------

# Detecta si estamos en Render (producción)
DEBUG = 'RENDER' not in os.environ

# Permitimos hosts para desarrollo y el host de Render (se define con una variable de entorno)
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # --- Apps de Terceros ---
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    # --- Tu App ---
    'core',
]

# 2. MIDDLEWARE (Agregamos WhiteNoise)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # <--- AGREGADO: Para servir archivos estáticos en Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'inventario_backend.urls'

# ... (TEMPLATES, WSGI_APPLICATION siguen igual) ...

# 3. DATABASE (Configuración Híbrida)
DATABASES = {
    'default': dj_database_url.config(
        # La variable de entorno DATABASE_URL (de Render) tiene prioridad.
        # Si no existe (estamos en local), usa la configuración local de PostgreSQL.
        default=f'postgresql://admin_inventario:admin@127.0.0.1:5432/inventario_db',
        conn_max_age=600
    )
}


# ... (Password validation, LANGUAGE_CODE, TIME_ZONE, USE_I18N, USE_TZ siguen igual) ...

# 4. ARCHIVOS ESTÁTICOS (STATICFILES)
STATIC_URL = 'static/'
# El directorio donde Django buscará archivos estáticos
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# El directorio donde collectstatic copiará los archivos para producción
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 
# Storage para producción (WhiteNoise)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' 

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- CONFIGURACIÓN PERSONALIZADA ---

AUTH_USER_MODEL = 'core.Usuario'

CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
]
# Agregamos la URL de Render para CORS
if RENDER_EXTERNAL_HOSTNAME:
    CORS_ALLOWED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')
    
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}