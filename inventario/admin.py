from django.contrib import admin
from .models import Categoria, Proveedor, Producto, HistorialMovimiento

# Configuración profesional para la tabla de Productos
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    # Cambia 'fecha_creacion' por 'created_at'
    list_display = ('nombre', 'sku', 'categoria', 'stock_actual', 'created_at') 
    
    # Cambia 'fecha_creacion' por 'created_at'
    ordering = ('-created_at',) 
    
    search_fields = ('nombre', 'sku')
    list_filter = ('categoria', 'is_active') # Añadimos is_active que es nuevo
