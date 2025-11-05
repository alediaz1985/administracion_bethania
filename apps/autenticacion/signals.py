# apps/autenticacion/signals.py
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Perfil

def _delete_file_safe(field_file):
    """
    Elimina el archivo físico del storage si existe.
    No lanza excepciones (útil para limpiezas silenciosas).
    """
    try:
        if field_file and getattr(field_file, "name", None):
            storage = field_file.storage
            name = field_file.name
            if storage.exists(name):
                storage.delete(name)
    except Exception:
        # Podés loguear si querés
        pass

@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    """
    Crea un Perfil vinculado cuando se crea un User nuevo.
    """
    if created:
        Perfil.objects.create(user=instance)

@receiver(pre_save, sender=Perfil)
def borrar_foto_anterior_en_reemplazo(sender, instance: Perfil, **kwargs):
    """
    Si se reemplaza o se limpia la foto, elimina el archivo anterior para no dejar basura.
    - Caso limpiar: old.name existía y new.name es None/"".
    - Caso reemplazo: old.name != new.name.
    """
    if not instance.pk:
        # Es un Perfil nuevo; no hay archivo anterior que borrar.
        return

    try:
        old = Perfil.objects.get(pk=instance.pk)
    except Perfil.DoesNotExist:
        return

    old_name = getattr(getattr(old, "foto", None), "name", "") or ""
    new_name = getattr(getattr(instance, "foto", None), "name", "") or ""

    # Limpieza (se dejó vacío el campo) o reemplazo (nombre distinto)
    if old_name and old_name != new_name:
        _delete_file_safe(old.foto)

@receiver(post_delete, sender=Perfil)
def borrar_foto_al_eliminar_perfil(sender, instance: Perfil, **kwargs):
    """
    Al borrar el Perfil, también eliminamos su archivo de foto si existe.
    """
    _delete_file_safe(instance.foto)
