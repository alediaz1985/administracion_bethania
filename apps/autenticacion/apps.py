# apps/autenticacion/apps.py
from django.apps import AppConfig

class AutenticacionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.autenticacion'

    def ready(self):
        """
        Se ejecuta automáticamente cuando Django inicia la app.
        Importamos las señales para que queden registradas.
        """
        import apps.autenticacion.signals  # noqa
