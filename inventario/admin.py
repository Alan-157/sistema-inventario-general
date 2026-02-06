from django.contrib import admin
from .models import Categoria, Proveedor, Producto, HistorialMovimiento

# Configuración profesional para la tabla de Productos
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    # Columnas que se verán en la lista principal
    list_display = ('sku', 'nombre', 'categoria', 'stock_actual', 'precio_venta')
    # Buscador por nombre y SKU (Muy rápido gracias a los índices que creamos)
    search_fields = ('nombre', 'sku')
    # Filtros laterales para segmentar datos rápidamente
    list_filter = ('categoria', 'proveedor')
    # Orden por defecto: los más nuevos primero
    ordering = ('-fecha_creacion',)

# Registros simples para el resto de modelos
admin.site.register(Categoria)
admin.site.register(Proveedor)
admin.site.register(HistorialMovimiento)
