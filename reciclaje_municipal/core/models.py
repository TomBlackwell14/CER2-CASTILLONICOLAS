from django.db import models
from django.contrib.auth.models import User


class Ciudadano(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username


class SolicitudRetiro(models.Model):
    TIPO_MATERIAL_CHOICES = [
        ('VID', 'Vidrio'),
        ('PAP', 'Papel'),
        ('PLA', 'Plástico'),
        ('LAT', 'Latas'),
        ('ORG', 'Orgánico'),
        ('ELE', 'Electrónicos'),
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_ruta', 'En Ruta'),
        ('completado', 'Completado'),
    ]

    ciudadano = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo_material = models.CharField(max_length=3, choices=TIPO_MATERIAL_CHOICES)
    cantidad = models.DecimalField(max_digits=6, decimal_places=2)
    fecha_retiro = models.DateField()
    direccion_retiro = models.CharField(max_length=255)
    comentario = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    operario_asignado = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='retiros_asignados')
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_tipo_material_display()} - {self.ciudadano.username}"
