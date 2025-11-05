# apps/autenticacion/models.py
from django.db import models
from django.contrib.auth.models import User
from .validators import validate_image_size_5mb

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    foto = models.ImageField(
        upload_to='autenticacion/images/usuarios/',
        blank=True,
        null=True,
        validators=[validate_image_size_5mb],  # 👈 agregado
    )

    @property
    def foto_url(self):
        if self.foto and hasattr(self.foto, 'url'):
            return self.foto.url
        return '/static/autenticacion/images/default-user.jpg'

    def __str__(self):
        return f"Perfil de {self.user.username}"
