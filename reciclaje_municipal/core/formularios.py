from django import forms
from .models import Ciudadano, SolicitudRetiro


class RegistroCiudadanoForm(forms.ModelForm):
    usuario = forms.CharField(label='Nombre de usuario')
    contraseña = forms.CharField(widget=forms.PasswordInput, label='Contraseña')
    correo = forms.EmailField(label='Correo electrónico')

    class Meta:
        model = Ciudadano
        fields = ['direccion', 'telefono']
        labels = {
            'direccion': 'Dirección',
            'telefono': 'Teléfono',
        }


class SolicitudRetiroForm(forms.ModelForm):
    class Meta:
        model = SolicitudRetiro
        fields = ['tipo_material', 'cantidad', 'fecha_retiro', 'direccion_retiro', 'comentario']
        labels = {
            'tipo_material': 'Tipo de material',
            'cantidad': 'Cantidad (en kilogramos)',  # aclaración directa
            'fecha_retiro': 'Fecha estimada de retiro',
            'direccion_retiro': 'Dirección de retiro',
            'comentario': 'Comentario (opcional)',
        }
        widgets = {
            'fecha_retiro': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control', 'style': 'max-width: 250px;'},
                format='%Y-%m-%d'
            ),
            'comentario': forms.TextInput(attrs={'maxlength': '100'}),
        }
    # 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_retiro'].widget.attrs.update({'class': 'form-control'})
