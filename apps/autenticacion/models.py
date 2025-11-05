"""from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    foto = models.CharField(max_length=255, blank=True, null=True)  # guarda la ruta

    @property
    def foto_url(self):
        if self.foto:
            return f"/static/autenticacion/images/usuarios/{self.foto}"
        return "/static/autenticacion/images/default-user.jpg"

    def __str__(self):
        return f"Perfil de {self.user.username}"
"""
# apps/autenticacion/models.py
from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    foto = models.ImageField(upload_to='autenticacion/images/usuarios/', blank=True, null=True)

    @property
    def foto_url(self):
        if self.foto and hasattr(self.foto, 'url'):
            return self.foto.url
        return '/static/autenticacion/images/default-user.jpg'
