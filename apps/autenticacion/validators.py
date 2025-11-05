# apps/autenticacion/validators.py
from django.core.exceptions import ValidationError

def validate_image_size_5mb(file):
    max_size_mb = 5
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"La imagen no puede superar {max_size_mb} MB.")
