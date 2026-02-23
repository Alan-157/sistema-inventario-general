from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
import openpyxl
from django.http import HttpResponse
from django.contrib import messages
from django.db import models  # <--- AGREGA ESTA LÍNEA
from .models import Producto, HistorialMovimiento
from .forms import MovimientoForm, ProductoForm

# Función de prueba para verificar si es ADMIN
def es_admin(user):
    if user.rol == 'ADMIN':
        return True
    raise PermissionDenied # Lanza un error 403 si no es admin

@login_required
def dashboard(request):
    # Contamos el total de productos para las tarjetas del dashboard
    total_productos = Producto.objects.count()
    
    # Aquí es donde fallaba porque no encontraba 'models'
    productos_criticos = Producto.objects.filter(stock_actual__lte=models.F('stock_minimo'))
    
    # Obtenemos los últimos 5 movimientos para mostrar actividad reciente
    ultimos_movimientos = HistorialMovimiento.objects.select_related('producto', 'usuario').order_by('-fecha')[:5]
    
    context = {
        'total_productos': total_productos,
        'cantidad_criticos': productos_criticos.count(),
        'productos_criticos': productos_criticos,
        'ultimos_movimientos': ultimos_movimientos,
    }
    return render(request, 'inventario/dashboard.html', context)

@login_required
def registrar_movimiento(request):
    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.usuario = request.user # Registramos quién hizo el cambio
            
            # Lógica de actualización de stock
            producto = movimiento.producto
            if movimiento.tipo == 'ENTRADA':
                producto.stock_actual += movimiento.cantidad
            elif movimiento.tipo == 'SALIDA' or movimiento.tipo == 'AJUSTE':
                producto.stock_actual -= movimiento.cantidad
            
            producto.save() # Guardamos el nuevo stock en la DB
            movimiento.save() # Guardamos el registro en el historial
            return redirect('lista_productos')
    else:
        form = MovimientoForm()
    
    return render(request, 'inventario/registrar_movimiento.html', {'form': form})

@login_required
def lista_productos(request):
    # Capturamos el valor de búsqueda desde el navegador
    query = request.GET.get('q')
    
    # Iniciamos la consulta base con optimización de relación (JOIN SQL)
    productos_list = Producto.objects.select_related('categoria').filter(is_active=True).order_by('-created_at')
    
    # Si hay una búsqueda, filtramos por nombre o SKU (insensible a mayúsculas)
    if query:
        productos_list = productos_list.filter(
            models.Q(nombre__icontains=query) | models.Q(sku__icontains=query)
        )
    
    # Paginación (se mantiene para no saturar la memoria)
    paginator = Paginator(productos_list, 20) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'inventario/lista_productos.html', {
        'page_obj': page_obj,
        'query': query  # Devolvemos el texto buscado para que no se borre del cuadro
    })


@login_required
@user_passes_test(es_admin)
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'inventario/crear_producto.html', {'form': form})

@login_required
def exportar_excel(request):
    # Creamos el libro de Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Inventario General"

    # Definimos los encabezados
    headers = ['SKU', 'Nombre', 'Categoría', 'Stock Actual', 'Precio Venta', 'Proveedor']
    ws.append(headers)

    # Obtenemos los productos (optimizado con select_related)
    productos = Producto.objects.select_related('categoria', 'proveedor').all()

    for p in productos:
        ws.append([
            p.sku, 
            p.nombre, 
            p.categoria.nombre, 
            p.stock_actual, 
            p.precio_venta, 
            p.proveedor.nombre if p.proveedor else "N/A"
        ])

    # Preparamos la respuesta del navegador para descargar el archivo
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Inventario_General.xlsx"'
    wb.save(response)
    return response

# VISTA PARA EDITAR
@login_required
@user_passes_test(es_admin)
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f"Producto '{producto.nombre}' actualizado con éxito.")
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'inventario/crear_producto.html', {'form': form, 'editando': True})

# VISTA PARA DESACTIVAR (SOFT DELETE)
@login_required
@user_passes_test(es_admin)
def desactivar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    producto.is_active = False
    producto.save()
    messages.warning(request, f"El producto '{producto.nombre}' ha sido desactivado.")
    return redirect('lista_productos')