from django import forms
from .models import Cartilla
from django.utils import timezone

# Formularios de administración de Django
class CartillaCreateForm(forms.ModelForm):
    especialidad = forms.MultipleChoiceField(choices=[], widget=forms.SelectMultiple(attrs={'class': 'specialty-select'}))

    class Meta:
        model = Cartilla
        fields = [
            'procedencia_convenio', 'tipo_cartilla', 'matricula', 'especialidad', 'nombre', 
            'domicilio', 'telefono', 'barrio_localidad', 'provincia', 'centro_de_atencion', 
            'cuit', 'habilitado', 'email', 'solo_derivacion', 
            'especialidades_originales'
        ]

    tipo_cartilla = forms.ChoiceField(choices=[])
    barrio_localidad = forms.ChoiceField(choices=[])
    provincia = forms.ChoiceField(choices=[])
    habilitado = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, **kwargs):
        super(CartillaCreateForm, self).__init__(*args, **kwargs)
        self.fields['tipo_cartilla'].choices = sorted([(tipo_cartilla, tipo_cartilla) for tipo_cartilla in Cartilla.objects.values_list('tipo_cartilla', flat=True).distinct()])
        self.fields['especialidad'].choices = sorted([(especialidad, especialidad) for especialidad in Cartilla.objects.values_list('especialidad', flat=True).distinct()])
        self.fields['barrio_localidad'].choices = sorted([(barrio_localidad, barrio_localidad) for barrio_localidad in Cartilla.objects.values_list('barrio_localidad', flat=True).distinct()])
        self.fields['provincia'].choices = sorted([(provincia, provincia) for provincia in Cartilla.objects.values_list('provincia', flat=True).distinct()])

    def save(self, commit=True):
        instance = super(CartillaCreateForm, self).save(commit=False)
        instance.fecha_alta = timezone.now().strftime('%d-%m-%Y')
        instance.habilitado = 1
        instance.solo_derivacion = 0
        instance.usuario_alta = 0
        especialidades = self.cleaned_data['especialidad']
        created_instances = []
        for especialidad in especialidades:
            created_instance = Cartilla.objects.create(
                procedencia_convenio=instance.procedencia_convenio,
                tipo_cartilla=instance.tipo_cartilla,
                matricula=instance.matricula,
                especialidad=especialidad,
                nombre=instance.nombre,
                domicilio=instance.domicilio,
                telefono=instance.telefono,
                barrio_localidad=instance.barrio_localidad,
                provincia=instance.provincia,
                centro_de_atencion=instance.centro_de_atencion,
                cuit=instance.cuit,
                habilitado=instance.habilitado,
                email=instance.email,
                solo_derivacion=instance.solo_derivacion,
                fecha_alta=instance.fecha_alta,
                usuario_alta=instance.usuario_alta,
                especialidades_originales=instance.especialidades_originales
            )
            created_instances.append(created_instance)
        return created_instances[0] if created_instances else instance  # Devolver la primera instancia creada o la instancia principal

class CartillaEditForm(forms.ModelForm):
    class Meta:
        model = Cartilla
        fields = [
            'procedencia_convenio', 'tipo_cartilla', 'matricula', 'especialidad', 'nombre', 
            'domicilio', 'telefono', 'barrio_localidad', 'provincia', 'centro_de_atencion', 
            'cuit', 'habilitado', 'email', 'solo_derivacion', 
            'especialidades_originales'
        ]

    tipo_cartilla = forms.ChoiceField(choices=[('', 'Todas')])
    especialidad = forms.ChoiceField(choices=[('', 'Todas')])
    barrio_localidad = forms.ChoiceField(choices=[('', 'Todas')])
    provincia = forms.ChoiceField(choices=[('', 'Todas')])
    habilitado = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(CartillaEditForm, self).__init__(*args, **kwargs)
        self.fields['tipo_cartilla'].choices += sorted([(tipo_cartilla, tipo_cartilla) for tipo_cartilla in Cartilla.objects.values_list('tipo_cartilla', flat=True).distinct()])
        self.fields['especialidad'].choices += sorted([(especialidad, especialidad) for especialidad in Cartilla.objects.values_list('especialidad', flat=True).distinct()])
        self.fields['barrio_localidad'].choices += sorted([(barrio_localidad, barrio_localidad) for barrio_localidad in Cartilla.objects.values_list('barrio_localidad', flat=True).distinct()])
        self.fields['provincia'].choices += sorted([(provincia, provincia) for provincia in Cartilla.objects.values_list('provincia', flat=True).distinct()])

    def clean_habilitado(self):
        return 1 if self.cleaned_data['habilitado'] else 0

    def clean(self):
        cleaned_data = super().clean()
        # Aquí puedes agregar validaciones adicionales si es necesario
        return cleaned_data
    
