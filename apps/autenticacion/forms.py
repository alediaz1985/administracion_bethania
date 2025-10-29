from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Perfil

# --- Login ---
class LoginForm(forms.Form):
    username = forms.CharField(
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese su usuario',
            'class': 'form-control'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Ingrese su contraseña',
            'class': 'form-control',
            'id': 'id_password'  # 👈 importante para el icono de ojo
        })
    )

    # ✅ Nuevo campo
    recordar = forms.BooleanField(
        required=False,
        label='Mantener sesión iniciada',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        })
    )

# --- Registro (solo superuser lo usa) ---
class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        labels = {
            'username': 'Nombre de usuario',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
        }

# --- Edición de datos del usuario ---
class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
        }

# --- Edición de foto de perfil ---
class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['foto']
        labels = {'foto': 'Foto de perfil'}
