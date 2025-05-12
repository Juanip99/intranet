from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib import admin

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

    class Meta:
        db_table = 'cartilla_online'  # Nombre de la tabla en la base de datos

    def __str__(self):
        return self.nombre

class CartillaChangeRequest(models.Model):
    ACTION_CHOICES = [
        ('create', 'Alta'),
        ('update', 'Edición'),
        ('delete', 'Baja'),
        ('add_specialties', 'Agregar Especialidades'),
    ]

    cartilla = models.ForeignKey(
        'Cartilla',
        on_delete=models.CASCADE,
        related_name='change_requests',
        null=True,
        blank=True
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, null=True, blank=True)
    field_name = models.CharField(max_length=255, null=True, blank=True)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    requested_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_changes'
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'cartilla_change_request'

    def __str__(self):
        if self.cartilla:
            return f"{self.get_action_display()} - {self.cartilla.nombre}"
        return f"{self.get_action_display()} - Nueva Cartilla"
    