from .models import Producto
from django.db.models import F

def notificaciones_stock(request):
    if request.user.is_authenticated and request.user.rol != 'CLIENTE':
        # Contamos cuántos productos están por debajo del mínimo
        cantidad = Producto.objects.filter(
            is_active=True, 
            stock_actual__lte=F('stock_minimo')
        ).count()
        return {'cantidad_criticos': cantidad}
    return {'cantidad_criticos': 0}