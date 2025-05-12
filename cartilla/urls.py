from django.urls import path
from . import views, autocomplete
from .views import CartillaListado, CartillaDetalle, filtro_cartilla, filtro_opciones, ver_cartilla, cartilla_dinamica, buscar_cartillas, generate_pdf, enlaces_utiles, historial_cartilla

urlpatterns = [
    path('', CartillaListado.as_view(), name='leer'),
    path('detalle/<int:pk>', CartillaDetalle.as_view(), name='detalles'),
    path('filtro-cartilla/', filtro_cartilla, name='filtro_cartilla'),
    path('filtro-opciones/', filtro_opciones, name='ajax_filtro_opciones'),
    path('ver/<int:pk>', ver_cartilla, name='ver_cartilla'),
    path('cartilla-dinamica/', cartilla_dinamica, name='cartilla_dinamica'),
    path('buscar-cartillas/', buscar_cartillas, name='buscar_cartillas'),
    path('generate_pdf/', generate_pdf, name='generate_pdf'),
    path('provincia-autocomplete/', autocomplete.ProvinciaAutocomplete.as_view(), name='provincia-autocomplete'),
    path('barrio-localidad-autocomplete/', autocomplete.BarrioLocalidadAutocomplete.as_view(), name='barrio-localidad-autocomplete'),
    path('especialidad-autocomplete/', autocomplete.EspecialidadAutocomplete.as_view(), name='especialidad-autocomplete'),
    path('enlaces-utiles/', enlaces_utiles, name='enlaces_utiles'),
    path('historial/<int:cartilla_id>/', historial_cartilla, name='cartilla_history'),

]