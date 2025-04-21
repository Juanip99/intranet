from django.contrib import admin
from django.urls import reverse, path
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin
from .models import Cartilla
from .forms import CartillaCreateForm, CartillaEditForm, CartillaAgregarForm
from .views import revert_change, history_view, especialidades_centros, agregar_especialidades
from django.db.models import CharField, Func, OuterRef, Subquery, Value, Case, When
from django.db.models.functions import Concat, Substr

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
                especialidades_agrupadas=Subquery(subquery),
                repetidos=Case(
                    When(
                        especialidad=Substr(Subquery(subquery), 1, Func(Subquery(subquery), function='LOCATE', template="%(function)s(',', %(expressions)s) - 1")),
                        then=Value(0)
                    ),
                    default=Value(1),
                    output_field=CharField()
                )
            ).filter(repetidos=0)
        return queryset

class CartillaAdmin(SimpleHistoryAdmin):
    list_display = (
        'nombre_link', 
        'get_especialidad',  # Mostrar la columna especialidad
        'get_especialidades_agrupadas', 
        'tipo_cartilla', 
        'ver_mas', 
        'editar',
        'agregar_especialidades',  # Nuevo botón
        'eliminar', 
        'history_button'
    )
    list_filter = ('especialidad', 'tipo_cartilla', 'provincia','barrio_localidad', AgruparEspecialidadesFilter)  # Ocultar barrio_localidad y provincia temporalmente
    list_per_page = 25  # Mostrar 25 registros por página por defecto
    form = CartillaCreateForm  # Asociar el formulario personalizado con el modelo
    change_form_template = 'admin/cartilla/change_form.html'  # Usar la plantilla personalizada

    def get_list_display(self, request):
        if request.GET.get('agrupar_especialidades') == 'yes':
            return (
                'nombre_link', 
                'get_especialidades_agrupadas', 
                'tipo_cartilla', 
                'get_repetidos', 
                'ver_mas', 
                'editar', 
                'agregar_especialidades',  # Nuevo botón
                'eliminar', 
                'history_button'
            )
        else:
            return (
                'nombre_link', 
                'get_especialidad', 
                'tipo_cartilla', 
                'get_repetidos', 
                'ver_mas', 
                'editar', 
                'agregar_especialidades',  # Nuevo botón
                'eliminar', 
                'history_button'
            )

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            kwargs['form'] = CartillaCreateForm
        else:
            kwargs['form'] = CartillaEditForm
        return super(CartillaAdmin, self).get_form(request, obj, **kwargs)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.order_by('-id')

    def nombre_link(self, obj):
        return format_html('<a href="{}">{}</a>', reverse('ver_cartilla', args=[obj.id]), obj.nombre)
    nombre_link.short_description = 'Nombre'
    nombre_link.allow_tags = True

    def ver_mas(self, obj):
        return format_html('<a class="button" href="{}">Ver</a>', reverse('ver_cartilla', args=[obj.id]))
    ver_mas.short_description = 'Ver'
    ver_mas.allow_tags = True

    def editar(self, obj):
        return format_html('<a class="button" href="{}">Editar</a>', reverse('admin:cartilla_cartilla_change', args=[obj.id]))
    editar.short_description = 'Editar'
    editar.allow_tags = True

    def agregar_especialidades(self, obj):
        return format_html('<a class="button" href="{}">Agregar Especialidades</a>', reverse('admin:agregar_especialidades', args=[obj.id]))
    agregar_especialidades.short_description = 'Agregar Especialidades'
    agregar_especialidades.allow_tags = True

    def eliminar(self, obj):
        return format_html('<a class="button" href="{}">Eliminar</a>', reverse('admin:cartilla_cartilla_delete', args=[obj.id]))
    eliminar.short_description = 'Eliminar'
    eliminar.allow_tags = True

    def history_button(self, obj):
        return format_html('<a class="button" href="{}">Historial</a>', reverse('admin:%s_%s_history' % (obj._meta.app_label, obj._meta.model_name), args=[obj.id]))
    history_button.short_description = 'Historial'
    history_button.allow_tags = True

    def get_especialidades_agrupadas(self, obj):
        return getattr(obj, 'especialidades_agrupadas', None)
    get_especialidades_agrupadas.short_description = 'Especialidades Agrupadas'

    def get_especialidad(self, obj):
        return obj.especialidad
    get_especialidad.short_description = 'Especialidad'

    def get_repetidos(self, obj):
        return getattr(obj, 'repetidos', None)
    get_repetidos.short_description = 'Repetidos'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('revert_change/<int:history_id>/', self.admin_site.admin_view(revert_change), name='revert_change'),
            path('history/', self.admin_site.admin_view(history_view), name='cartilla_history'),
            path('especialidades-centros/', self.admin_site.admin_view(especialidades_centros), name='especialidades_centros'),
            path('agregar_especialidades/<int:cartilla_id>/', self.admin_site.admin_view(agregar_especialidades), name='agregar_especialidades'),  # Nueva URL
        ]
        return custom_urls + urls

    def especialidades_centros_link(self, request):
        url = reverse('admin:especialidades_centros')
        return format_html('<a class="button" href="{}">Especialidades de Centros</a>', url)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['especialidades_centros_link'] = self.especialidades_centros_link(request)
        extra_context['agrupar_especialidades'] = request.GET.get('agrupar_especialidades', False)
        
        # Verificar si se debe agrupar
        if request.GET.get('agrupar_especialidades') == 'yes':
            subquery = Cartilla.objects.filter(
                nombre=OuterRef('nombre'),
                domicilio=OuterRef('domicilio')
            ).values('nombre').annotate(
                especialidades_agrupadas=GroupConcat('especialidad', separator=',')
            ).values('especialidades_agrupadas')
            
            queryset = self.get_queryset(request)
            queryset = queryset.annotate(
                especialidades_agrupadas=Subquery(subquery),
                repetidos=Case(
                    When(
                        especialidad=Substr(Subquery(subquery), 1, Func(Subquery(subquery), function='LOCATE', template="%(function)s(',', %(expressions)s) - 1")),
                        then=Value(0)
                    ),
                    default=Value(1),
                    output_field=CharField()
                )
            ).filter(repetidos=0)

        response = super(CartillaAdmin, self).changelist_view(request, extra_context=extra_context)
        if request.GET.get('agrupar_especialidades') == 'yes':
            response.context_data['cl'].queryset = queryset

        return response


class CartillaHistoryAdmin(admin.ModelAdmin):
    list_display = ('history_date', 'history_user', 'history_type', 'get_changes', 'revert_button')
    list_filter = ('history_date', 'history_user', 'history_type')
    search_fields = ('history_user__username', 'history_user__email')
    verbose_name_plural = 'Historial de Cambios'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.order_by('-history_date')

    def get_changes(self, obj):
        if obj.prev_record:
            delta = obj.diff_against(obj.prev_record)
            changes = []
            for change in delta.changes:
                changes.append(f"{change.field}: {change.old} → {change.new}")
            return ", ".join(changes)
        return "No previous record"
    get_changes.short_description = 'Changes'

    def revert_button(self, obj):
        return format_html('<a class="button" href="{}">Revertir</a>', reverse('admin:revert_change', args=[obj.pk]))
    revert_button.short_description = 'Revertir'
    revert_button.allow_tags = True

admin.site.register(Cartilla, CartillaAdmin)

# Register the historical model with a custom admin class
admin.site.register(Cartilla.history.model, CartillaHistoryAdmin)