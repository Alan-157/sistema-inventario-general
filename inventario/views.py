from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from .models import Producto
from .forms import MovimientoForm, ProductoForm

def lista_productos(request):
    # Obtenemos todos los productos. 
    # Usamos select_related para traer la categoría en una sola consulta SQL (Optimización)
    productos_list = Producto.objects.select_related('categoria').all().order_by('-fecha_creacion')
    # 'select_related' hace un JOIN en SQL para traer la categoría rápido
    # sin hacer múltiples consultas a la base de datos (Optimización clave)
    
    # Paginación: Mostramos solo 20 productos por página
    paginator = Paginator(productos_list, 20) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'inventario/lista_productos.html', {'page_obj': page_obj})

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

def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    
    return render(request, 'inventario/crear_producto.html', {'form': form})