from django import forms
from .models import Cartilla, CartillaChangeRequest
from django.utils import timezone
from django.contrib.auth.models import User

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
        # Guardar la instancia actual antes de actualizarla
        instance = super(CartillaEditForm, self).save(commit=False)
    
        # Crear una solicitud de cambio en lugar de guardar directamente
        for field in self.changed_data:
            # Forzar una consulta directa a la base de datos para obtener el valor antiguo
            old_value_query = Cartilla.objects.filter(pk=self.instance.pk).values(field).first()
            old_value = old_value_query[field] if old_value_query and field in old_value_query else ''  # Manejar valores nulos o inexistentes
    
            # Obtener el nuevo valor del formulario
            new_value = self.cleaned_data[field]
    
            # Obtener la instancia del usuario a partir de usuario_alta
            user_instance = User.objects.filter(id=self.instance.usuario_alta).first()
            if user_instance:  # Verificar que el usuario exista
                CartillaChangeRequest.objects.create(
                    cartilla=self.instance,
                    action='update',
                    field_name=field,
                    old_value=old_value,  # Guardar el valor antiguo correctamente
                    new_value=new_value,  # Guardar el nuevo valor correctamente
                    requested_by=user_instance  # Asignar la instancia del usuario
                )
        return instance  # No guardar directamente
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
    def save(self, commit=True):
        # Guardar la instancia actual antes de actualizarla
        instance = super(CartillaEditForm, self).save(commit=False)
    
        # Crear una solicitud de cambio en lugar de guardar directamente
        for field in self.changed_data:
            # Obtener el valor antiguo directamente desde la base de datos
            old_value_query = Cartilla.objects.filter(pk=self.instance.pk).values_list(field, flat=True).first()
            old_value = old_value_query if old_value_query is not None else ''  # Manejar valores nulos
    
            # Obtener el nuevo valor del formulario
            new_value = self.cleaned_data[field]
    
            # Obtener la instancia del usuario a partir de usuario_alta
            user_instance = User.objects.filter(id=self.instance.usuario_alta).first()
            if user_instance:  # Verificar que el usuario exista
                CartillaChangeRequest.objects.create(
                    cartilla=self.instance,
                    action='update',
                    field_name=field,
                    old_value=old_value,  # Guardar el valor antiguo correctamente
                    new_value=new_value,  # Guardar el nuevo valor correctamente
                    requested_by=user_instance  # Asignar la instancia del usuario
                )
        return instance  # No guardar directamente
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