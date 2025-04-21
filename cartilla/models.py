from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

class Cartilla(models.Model):
    id = models.AutoField(primary_key=True)
    procedencia_convenio = models.CharField(max_length=50, null=True, blank=True)
    tipo_cartilla = models.CharField(max_length=50, null=True, blank=True)
    matricula = models.CharField(max_length=255, null=True, blank=True)
    especialidad = models.CharField(max_length=3000)
    nombre = models.CharField(max_length=255)
    domicilio = models.CharField(max_length=255)
    telefono = models.CharField(max_length=255, null=True, blank=True)
    barrio_localidad = models.CharField(max_length=255, null=True, blank=True)
    provincia = models.CharField(max_length=50, null=True, blank=True)
    centro_de_atencion = models.CharField(max_length=255, null=True, blank=True)
    cuit = models.CharField(max_length=15, null=True, blank=True)
    habilitado = models.IntegerField(default=1)
    email = models.CharField(max_length=100, null=True, blank=True)
    solo_derivacion = models.BooleanField(default=False)
    fecha_alta = models.CharField(max_length=15, default=timezone.now().strftime('%d-%m-%Y'))
    usuario_alta = models.IntegerField(null=True, blank=True)
    fecha_baja = models.CharField(max_length=15, null=True, blank=True)
    especialidades_originales = models.CharField(max_length=255, null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        db_table = 'cartilla_online'  # Nombre de la tabla en la base de datos

class HistoricalCartillaProxy(Cartilla.history.model):
    class Meta:
        proxy = True
        verbose_name = "Historial de Cambio"
        verbose_name_plural = "Historial de Cambios"