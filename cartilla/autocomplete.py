# filepath: /c:/Users/jipai/OneDrive/Escritorio/django/admin/cartilla/autocomplete.py
from dal import autocomplete
from .models import Cartilla

class ProvinciaAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Cartilla.objects.none()

        qs = Cartilla.objects.all().distinct('provincia')

        if self.q:
            qs = qs.filter(provincia__icontains=self.q)

        return qs

class BarrioLocalidadAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Cartilla.objects.none()

        provincia = self.forwarded.get('provincia', None)
        qs = Cartilla.objects.all()

        if provincia:
            qs = qs.filter(provincia=provincia).distinct('barrio_localidad')

        if self.q:
            qs = qs.filter(barrio_localidad__icontains=self.q)

        return qs

class EspecialidadAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Cartilla.objects.none()

        provincia = self.forwarded.get('provincia', None)
        barrio_localidad = self.forwarded.get('barrio_localidad', None)
        qs = Cartilla.objects.all()

        if provincia:
            qs = qs.filter(provincia=provincia)
        if barrio_localidad:
            qs = qs.filter(barrio_localidad=barrio_localidad).distinct('especialidad')

        if self.q:
            qs = qs.filter(especialidad__icontains=self.q)

        return qs