from django.contrib import admin, messages
from django.contrib.auth.models import User
from django.urls import reverse, path
from django.utils.html import format_html
from django.utils import timezone
from .models import Cartilla, CartillaChangeRequest
from .forms import CartillaCreateForm, CartillaEditForm, CartillaAgregarForm
from .views import historial_cartilla, agregar_especialidades
from django.db.models import CharField, Func, OuterRef, Subquery, Value, Case, When
from django.db.models.functions import Concat, Substr
from django.db import connection  


class GroupConcat(Func):
    function = 'GROUP_CONCAT'
    template = '%(function)s(%(expressions)s SEPARATOR "%(separator)s")'

    def __init__(self, expression, separator=',', **extra):
        super().__init__(expression, separator=separator, output_field=CharField(), **extra)

class AgruparEspecialidadesFilter(admin.SimpleListFilter):
    title = 'Agrupar Especialidades'
    parameter_name = 'agrupar_especialidades'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Sí'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        queryset = queryset.order_by('provincia', 'barrio_localidad', 'nombre')
        if self.value() == 'yes':
            subquery = Cartilla.objects.filter(
                nombre=OuterRef('nombre'),
                domicilio=OuterRef('domicilio')
            ).values('nombre').annotate(
                especialidades_agrupadas=GroupConcat('especialidad', separator=',')
            ).values('especialidades_agrupadas')
            queryset = queryset.annotate(
                especialidades_agrupadas=Subquery(subquery)
            )
            combinaciones_vistas = set()
            ids_unicos = []
            for obj in queryset:
                key = (obj.nombre)
                if key not in combinaciones_vistas:
                    combinaciones_vistas.add(key)
                    ids_unicos.append(obj.id)
            return queryset.filter(id__in=ids_unicos)
        return queryset

