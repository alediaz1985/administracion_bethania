# apps/cuotas/base.py
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

class BaseList(LoginRequiredMixin, ListView):
    template_name = None            # obligar a setearlo en hijos
    context_object_name = None      # idem
    paginate_by = 25
    ordering = None

class BaseCreate(LoginRequiredMixin, CreateView):
    template_name = None
    success_url = reverse_lazy("cuotas:home")

    def form_valid(self, form):
        obj = form.save()
        messages.success(self.request, "Creado correctamente.")
        return super().form_valid(form)

class BaseUpdate(LoginRequiredMixin, UpdateView):
    template_name = None
    success_url = reverse_lazy("cuotas:home")

    def form_valid(self, form):
        obj = form.save()
        messages.success(self.request, "Actualizado correctamente.")
        return super().form_valid(form)
