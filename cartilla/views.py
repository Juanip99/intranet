from django.shortcuts import render, get_object_or_404, HttpResponse, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.views.generic import ListView, DetailView
from .models import Cartilla
from .forms import CartillaFilterForm, CartillaAgregarForm
from .decorators import staff_required
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.template.loader import get_template
from django.conf import settings
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
import os
from django.contrib import messages
from django.utils.decorators import method_decorator

# Vistas del sitio
@login_required
@staff_required
def index(request):
    return render(request, 'index.html')
def enlaces_utiles(request):
    return render(request, 'cartilla/links.html')

@login_required
@staff_required
def filtro_cartilla(request):
    form = CartillaFilterForm(request.GET or None)
    results = Cartilla.objects.all()
    if form.is_valid():
        provincia = form.cleaned_data.get('provincia')
        barrio_localidad = form.cleaned_data.get('barrio_localidad')
        especialidad = form.cleaned_data.get('especialidad')
        tipo_cartilla = form.cleaned_data.get('tipo_cartilla')
        if provincia:
            results = results.filter(provincia=provincia)
        if barrio_localidad:
            results = results.filter(barrio_localidad=barrio_localidad)
        if especialidad:
            results = results.filter(especialidad=especialidad)
        if tipo_cartilla:
            results = results.filter(tipo_cartilla=tipo_cartilla)
    paginator = Paginator(results, request.GET.get('page_size', 25))
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    results_list = list(page_obj.object_list.values('id', 'nombre', 'provincia', 'barrio_localidad', 'especialidad', 'tipo_cartilla'))
    return JsonResponse({
        'results': results_list,
        'page': page_obj.number,
        'num_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
        'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
    })

@login_required
@staff_required
def filtro_opciones(request):
    provincia = request.GET.get('provincia')
    barrio_localidad = request.GET.get('barrio_localidad')
    especialidad = request.GET.get('especialidad')
    tipo_cartilla = request.GET.get('tipo_cartilla')

    cartillas = Cartilla.objects.all()
    if provincia:
        cartillas = cartillas.filter(provincia=provincia)
    if barrio_localidad:
        cartillas = cartillas.filter(barrio_localidad=barrio_localidad)
    if especialidad:
        cartillas = cartillas.filter(especialidad=especialidad)
    if tipo_cartilla:
        cartillas = cartillas.filter(tipo_cartilla=tipo_cartilla)

    provincias = sorted(cartillas.values_list('provincia', flat=True).distinct())
    barrios = sorted(cartillas.values_list('barrio_localidad', flat=True).distinct())
    especialidades = sorted(cartillas.values_list('especialidad', flat=True).distinct())
    tipos_cartilla = sorted(cartillas.values_list('tipo_cartilla', flat=True).distinct())

    data = {
        'provincias': list(provincias),
        'barrios': list(barrios),
        'especialidades': list(especialidades),
        'tipos_cartilla': list(tipos_cartilla),
    }
    return JsonResponse(data)