class CartillaAdmin(admin.ModelAdmin):
    list_display = (
        'nombre_link', 
        'get_especialidad', 
        'tipo_cartilla', 
        'barrio_localidad', 
        'ver_mas', 
        'editar', 
        'agregar_especialidades', 
        'eliminar', 
        'history_button'
    )
    list_filter = ('especialidad', 'tipo_cartilla', 'provincia', 'barrio_localidad', AgruparEspecialidadesFilter)
    list_per_page = 25
    form = CartillaEditForm
    
    def save_model(self, request, obj, form, change):
        if change:  # Si se está editando un objeto existente
            if not isinstance(request.user, User):
                messages.error(request, "No se pudo registrar la solicitud porque el usuario no está autenticado.")
                return
    
            for field in form.changed_data:
                with connection.cursor() as cursor:
                    # Obtener el valor antiguo directamente desde la base de datos
                    cursor.execute(f"SELECT {field} FROM cartilla_online WHERE id = %s", [obj.pk])
                    row = cursor.fetchone()
                    old_value = row[0] if row else ''  # Manejar valores nulos o inexistentes
    
                # Obtener el nuevo valor del formulario
                new_value = form.cleaned_data[field]
    
                if request.user.is_superuser:
                    # Si el usuario es superusuario, aplicar los cambios directamente
                    setattr(obj, field, new_value)
                    obj.save()
    
                    # Registrar el cambio como aprobado automáticamente
                    CartillaChangeRequest.objects.create(
                        cartilla=obj,
                        action='update',
                        field_name=field,
                        old_value=old_value,
                        new_value=new_value,
                        requested_by=request.user,
                        approved=True,  # Marcar como aprobado
                        approved_by=request.user,  # Aprobado por el superusuario
                        approved_at=timezone.now()  # Fecha de aprobación
                    )
                    messages.success(request, f"El campo '{field}' se actualizó automáticamente y se registró en el historial.")
                else:
                    # Crear una solicitud de cambio pendiente de aprobación
                    CartillaChangeRequest.objects.create(
                        cartilla=obj,
                        action='update',
                        field_name=field,
                        old_value=old_value,
                        new_value=new_value,
                        requested_by=request.user
                    )
            if not request.user.is_superuser:
                messages.info(request, "Los cambios se han registrado como una solicitud para su aprobación.")
        else:
            super().save_model(request, obj, form, change)
    def get_list_display(self, request):
        if request.GET.get('agrupar_especialidades') == 'yes':
            return (
                'nombre_link', 
                'get_especialidades_agrupadas', 
                'tipo_cartilla', 
                'barrio_localidad', 
                'ver_mas', 
                'editar', 
                'agregar_especialidades', 
                'eliminar', 
                'history_button'
            )
        else:
            return (
                'nombre_link', 
                'get_especialidad', 
                'tipo_cartilla', 
                'barrio_localidad', 
                'ver_mas', 
                'editar', 
                'eliminar', 
                'history_button'
            )

    def nombre_link(self, obj):
        return format_html('<a href="{}">{}</a>', reverse('ver_cartilla', args=[obj.id]), obj.nombre)
    nombre_link.short_description = 'Nombre'

    def ver_mas(self, obj):
        return format_html('<a class="button" href="{}">Ver</a>', reverse('ver_cartilla', args=[obj.id]))
    ver_mas.short_description = 'Ver'

    def editar(self, obj):
        return format_html('<a class="button" href="{}">Editar</a>', reverse('admin:cartilla_cartilla_change', args=[obj.id]))
    editar.short_description = 'Editar'

    def agregar_especialidades(self, obj):
        return format_html('<a class="button" href="{}">Agregar Especialidades</a>', reverse('admin:agregar_especialidades', args=[obj.id]))
    agregar_especialidades.short_description = 'Agregar Especialidades'

    def eliminar(self, obj):
        return format_html('<a class="button" href="{}">Eliminar</a>', reverse('admin:cartilla_cartilla_delete', args=[obj.id]))
    eliminar.short_description = 'Eliminar'

    def history_button(self, obj):
        return format_html('<a class="button" href="{}">Historial</a>', reverse('cartilla_history', args=[obj.id]))
    history_button.short_description = 'Historial'

    def get_especialidad(self, obj):
        return obj.especialidad
    get_especialidad.short_description = 'Especialidad'

    def get_especialidades_agrupadas(self, obj):
        return getattr(obj, 'especialidades_agrupadas', None)
    get_especialidades_agrupadas.short_description = 'Especialidades Agrupadas'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('historial/<int:cartilla_id>/', self.admin_site.admin_view(historial_cartilla), name='cartilla_history'),
            path('agregar_especialidades/<int:cartilla_id>/', self.admin_site.admin_view(agregar_especialidades), name='agregar_especialidades'),
        ]
        return custom_urls + urls

admin.site.register(Cartilla, CartillaAdmin)

class CartillaChangeRequestAdmin(admin.ModelAdmin):
    list_display = ('cartilla', 'action', 'field_name', 'old_value', 'new_value', 'requested_by', 'requested_at', 'approved', 'approved_by', 'approved_at')
    list_filter = ('action', 'approved', 'requested_by', 'approved_by')
    search_fields = ('cartilla__nombre', 'field_name', 'requested_by__username', 'approved_by__username')
    actions = ['approve_changes', 'reject_changes']

    def approve_changes(self, request, queryset):
        for change_request in queryset:
            if not change_request.approved:
                # Aplicar el cambio al modelo Cartilla
                setattr(change_request.cartilla, change_request.field_name, change_request.new_value)
                change_request.cartilla.save()

                # Marcar la solicitud como aprobada
                change_request.approved = True
                change_request.approved_by = request.user
                change_request.approved_at = timezone.now()
                change_request.save()

        self.message_user(request, "Los cambios seleccionados han sido aprobados.")
    approve_changes.short_description = "Aprobar cambios seleccionados"

    def reject_changes(self, request, queryset):
        for change_request in queryset:
            if not change_request.approved:
                # Marcar la solicitud como rechazada
                change_request.approved = False
                change_request.approved_by = request.user
                change_request.approved_at = timezone.now()
                change_request.save()

        self.message_user(request, "Los cambios seleccionados han sido rechazados.")
    reject_changes.short_description = "Rechazar cambios seleccionados"

# Registrar el modelo en el administrador
admin.site.register(CartillaChangeRequest, CartillaChangeRequestAdmin)