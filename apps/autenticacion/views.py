# apps/autenticacion/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import LoginForm, RegisterForm, PerfilUsuarioForm, PerfilForm
from .models import Perfil

# --- Iniciar sesión ---
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                return render(request, 'autenticacion/iniciar_sesion.html', {
                    'form': form,
                    'error': 'Credenciales inválidas'
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
    logout(request)
    return redirect('home')

# --- Editar perfil (nombre, apellido, correo, foto) ---
@login_required
def editar_perfil(request):
    # Crear el perfil si no existe (por si el usuario es viejo)
    Perfil.objects.get_or_create(user=request.user)

    user = request.user
    user_form = PerfilUsuarioForm(instance=user)
    perfil_form = PerfilForm(instance=user.perfil)

    if request.method == 'POST':
        user_form = PerfilUsuarioForm(request.POST, instance=user)
        perfil_form = PerfilForm(request.POST, request.FILES, instance=user.perfil)
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('password_confirm')

        if user_form.is_valid() and perfil_form.is_valid():
            user = user_form.save(commit=False)

            # Si el usuario escribió una nueva contraseña
            if new_password or confirm_password:
                if new_password == confirm_password:
                    user.set_password(new_password)
                else:
                    messages.error(request, 'Las contraseñas no coinciden.')
                    return redirect('editar_perfil')

            user.save()
            perfil_form.save()

            messages.success(request, 'Perfil actualizado correctamente.')

            # Si cambió la contraseña, forzamos re-login
            if new_password:
                logout(request)
                return redirect('iniciar_sesion')

            return redirect('ver_perfil')

    return render(request, 'autenticacion/editar_perfil.html', {
        'user_form': user_form,
        'perfil_form': perfil_form,
    })

# --- Ver perfil del usuario ---
@login_required
def ver_perfil(request):
    perfil = request.user.perfil
    return render(request, 'autenticacion/ver_perfil.html', {'perfil': perfil})