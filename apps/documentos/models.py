from django.db import models

class Documento(models.Model):
    archivo = models.FileField(upload_to='documentos/')
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre
