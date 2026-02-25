from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db import models
from .models import Producto, HistorialMovimiento, Categoria, Proveedor
from django.contrib import messages
from django.db.models import F, Count, Q # Importante para comparar campos
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse,HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_POST
from django.template.loader import get_template
from .forms import ProductoForm, MovimientoForm, CategoriaForm, ProveedorForm
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
    """Dashboard Dinámico: Muestra información diferente según el rol del usuario"""
    
    # ---------------------------------------------------------
    # 1. DASHBOARD PARA EL CLIENTE (Vitrina / Novedades)
    # ---------------------------------------------------------
    if request.user.rol == 'CLIENTE':
        # Traemos los últimos 4 productos agregados para mostrarlos como "Novedades"
        ultimos_productos = Producto.objects.filter(is_active=True, stock_actual__gt=0).order_by('-created_at')[:4]
        total_disponibles = Producto.objects.filter(is_active=True, stock_actual__gt=0).count()
        categorias_activas = Categoria.objects.annotate(num_prods=Count('producto')).filter(num_prods__gt=0).count()
        
        context_cliente = {
            'ultimos_productos': ultimos_productos,
            'total_disponibles': total_disponibles,
            'categorias_activas': categorias_activas,
        }
        return render(request, 'inventario/dashboard_cliente.html', context_cliente)

    # ---------------------------------------------------------
    # 2. DASHBOARD OPERATIVO (Admins, Superusuarios y Trabajadores)
    # ---------------------------------------------------------
    total_productos = Producto.objects.filter(is_active=True).count()
    
    productos_criticos = Producto.objects.filter(
        is_active=True, 
        stock_actual__lte=F('stock_minimo')
    ).select_related('categoria')
    
    ultimos_movimientos = HistorialMovimiento.objects.select_related('producto', 'usuario').order_by('-created_at')[:5]
    datos_grafico = Producto.objects.filter(is_active=True).values('categoria__nombre').annotate(total=Count('id'))

    context_operativo = {
        'total_productos': total_productos,
        'cantidad_criticos': productos_criticos.count(),
        'productos_criticos': productos_criticos,
        'ultimos_movimientos': ultimos_movimientos,
        'datos_grafico': datos_grafico,
    }
    return render(request, 'inventario/dashboard.html', context_operativo)

@login_required
def lista_productos(request):
    # 1. Recolectar datos de los filtros
    query = request.GET.get('q', '')
    cat_id = request.GET.get('categoria', '')
    prov_id = request.GET.get('proveedor', '')
    precio_min = request.GET.get('min_precio', '')
    precio_max = request.GET.get('max_precio', '')

    # 2. Queryset base (solo productos activos)
    productos = Producto.objects.filter(is_active=True).select_related('categoria', 'proveedor').order_by('nombre')

    # 3. Aplicar Filtros Dinámicos
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

    # 4. Paginación (10 productos por página)
    paginator = Paginator(productos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 5. Datos para los select del formulario
    categorias = Categoria.objects.all()
    proveedores = Proveedor.objects.all()

    context = {
        'page_obj': page_obj,
        'categorias': categorias,
        'proveedores': proveedores,
        'query': query,
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
@require_POST
def desactivar_producto(request, pk):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        producto = get_object_or_404(Producto, pk=pk)
        producto.is_active = False # Soft Delete
        producto.save()
        return JsonResponse({'ok': True, 'message': f'El producto {producto.nombre} ha sido desactivado.'})
    return JsonResponse({'ok': False}, status=400)

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

@login_required
def lista_movimientos(request):
    """Muestra el historial completo de entradas y salidas con búsqueda AJAX"""
    if request.user.rol == 'CLIENTE':
        raise PermissionDenied

    query = request.GET.get('q', '')
    movimientos = HistorialMovimiento.objects.select_related('producto', 'usuario').order_by('-created_at')
    
    # Si hay texto en el buscador, filtramos
    if query:
        movimientos = movimientos.filter(
            Q(producto__nombre__icontains=query) |
            Q(producto__sku__icontains=query) |
            Q(motivo__icontains=query)
        )

    # 1. RESPUESTA AJAX (Para la búsqueda en tiempo real)
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        data = []
        for mov in movimientos[:30]: # Limitamos a 30 resultados rápidos
            data.append({
                'fecha': mov.created_at.strftime("%d/%m/%Y %H:%M"),
                'producto_nombre': mov.producto.nombre,
                'producto_sku': mov.producto.sku,
                'producto_id': mov.producto.pk,
                'tipo': mov.tipo,
                'cantidad': mov.cantidad,
                'usuario': mov.usuario.username,
                'motivo': mov.motivo or "Sin motivo especificado"
            })
        return JsonResponse({'movimientos': data})

    # 2. RESPUESTA NORMAL (Cuando carga la página por primera vez)
    paginator = Paginator(movimientos, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'inventario/lista_movimientos.html', {'page_obj': page_obj, 'query': query})

@login_required
@user_passes_test(es_admin_o_super)
def lista_categorias(request):
    query = request.GET.get('q', '')
    
    # Obtenemos categorías y contamos cuántos productos tiene cada una
    categorias_list = Categoria.objects.annotate(
        num_productos=Count('producto')
    ).order_by('nombre')

    # Filtro de búsqueda
    if query:
        categorias_list = categorias_list.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query)
        )

    # Configuración del Paginador (5 por página)
    paginator = Paginator(categorias_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'inventario/lista_categorias.html', {
        'page_obj': page_obj,
        'query': query
    })