class CartillaListado(ListView):
    model = Cartilla
    template_name = 'cartilla/cartilla.html'
    context_object_name = 'cartillas'
    paginate_by = 25

    @method_decorator(login_required)
    @method_decorator(staff_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = CartillaFilterForm(self.request.GET or None)
        context['form'] = form
        context['page_size'] = self.get_paginate_by(self.get_queryset())
        return context

    def get_queryset(self):
        queryset = Cartilla.objects.all()
        form = CartillaFilterForm(self.request.GET or None)
        if form.is_valid():
            provincia = form.cleaned_data.get('provincia')
            barrio_localidad = form.cleaned_data.get('barrio_localidad')
            especialidad = form.cleaned_data.get('especialidad')
            tipo_cartilla = form.cleaned_data.get('tipo_cartilla')
            if provincia:
                queryset = queryset.filter(provincia=provincia)
            if barrio_localidad:
                queryset = queryset.filter(barrio_localidad=barrio_localidad)
            if especialidad:
                queryset = queryset.filter(especialidad=especialidad)
            if tipo_cartilla:
                queryset = queryset.filter(tipo_cartilla=tipo_cartilla)
        return queryset

class CartillaDetalle(DetailView):
    model = Cartilla
    template_name = 'cartilla/detalles.html'

    @method_decorator(login_required)
    @method_decorator(staff_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

@login_required
@staff_required
def cartilla_dinamica(request):
    return render(request, 'cartilla/cartilla_dinamica.html')

@login_required
@staff_required
def buscar_cartillas(request):
    search = request.GET.get('search', '')
    provincia = request.GET.get('provincia', '')
    localidad = request.GET.get('localidad', '')
    especialidad = request.GET.get('especialidad', '')
    domicilio = request.GET.get('domicilio', '')
    page = request.GET.get('page', 1)

    cartillas = Cartilla.objects.all()

    if search:
        cartillas = cartillas.filter(nombre__icontains=search)
    if provincia:
        cartillas = cartillas.filter(provincia__icontains=provincia)
    if localidad:
        cartillas = cartillas.filter(barrio_localidad__icontains=localidad)
    if especialidad:
        cartillas = cartillas.filter(especialidad__icontains=especialidad) | cartillas.filter(especialidades_originales__icontains=especialidad)
    if domicilio:
        cartillas = cartillas.filter(domicilio__icontains=domicilio)

    paginator = Paginator(cartillas, 10)  # 10 resultados por página
    page_obj = paginator.get_page(page)

    data = {
        'results': list(page_obj.object_list.values('id', 'nombre', 'provincia', 'barrio_localidad', 'especialidad', 'tipo_cartilla', 'domicilio')),
        'num_pages': paginator.num_pages,
        'page': page_obj.number,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
    }

    return JsonResponse(data)
@login_required
@staff_required
def generate_pdf(request):
    # Obtener los parámetros de la solicitud
    provincia = request.GET.get('provincia', '')
    barrio_localidad = request.GET.get('barrio_localidad', '')
    especialidad = request.GET.get('especialidad', '')
    tipo_cartilla = request.GET.get('tipo_cartilla', '')

    # Filtrar los datos según los parámetros
    cartillas = Cartilla.objects.all()
    if provincia:
        cartillas = cartillas.filter(provincia=provincia)
    if barrio_localidad:
        cartillas = cartillas.filter(barrio_localidad=barrio_localidad)
    if especialidad:
        cartillas = cartillas.filter(especialidad=especialidad)
    if tipo_cartilla:
        cartillas = cartillas.filter(tipo_cartilla=tipo_cartilla)

    # Ordenar los datos por tipo_cartilla (guardia primero), especialidad, barrio y luego por nombre
    cartillas = sorted(cartillas, key=lambda x: (
        x.tipo_cartilla != 'GUARDIA',  # Poner 'guardia' primero
        x.tipo_cartilla,               # Luego ordenar por tipo_cartilla alfabéticamente
        x.especialidad,                # Luego ordenar por especialidad alfabéticamente
        x.barrio_localidad,            # Luego ordenar por barrio alfabéticamente
        x.nombre                       # Finalmente ordenar por nombre alfabéticamente
    ))
    # Organizar los datos por provincia y especialidad
    data = {}
    for cartilla in cartillas:
        if cartilla.provincia not in data:
            data[cartilla.provincia] = {}
        if cartilla.especialidad not in data[cartilla.provincia]:
            data[cartilla.provincia][cartilla.especialidad] = []
        data[cartilla.provincia][cartilla.especialidad].append(cartilla)

    # Crear el PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=20, rightMargin=20, topMargin=50, bottomMargin=50)
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    blue_color = colors.HexColor('#4C7CA4')
    light_blue_color = colors.HexColor('#f8f9fa')


    # Logo, encabezado, pie de página y marca de agua
    def header_footer(canvas, doc):
        canvas.saveState()
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'uteplim_salud.jpg')
        watermark_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'ICONO.png')
        if os.path.exists(logo_path):
            canvas.drawImage(logo_path, 20, doc.pagesize[1] - 125, width=125, preserveAspectRatio=True, mask='auto')
        if os.path.exists(watermark_path):
            watermark = ImageReader(watermark_path)
            canvas.saveState()
            canvas.setFillAlpha(0.1)  # Ajustar la transparencia de la marca de agua
            canvas.drawImage(watermark, 0, 0, width=doc.pagesize[0], height=doc.pagesize[1], mask='auto')
            canvas.restoreState()
        canvas.setFont('Helvetica-Bold', 18)
        canvas.setFillColor(colors.HexColor('#4C7CA4'))   # Color del encabezado
        canvas.drawCentredString(doc.pagesize[0] / 2.0, doc.pagesize[1] - 40, "CARTILLA UTEPLIM SALUD")
        canvas.setFont('Helvetica', 8)
        canvas.setFillColorRGB(51/255, 51/255, 51/255)  # Color del texto del footer
        canvas.drawCentredString(doc.pagesize[0] / 2.0, 40, "0800-3450-861")
        canvas.drawCentredString(doc.pagesize[0] / 2.0, 30, "Lunes a Viernes de 10 a 16hs.")
        canvas.drawRightString(doc.pagesize[0] - 20, 40, f"Página {doc.page}")
        canvas.restoreState()


    # Tabla de datos
    for provincia, especialidades in data.items():
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(provincia, ParagraphStyle(name='Heading2', fontSize=14, textColor=blue_color, alignment=1, fontName='Helvetica-Bold')))
        elements.append(Spacer(1, 6))
        elements.append(HRFlowable(width="100%", thickness=2, lineCap='round', color=blue_color, spaceBefore=1, spaceAfter=1))  # Línea divisoria más gruesa
        for especialidad, items in especialidades.items():
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(especialidad, ParagraphStyle(name='Heading3', fontSize=12, textColor=blue_color, alignment=1, fontName='Helvetica-Bold')))
            elements.append(Spacer(1, 6))
            table_data = []
            for item in items:
                table_data.append([
                    Paragraph(item.nombre or '', styles['BodyText']),
                    Paragraph(item.domicilio or '', styles['BodyText']),
                    Paragraph(item.telefono or '', styles['BodyText']),
                    Paragraph(item.barrio_localidad or '', styles['BodyText'])
                ])
            table = Table(table_data, colWidths='*')
            table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#D3D3D3')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('WORDWRAP', (0, 0), (-1, -1), 'CJK'),
            ]))
            elements.append(table)

    doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)

    # Obtener el valor del buffer y crear la respuesta
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Cartilla_Uteplim.pdf"'
    response.write(pdf)
    return response

