#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
```

**4. Configurar `settings.py` para Producción**
Abre **`inventario_backend/settings.py`** y haz estos cambios cruciales.

**A. Importar librerías nuevas al inicio:**
```python
import os
import dj_database_url # <--- NUEVO
from pathlib import Path
```

**B. Configurar Seguridad y Hosts:**
```python
# SEGURIDAD: Nunca uses 'True' en producción, pero usaremos una variable de entorno para controlarlo
DEBUG = 'RENDER' not in os.environ

# Permitir que Render acceda a tu app
ALLOWED_HOSTS = ['*'] # Asterisco permite todo (útil para empezar), luego lo restringiremos al dominio real
```

**C. Configurar Base de Datos (SQLite local vs Postgres nube):**
Busca la sección `DATABASES` y cámbiala por esto:

```python
DATABASES = {
    'default': dj_database_url.config(
        # Busca la variable DATABASE_URL, si no la encuentra, usa SQLite local
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),
        conn_max_age=600
    )
}
```

**D. Configurar Archivos Estáticos (WhiteNoise):**
Esto es vital para que el panel de admin se vea bien.

Agrega `whitenoise` en `MIDDLEWARE` (justo después de `SecurityMiddleware`):

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # <--- AQUÍ
    # ... resto de middlewares ...
]
```

Y al final del archivo `settings.py`, agrega esto:

```python
# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
if not DEBUG:
    # En producción:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'