from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db import models
from .models import Producto, HistorialMovimiento, Categoria, Proveedor
from django.contrib import messages
from django.db.models import F, Count, Q # Importante para comparar campos
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.template.loader import get_template
from .forms import ProductoForm, MovimientoForm
import openpyxl
from xhtml2pdf import pisa
import datetime

# --- SEGURIDAD Y DECORADORES ---

def es_admin_o_super(user):
    """Verifica si el usuario es ADMIN o SUPERUSUARIO según PPT U2-C4"""
    if user.rol in ['ADMIN', 'SUPERUSUARIO'] or user.is_superuser:
        return True
    raise PermissionDenied

# --- VISTAS DEL SISTEMA ---

@login_required
def dashboard(request):
    """Dashboard con gráficos y alertas de stock crítico"""
    total_productos = Producto.objects.filter(is_active=True).count()
    
    productos_criticos = Producto.objects.filter(
        is_active=True, 
        stock_actual__lte=F('stock_minimo')
    ).select_related('categoria')
    
    ultimos_movimientos = HistorialMovimiento.objects.select_related('producto', 'usuario').order_by('-created_at')[:5]

    datos_grafico = Producto.objects.filter(is_active=True).values('categoria__nombre').annotate(total=Count('id'))

    context = {
        'total_productos': total_productos,
        'cantidad_criticos': productos_criticos.count(),
        'productos_criticos': productos_criticos,
        'ultimos_movimientos': ultimos_movimientos,
        'datos_grafico': datos_grafico,
    }
    return render(request, 'inventario/dashboard.html', context)

@login_required
def lista_productos(request):
    """Listado con filtros avanzados y paginación"""
    productos = Producto.objects.filter(is_active=True).select_related('categoria', 'proveedor')
    categorias = Categoria.objects.all()
    proveedores = Proveedor.objects.all()

    query = request.GET.get('q', '')
    cat_id = request.GET.get('categoria', '')
    prov_id = request.GET.get('proveedor', '')
    precio_min = request.GET.get('min_precio', '')
    precio_max = request.GET.get('max_precio', '')

    if query:
        productos = productos.filter(Q(nombre__icontains=query) | Q(sku__icontains=query))
    if cat_id:
        productos = productos.filter(categoria_id=cat_id)
    if prov_id:
        productos = productos.filter(proveedor_id=prov_id)
    if precio_min:
        productos = productos.filter(precio_venta__gte=precio_min)
    if precio_max:
        productos = productos.filter(precio_venta__lte=precio_max)

    paginator = Paginator(productos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'categorias': categorias,
        'proveedores': proveedores,
        'cat_seleccionada': cat_id,
        'prov_seleccionado': prov_id,
        'precio_min': precio_min,
        'precio_max': precio_max,
    }
    return render(request, 'inventario/lista_productos.html', context)

@login_required
@user_passes_test(es_admin_o_super)
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Producto creado con éxito!")
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    
    # Pasamos 'editando' en False para el título del template
    return render(request, 'inventario/crear_producto.html', {'form': form, 'editando': False})

@login_required
@user_passes_test(es_admin_o_super)
def editar_producto(request, pk):
    """Edita un producto existente (Solo Admin/Super)"""
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f"Producto {producto.nombre} actualizado.")
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'inventario/crear_producto.html', {'form': form, 'editando': True})

@login_required
@user_passes_test(es_admin_o_super)
def desactivar_producto(request, pk):
    """Eliminación lógica (Soft Delete) (PPT U1-C6)"""
    producto = get_object_or_404(Producto, pk=pk)
    producto.is_active = False
    producto.save()
    messages.warning(request, f"El producto {producto.nombre} ha sido desactivado del inventario.")
    return redirect('lista_productos')

@login_required
def registrar_movimiento(request):
    """Gestiona entradas y salidas de stock (PPT U1-C9)"""
    # El Cliente no puede registrar movimientos
    if request.user.rol == 'CLIENTE':
        raise PermissionDenied

    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.usuario = request.user
            
            # Lógica atómica de actualización
            producto = movimiento.producto
            if movimiento.tipo == 'ENTRADA':
                producto.stock_actual += movimiento.cantidad
            elif movimiento.tipo in ['SALIDA', 'AJUSTE']:
                # Validación simple: No quedar en negativo
                if producto.stock_actual >= movimiento.cantidad:
                    producto.stock_actual -= movimiento.cantidad
                else:
                    messages.error(request, "No hay stock suficiente para esta salida.")
                    return render(request, 'inventario/registrar_movimiento.html', {'form': form})
            
            producto.save()
            movimiento.save()
            messages.success(request, "Movimiento registrado y stock actualizado.")
            return redirect('lista_productos')
    else:
        form = MovimientoForm()
    
    return render(request, 'inventario/registrar_movimiento.html', {'form': form})

@login_required
def exportar_excel(request):
    """Exportación masiva a Excel (Reportabilidad)"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Inventario"

    headers = ['SKU', 'Producto', 'Categoría', 'Stock', 'Precio Venta']
    ws.append(headers)

    productos = Producto.objects.filter(is_active=True).select_related('categoria')
    for p in productos:
        ws.append([p.sku, p.nombre, p.categoria.nombre, p.stock_actual, p.precio_venta])

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Inventario_General.xlsx"'
    wb.save(response)
    return response

@login_required
def exportar_pdf(request):
    """Genera reporte de inventario en PDF"""
    productos = Producto.objects.filter(is_active=True).select_related('categoria')
    fecha_actual = datetime.datetime.now()
    
    context = {
        'productos': productos,
        'fecha': fecha_actual,
        'usuario': request.user
    }
    
    template = get_template('inventario/reporte_pdf.html')
    html = template.render(context)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Reporte_Inventario.pdf"'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Error al generar PDF', status=500)
    return response

@login_required
@user_passes_test(es_admin_o_super)
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        # request.FILES es clave para las imágenes (Clase 10)
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f"Producto {producto.nombre} actualizado correctamente.")
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'inventario/crear_producto.html', {'form': form, 'editando': True})

@login_required
@user_passes_test(es_admin_o_super)
def desactivar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    # No borramos, desactivamos (Soft Delete)
    producto.is_active = False
    producto.save()
    messages.warning(request, f"Producto {producto.nombre} desactivado.")
    return redirect('lista_productos')

@login_required
def catalogo_cliente(request):
    """Vista de catálogo estilo tienda para el rol CLIENTE (U2 Clase 4)"""
    # Filtramos solo lo que el cliente debe ver
    productos = Producto.objects.filter(is_active=True, stock_actual__gt=0).select_related('categoria')
    
    return render(request, 'inventario/catalogo.html', {'productos': productos})

@login_required
def detalle_producto(request, pk):
    """Muestra la ficha técnica de un producto"""
    producto = get_object_or_404(Producto, pk=pk, is_active=True)
    return render(request, 'inventario/detalle_producto.html', {'producto': producto})