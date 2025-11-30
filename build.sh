#!/usr/bin/env bash
# Script de construcción para Render
set -o errexit

# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Recopilar archivos estáticos (CSS del Admin)
python manage.py collectstatic --no-input

# 3. Aplicar migraciones (Crear tablas)
python manage.py migrate