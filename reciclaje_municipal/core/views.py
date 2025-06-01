from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.timesince import timesince
from django.db.models import Count, Avg
from django.db.models.functions import TruncMonth

from .models import SolicitudRetiro, Ciudadano
from .formularios import RegistroCiudadanoForm, SolicitudRetiroForm


# Página de inicio con métricas
def inicio(request):
    # MÉTRICA 1: Solicitudes por mes
    solicitudes_por_mes = (
        SolicitudRetiro.objects
        .annotate(mes=TruncMonth('creado_en'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    # MÉTRICA 2: Tipos de materiales más reciclados
    materiales_mas_reciclados = (
        SolicitudRetiro.objects
        .values('tipo_material')
        .annotate(total=Count('tipo_material'))
        .order_by('-total')[:5]
    )

    # MÉTRICA 3: Promedio de cantidad reciclada (en kg)
    promedio_kg = SolicitudRetiro.objects.aggregate(promedio=Avg('cantidad'))['promedio']

    return render(request, 'core/inicio.html', {
        'solicitudes_por_mes': solicitudes_por_mes,
        'materiales_mas_reciclados': materiales_mas_reciclados,
        'promedio_kg': promedio_kg,
    })


# Página de información general
def informacion(request):
    return render(request, 'core/informacion.html')


# Registro de ciudadanos
def registrate(request):
    if request.method == 'POST':
        form = RegistroCiudadanoForm(request.POST)
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['usuario']).exists():
                messages.warning(request, 'El nombre de usuario ya está en uso.')
            else:
                user = User.objects.create_user(
                    username=form.cleaned_data['usuario'],
                    password=form.cleaned_data['contraseña'],
                    email=form.cleaned_data['correo']
                )
                Ciudadano.objects.create(
                    user=user,
                    direccion=form.cleaned_data['direccion'],
                    telefono=form.cleaned_data['telefono'],
                )
                messages.success(request, '¡Cuenta creada con éxito!')
                return redirect('inicio_sesion')
    else:
        form = RegistroCiudadanoForm()
    return render(request, 'core/registrate.html', {'form': form})


# Perfil del ciudadano
@login_required(login_url='inicio_sesion')
def perfil(request):
    try:
        ciudadano = Ciudadano.objects.get(user=request.user)
        solicitudes = SolicitudRetiro.objects.filter(ciudadano=request.user).order_by('-creado_en')
        for solicitud in solicitudes:
            solicitud.tiempo_transcurrido = timesince(solicitud.creado_en)
    except Ciudadano.DoesNotExist:
        ciudadano = None
        solicitudes = []
        messages.warning(request, 'No hay datos del ciudadano asociados.')

    return render(request, 'core/perfil.html', {
        'ciudadano': ciudadano,
        'solicitudes': solicitudes,
    })


# Formulario para solicitar retiro
@login_required(login_url='inicio_sesion')
def recicla_ahora(request):
    if request.method == 'POST':
        form = SolicitudRetiroForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.ciudadano = request.user
            solicitud.save()
            messages.success(request, 'Solicitud enviada correctamente.')
            return redirect('perfil')
    else:
        form = SolicitudRetiroForm()
    return render(request, 'core/recicla.html', {'form': form})


# Eliminar solicitud
@login_required
def eliminar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudRetiro, id=solicitud_id, ciudadano=request.user)
    if request.method == 'POST':
        solicitud.delete()
        messages.success(request, 'Solicitud eliminada correctamente.')
        return redirect('perfil')
    return render(request, 'core/eliminar_confirmacion.html', {'solicitud': solicitud})
