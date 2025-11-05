# apps/autenticacion/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import LoginForm, RegisterForm, PerfilUsuarioForm, PerfilForm
from .models import Perfil
from django.conf import settings
import os
from datetime import timedelta
from time import time

# --- Iniciar sesión ---
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            recordar = form.cleaned_data.get('recordar')  # ✅ nuevo campo

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                # ✅ Guardar preferencia del usuario en la sesión
                request.session['recordar'] = bool(recordar)

                # ✅ Configurar duración de la sesión
                if recordar:
                    # 🔹 Mantener sesión iniciada (30 días o hasta cerrar navegador)
                    request.session.set_expiry(timedelta(days=30))
                else:
                    # ⏰ Cerrar sesión tras 20 minutos de inactividad
                    request.session.set_expiry(timedelta(minutes=25))

                return redirect('home')
            else:
                return render(request, 'autenticacion/iniciar_sesion.html', {
                    'form': form,
                    'error': 'El nombre de usuario o la contraseña no son correctos. Por favor, verificá tus datos e intentá nuevamente.'
                })
    else:
        form = LoginForm()

    return render(request, 'autenticacion/iniciar_sesion.html', {'form': form})

# --- Crear usuarios (solo superusuario) ---
@login_required
@user_passes_test(lambda u: u.is_superuser)
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado correctamente.')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'autenticacion/registrar.html', {'form': form})

# --- Cerrar sesión ---
def logout_view(request):
    request.session.pop('recordar', None)  # 🔹 elimina la variable si existe
    logout(request)
    return redirect('iniciar_sesion')

# --- Editar perfil (nombre, apellido, correo, foto) ---
@login_required
def editar_perfil(request):
    # Garantizar que exista Perfil
    perfil, _ = Perfil.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = PerfilUsuarioForm(request.POST, instance=request.user)
        perfil_form = PerfilForm(request.POST, request.FILES, instance=perfil)

        new_password = request.POST.get('password') or ''
        confirm_password = request.POST.get('password_confirm') or ''

        ok = user_form.is_valid() and perfil_form.is_valid()

        # Validación de password (opcional)
        if (new_password or confirm_password) and new_password != confirm_password:
            ok = False
            messages.error(request, 'Las contraseñas no coinciden.')

        if ok:
            # 1) Guardar datos del usuario
            user = user_form.save(commit=False)
            if new_password:
                user.set_password(new_password)
            user.save()

            # 2) Guardar foto (y demás campos de Perfil) -> ¡acá va el archivo!
            #    NO escribir en /static ni manejar archivos a mano
            perfil_form.save()

            messages.success(request, 'Perfil actualizado correctamente.')

            if new_password:
                # Mantener sesión activa tras cambiar password
                update_session_auth_hash(request, user)

            return redirect('ver_perfil')
    else:
        user_form = PerfilUsuarioForm(instance=request.user)
        perfil_form = PerfilForm(instance=perfil)

    return render(request, 'autenticacion/editar_perfil.html', {
        'user_form': user_form,
        'perfil_form': perfil_form,
    })

# --- Ver perfil del usuario ---
@login_required
def ver_perfil(request):
    perfil = request.user.perfil
    timestamp = int(time())  # número UNIX
    return render(request, 'autenticacion/ver_perfil.html', {
        'perfil': perfil,
        'cache_buster': timestamp
    })