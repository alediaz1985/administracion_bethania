# administracion_bethania/middleware.py

from django.shortcuts import redirect
from django.conf import settings
from django.urls import resolve

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and resolve(request.path_info).url_name != settings.LOGIN_URL:
            return redirect(settings.LOGIN_URL)
        return self.get_response(request)
