from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Producto

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
