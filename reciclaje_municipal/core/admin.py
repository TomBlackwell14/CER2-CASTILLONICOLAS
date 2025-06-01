from django.contrib import admin
from django.core.exceptions import PermissionDenied
from .models import SolicitudRetiro

@admin.register(SolicitudRetiro)
class SolicitudRetiroAdmin(admin.ModelAdmin):
    list_display = ['ciudadano', 'tipo_material', 'estado', 'fecha_retiro', 'operario_asignado']
    list_filter = ['estado', 'operario_asignado']
    search_fields = ['ciudadano__username', 'direccion_retiro']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='Operadores').exists():
            return qs.filter(operario_asignado=request.user)
        return qs

    def get_readonly_fields(self, request, obj=None):
        # OPERADORES solo puede editar 'estado'
        if request.user.groups.filter(name='Operadores').exists():
            return [f.name for f in self.model._meta.fields if f.name != 'estado']
        # STAFF puede editar 'estado' y 'operario_asignado'
        elif request.user.groups.filter(name='Staff').exists():
            return [f.name for f in self.model._meta.fields if f.name not in ['estado', 'operario_asignado']]
        # SUPERUSER puede editar todo
        return super().get_readonly_fields(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        # BLOQUEA FORMULARIO si operador intenta editar solicitud no asignada
        if obj and request.user.groups.filter(name='Operadores').exists():
            if obj.operario_asignado != request.user:
                raise PermissionDenied("No tienes permiso para editar esta solicitud.")
        return super().get_form(request, obj, **kwargs)

    def has_change_permission(self, request, obj=None):
        # OPERADOR solo puede modificar solicitudes asignadas a él
        if request.user.groups.filter(name='Operadores').exists():
            if obj is None:
                return False
            return obj.operario_asignado == request.user
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request):
        # OPERADOR no puede crear
        if request.user.groups.filter(name='Operadores').exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        # OPERADOR no puede eliminar
        if request.user.groups.filter(name='Operadores').exists():
            return False
        return super().has_delete_permission(request, obj)
