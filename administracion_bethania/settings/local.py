# administracion_bethania/settings/local.py
import os
from dotenv import load_dotenv
from .base import *

# Cargar .env.local (si no existe, cae en variables de entorno)
load_dotenv(os.path.join(BASE_DIR, '.env.local'), override=True)

DEBUG = True
ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', '127.0.0.1,localhost')
CSRF_TRUSTED_ORIGINS = [o for o in env_list('CSRF_TRUSTED_ORIGINS', '')]

# Logs útiles en dev
if DEBUG:
    print(f"[DEBUG] GOOGLE_CREDENTIALS           = {GOOGLE_CREDENTIALS} (existe: {os.path.exists(GOOGLE_CREDENTIALS)})")
    print(f"[DEBUG] GOOGLE_CREDENTIALS_ALUMNOS   = {GOOGLE_CREDENTIALS_ALUMNOS} (existe: {os.path.exists(GOOGLE_CREDENTIALS_ALUMNOS)})")
    print(f"[DEBUG] ARCHIVOS_DIR                 = {ARCHIVOS_DIR}")
    print(f"[DEBUG] FOTO_PERFIL_ESTUDIANTE_DIR   = {FOTO_PERFIL_ESTUDIANTE_DIR}")
    print(f"[DEBUG] FOTO_ESTUDIANTE_DIR          = {FOTO_ESTUDIANTE_DIR}")
