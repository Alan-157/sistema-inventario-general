from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    # Página principal del inventario: http://127.0.0.1:8000/inventario/
    path('movimiento/', views.registrar_movimiento, name='registrar_movimiento'),
    path('', views.lista_productos, name='lista_productos'),
    path('nuevo/', views.crear_producto, name='crear_producto'),
    path('editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('desactivar/<int:pk>/', views.desactivar_producto, name='desactivar_producto'),
    path('exportar/excel/', views.exportar_excel, name='exportar_excel'),
    path('editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('desactivar/<int:pk>/', views.desactivar_producto, name='desactivar_producto'),
    path('catalogo/', views.catalogo_cliente, name='catalogo_cliente'),
]