@login_required
@user_passes_test(es_admin_o_super)
def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría creada exitosamente.")
            return redirect('lista_categorias')
    else:
        form = CategoriaForm()
    return render(request, 'inventario/crear_categoria.html', {'form': form, 'editando': False})

@login_required
@user_passes_test(es_admin_o_super)
def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, f"Categoría '{categoria.nombre}' actualizada.")
            return redirect('lista_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'inventario/crear_categoria.html', {'form': form, 'editando': True})

@login_required
@require_POST
@user_passes_test(es_admin_o_super)
def eliminar_categoria(request, pk):
    if not request.headers.get("x-requested-with") == "XMLHttpRequest":
        return HttpResponseBadRequest("Solo AJAX")
    
    categoria = get_object_or_404(Categoria, pk=pk)
    
    # PROTECCIÓN: Si tiene productos, no se puede borrar
    if categoria.producto_set.count() > 0:
        return JsonResponse({
            "ok": False, 
            "message": "No puedes eliminar esta categoría porque tiene productos asociados."
        })
        
    nombre = categoria.nombre
    categoria.delete()
    return JsonResponse({"ok": True, "message": f"La categoría '{nombre}' ha sido eliminada."})

@login_required
@user_passes_test(es_admin_o_super)
def lista_proveedores(request):
    """Listado de proveedores con búsqueda y paginación real"""
    query = request.GET.get('q', '')
    
    # Obtenemos los proveedores y contamos sus productos
    proveedores_list = Proveedor.objects.annotate(
        num_productos=Count('producto')
    ).order_by('nombre')
    
    # Aplicamos filtro si existe búsqueda
    if query:
        proveedores_list = proveedores_list.filter(
            Q(nombre__icontains=query) | 
            Q(contacto__icontains=query)
        )
        
    # CONFIGURACIÓN DE PAGINACIÓN (Clase 9)
    # Mostraremos 5 por página para ver el efecto
    paginator = Paginator(proveedores_list, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'inventario/lista_proveedores.html', {
        'page_obj': page_obj, 
        'query': query
    })

@login_required
@user_passes_test(es_admin_o_super)
def crear_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Proveedor registrado exitosamente.")
            return redirect('lista_proveedores')
    else:
        form = ProveedorForm()
    return render(request, 'inventario/form_proveedor.html', {'form': form, 'editando': False})

@login_required
@user_passes_test(es_admin_o_super)
def editar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, f"Proveedor {proveedor.nombre} actualizado.")
            return redirect('lista_proveedores')
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'inventario/form_proveedor.html', {'form': form, 'editando': True})

@login_required
@require_POST
@user_passes_test(es_admin_o_super)
def eliminar_proveedor(request, pk):
    if not request.headers.get("x-requested-with") == "XMLHttpRequest":
        return HttpResponseBadRequest()
    
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if proveedor.producto_set.count() > 0:
        return JsonResponse({"ok": False, "message": "No se puede eliminar: tiene productos asociados."})
        
    proveedor.delete()
    return JsonResponse({"ok": True, "message": "Proveedor eliminado correctamente."})