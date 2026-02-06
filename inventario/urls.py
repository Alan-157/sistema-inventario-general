from django.urls import path
from . import views

urlpatterns = [
    # Página principal del inventario: http://127.0.0.1:8000/inventario/
    path('', views.lista_productos, name='lista_productos'),
    path('movimiento/', views.registrar_movimiento, name='registrar_movimiento'),
    path('nuevo/', views.crear_producto, name='crear_producto'),
]