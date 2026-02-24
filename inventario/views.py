from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db import models
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
import openpyxl

from .models import Producto, HistorialMovimiento
from .forms import MovimientoForm, ProductoForm

# --- SEGURIDAD Y DECORADORES ---

def es_admin_o_super(user):
    """Verifica si el usuario es ADMIN o SUPERUSUARIO según PPT U2-C4"""
    if user.rol in ['ADMIN', 'SUPERUSUARIO'] or user.is_superuser:
        return True
    raise PermissionDenied

# --- VISTAS DEL SISTEMA ---

@login_required
def dashboard(request):
    """Vista principal con alertas de stock crítico (PPT U1-C8)"""
    total_productos = Producto.objects.filter(is_active=True).count()
    
    # Uso de F() para comparar campos en la DB (Rendimiento optimizado)
    productos_criticos = Producto.objects.filter(
        is_active=True, 
        stock_actual__lte=models.F('stock_minimo')
    )
    
    ultimos_movimientos = HistorialMovimiento.objects.select_related(
        'producto', 'usuario'
    ).order_by('-fecha')[:5]
    
    context = {
        'total_productos': total_productos,
        'cantidad_criticos': productos_criticos.count(),
        'productos_criticos': productos_criticos,
        'ultimos_movimientos': ultimos_movimientos,
    }
    return render(request, 'inventario/dashboard.html', context)

@login_required
def lista_productos(request):
    """Listado con buscador y paginador (PPT U2-C9)"""
    query = request.GET.get('q')
    
    # Solo mostramos productos activos (Soft Delete)
    productos_list = Producto.objects.select_related('categoria').filter(is_active=True).order_by('-created_at')
    
    if query:
        # Consulta lógica Q para buscar en múltiples campos
        productos_list = productos_list.filter(
            models.Q(nombre__icontains=query) | models.Q(sku__icontains=query)
        )
    
    # Paginación de 10 en 10
    paginator = Paginator(productos_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'inventario/lista_productos.html', {
        'page_obj': page_obj,
        'query': query
    })

@login_required
@user_passes_test(es_admin_o_super)
def crear_producto(request):
    """Crea un nuevo producto (Solo Admin/Super)"""
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES) # request.FILES para fotos PPT U1-C10
        if form.is_valid():
            producto = form.save()
            messages.success(request, f"Producto {producto.nombre} creado exitosamente.")
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'inventario/crear_producto.html', {'form': form})

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