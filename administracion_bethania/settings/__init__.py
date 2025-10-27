# administracion_bethania/settings/__init__.py
import os
from importlib import import_module

DJANGO_ENV = os.getenv("DJANGO_ENV", "local").strip().lower()
if DJANGO_ENV not in {"local", "production"}:
    DJANGO_ENV = "local"

module_path = f"administracion_bethania.settings.{DJANGO_ENV}"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", module_path)

globals().update(import_module(module_path).__dict__)