class CartillaAgregarForm(forms.ModelForm):
    especialidad = forms.MultipleChoiceField(choices=[], widget=forms.SelectMultiple(attrs={'class': 'specialty-select'}))

    class Meta:
        model = Cartilla
        fields = [
            'procedencia_convenio', 'tipo_cartilla', 'matricula', 'especialidad', 'nombre', 
            'domicilio', 'telefono', 'barrio_localidad', 'provincia', 'centro_de_atencion', 
            'cuit', 'habilitado', 'email', 'solo_derivacion', 
            'especialidades_originales'
        ]

    tipo_cartilla = forms.ChoiceField(choices=[('', 'Todas')])
    barrio_localidad = forms.ChoiceField(choices=[('', 'Todas')])
    provincia = forms.ChoiceField(choices=[('', 'Todas')])
    habilitado = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, **kwargs):
        super(CartillaAgregarForm, self).__init__(*args, **kwargs)
        self.fields['tipo_cartilla'].choices += sorted([(tipo_cartilla, tipo_cartilla) for tipo_cartilla in Cartilla.objects.values_list('tipo_cartilla', flat=True).distinct()])
        self.fields['especialidad'].choices += sorted([(especialidad, especialidad) for especialidad in Cartilla.objects.values_list('especialidad', flat=True).distinct()])
        self.fields['barrio_localidad'].choices += sorted([(barrio_localidad, barrio_localidad) for barrio_localidad in Cartilla.objects.values_list('barrio_localidad', flat=True).distinct()])
        self.fields['provincia'].choices += sorted([(provincia, provincia) for provincia in Cartilla.objects.values_list('provincia', flat=True).distinct()])

# Formularios del sitio

class CartillaFilterForm(forms.Form):
    provincia = forms.ChoiceField(
        choices=[('', 'Todas')],
        required=False,
        widget=forms.Select(attrs={'id': 'id_provincia', 'class': 'form-control'})
    )
    barrio_localidad = forms.ChoiceField(
        choices=[('', 'Todas')],
        required=False,
        widget=forms.Select(attrs={'id': 'id_barrio_localidad', 'class': 'form-control'})
    )
    especialidad = forms.ChoiceField(
        choices=[('', 'Todas')],
        required=False,
        widget=forms.Select(attrs={'id': 'id_especialidad', 'class': 'form-control'})
    )
    tipo_cartilla = forms.ChoiceField(
        choices=[('', 'Todas')],
        required=False,
        widget=forms.Select(attrs={'id': 'id_tipo_cartilla', 'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super(CartillaFilterForm, self).__init__(*args, **kwargs)
        self.fields['provincia'].choices += [(provincia, provincia) for provincia in Cartilla.objects.values_list('provincia', flat=True).distinct()]
        self.fields['barrio_localidad'].choices += [(barrio, barrio) for barrio in Cartilla.objects.values_list('barrio_localidad', flat=True).distinct()]
        self.fields['especialidad'].choices += [(especialidad, especialidad) for especialidad in Cartilla.objects.values_list('especialidad', flat=True).distinct()]
        self.fields['tipo_cartilla'].choices += [(tipo, tipo) for tipo in Cartilla.objects.values_list('tipo_cartilla', flat=True).distinct()]