@login_required
@staff_required
def revert_change(request, history_id):
    
    history_instance = get_object_or_404(Cartilla.history.model, pk=history_id)
    if history_instance.prev_record:
        history_instance.prev_record.instance.save()
        messages.success(request, "Los cambios han sido revertidos.")
    else:
        messages.error(request, "No se puede revertir este cambio.")
    return redirect(request.META.get('HTTP_REFERER', 'admin:cartilla_cartilla_changelist'))

@login_required
@staff_required
def history_view(request):
    history_list = Cartilla.history.all().order_by('-history_date')
    changes = []
    for history in history_list:
        if history.prev_record:
            delta = history.diff_against(history.prev_record)
            for change in delta.changes:
                changes.append({
                    'field': change.field,
                    'old': change.old,
                    'new': change.new,
                    'history_date': history.history_date,
                    'history_user': history.history_user,
                    'history_type': history.get_history_type_display(),
                    'revert_url': reverse('admin:revert_change', args=[history.id])
                })
    context = {
        'changes': changes,
        'opts': Cartilla._meta,
    }
    return render(request, 'admin/cartilla/history_view.html', context)
def agregar_especialidades(request, cartilla_id):
    cartilla = get_object_or_404(Cartilla, id=cartilla_id)
    if request.method == 'POST':
        form = CartillaAgregarForm(request.POST)
        if form.is_valid():
            especialidades = form.cleaned_data['especialidad']
            for especialidad in especialidades:
                Cartilla.objects.create(
                    procedencia_convenio=cartilla.procedencia_convenio,
                    tipo_cartilla=cartilla.tipo_cartilla,
                    matricula=cartilla.matricula,
                    especialidad=especialidad,
                    nombre=cartilla.nombre,
                    domicilio=cartilla.domicilio,
                    telefono=cartilla.telefono,
                    barrio_localidad=cartilla.barrio_localidad,
                    provincia=cartilla.provincia,
                    centro_de_atencion=cartilla.centro_de_atencion,
                    cuit=cartilla.cuit,
                    habilitado=cartilla.habilitado,
                    email=cartilla.email,
                    solo_derivacion=cartilla.solo_derivacion,
                    especialidades_originales=cartilla.especialidades_originales
                )
            return redirect(reverse('admin:cartilla_cartilla_changelist'))
    else:
        initial_data = {
            'procedencia_convenio': cartilla.procedencia_convenio,
            'tipo_cartilla': cartilla.tipo_cartilla,
            'matricula': cartilla.matricula,
            'nombre': cartilla.nombre,
            'domicilio': cartilla.domicilio,
            'telefono': cartilla.telefono,
            'barrio_localidad': cartilla.barrio_localidad,
            'provincia': cartilla.provincia,
            'centro_de_atencion': cartilla.centro_de_atencion,
            'cuit': cartilla.cuit,
            'habilitado': cartilla.habilitado,
            'email': cartilla.email,
            'solo_derivacion': cartilla.solo_derivacion,
            'especialidades_originales': cartilla.especialidades_originales
        }
        form = CartillaAgregarForm(initial=initial_data)
    return render(request, 'admin/cartilla/agregar_especialidades.html', {'form': form, 'cartilla': cartilla})
