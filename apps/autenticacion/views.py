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

                # ✅ Configurar duración de la sesión
                if recordar:
                    # 🔹 Mantener sesión iniciada (30 días o hasta cerrar navegador)
                    request.session.set_expiry(timedelta(days=30))
                else:
                    # ⏰ Cerrar sesión tras 20 minutos de inactividad
                    request.session.set_expiry(timedelta(minutes=20))

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
    logout(request)
    return redirect('iniciar_sesion')

# --- Editar perfil (nombre, apellido, correo, foto) ---
@login_required
def editar_perfil(request):
    # Crear el perfil si no existe (por si el usuario es viejo)
    perfil, created = Perfil.objects.get_or_create(user=request.user)

    user = request.user
    user_form = PerfilUsuarioForm(instance=user)
    perfil_form = PerfilForm(instance=perfil)

    if request.method == 'POST':
        user_form = PerfilUsuarioForm(request.POST, instance=user)
        perfil_form = PerfilForm(request.POST, request.FILES, instance=perfil)
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

            # 🔹 Guardar la foto de perfil en /static/autenticacion/images/usuarios/
            nueva_foto = request.FILES.get('foto')
            if nueva_foto:
                # Carpeta destino
                destino = os.path.join(
                    settings.BASE_DIR,
                    'apps', 'autenticacion', 'static', 'autenticacion', 'images', 'usuarios'
                )
                os.makedirs(destino, exist_ok=True)

                # Nombre de archivo: username + extensión
                extension = nueva_foto.name.split('.')[-1]
                nombre_archivo = f"{user.username}.{extension}"
                ruta_archivo = os.path.join(destino, nombre_archivo)

                # Guardar físicamente
                with open(ruta_archivo, 'wb+') as f:
                    for chunk in nueva_foto.chunks():
                        f.write(chunk)

                # Guardar en el modelo el nombre del archivo
                perfil.foto = nombre_archivo
                perfil.save()
            else:
                perfil_form.save()  # si no sube nueva foto, guardar los demás campos

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