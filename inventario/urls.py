from django.urls import path
from . import views

urlpatterns = [
    # Dashboard e Inicio
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.lista_productos, name='lista_productos'),
    
    # CRUD de Productos (Unidad 1 y 2)
    path('producto/nuevo/', views.crear_producto, name='crear_producto'),
    path('producto/<int:pk>/', views.detalle_producto, name='detalle_producto'),
    path('producto/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('producto/desactivar/<int:pk>/', views.desactivar_producto, name='desactivar_producto'),
    
    # Movimientos y Stock
    path('movimiento/', views.registrar_movimiento, name='registrar_movimiento'),
    
    # Vistas de Cliente (Scoping)
    path('catalogo/', views.catalogo_cliente, name='catalogo_cliente'),
    
    # Reportes y Exportación
    path('exportar/excel/', views.exportar_excel, name='exportar_excel'),
    path('exportar/pdf/', views.exportar_pdf, name='exportar_pdf'), # <--- Esta es la ruta que faltaba
]