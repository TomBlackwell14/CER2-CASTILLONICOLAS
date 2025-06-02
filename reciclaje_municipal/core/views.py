from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.timesince import timesince
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from .models import SolicitudRetiro, Ciudadano
from .formularios import RegistroCiudadanoForm, SolicitudRetiroForm


# Página de inicio con métricas
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField

def inicio(request):

    materiales = SolicitudRetiro.objects.values('tipo_material').annotate(total=Count('id'))
    promedio_kg = SolicitudRetiro.objects.aggregate(
        promedio=Avg('cantidad')
    )['promedio'] or 0

    # Tiempo promedio
    tiempo_promedio = SolicitudRetiro.objects.filter(
        estado='completado',
        completado_en__isnull=False
    ).annotate(
        duracion=ExpressionWrapper(
            F('completado_en') - F('creado_en'),
            output_field=DurationField()
        )
    ).aggregate(
        promedio_duracion=Avg('duracion')
    )['promedio_duracion']

    return render(request, 'core/inicio.html', {
        'materiales': materiales,
        'promedio_kg': round(promedio_kg, 2),
        'tiempo_promedio': tiempo_promedio,
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
        return redirect('perfil')
    return render(request, 'core/eliminar_confirmacion.html', {'solicitud': solicitud})