# Vistas de administración de Django
@login_required
@staff_required
def especialidades_centros(request):
    return render(request, 'cartilla/especialidades_centros.html')

@login_required
@staff_required
def buscar_especialidades_centros(request):
    search = request.GET.get('search', '')
    page = request.GET.get('page', 1)

    cartillas = Cartilla.objects.all()

    if search:
        cartillas = cartillas.filter(nombre__icontains=search)

    # Ordenar alfabeticamente por nombre
    cartillas = cartillas.order_by('nombre')

    # Combinar filas con el mismo nombre y domicilio
    combined_cartillas = {}
    for cartilla in cartillas:
        key = (cartilla.nombre, cartilla.domicilio)
        if key not in combined_cartillas:
            combined_cartillas[key] = {
                'nombre': cartilla.nombre,
                'provincia': cartilla.provincia,
                'barrio_localidad': cartilla.barrio_localidad,
                'especialidades': cartilla.especialidad,
                'tipo_cartilla': cartilla.tipo_cartilla,
                'domicilio': cartilla.domicilio,
                'id': cartilla.id
            }
        else:
            combined_cartillas[key]['especialidades'] += f", {cartilla.especialidad}"

    combined_cartillas_list = list(combined_cartillas.values())

    paginator = Paginator(combined_cartillas_list, 10)  # 10 resultados por página
    page_obj = paginator.get_page(page)

    data = {
        'results': page_obj.object_list,
        'num_pages': paginator.num_pages,
        'page': page_obj.number,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
    }

    return JsonResponse(data)

@login_required
@staff_required
def ver_cartilla(request, pk):
    cartilla = get_object_or_404(Cartilla, pk=pk)
    return render(request, 'cartilla/detalles.html', {'object': cartilla})