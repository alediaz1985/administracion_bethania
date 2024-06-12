# apps/autenticacion/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import LoginForm, RegisterForm

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
                return render(request, 'autenticacion/iniciar_sesion.html', {'form': form, 'error': 'Credenciales inválidas'})
    else:
        form = LoginForm()
    return render(request, 'autenticacion/iniciar_sesion.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'autenticacion/registrar.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')
