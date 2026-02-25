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
    path('movimientos/historial/', views.lista_movimientos, name='lista_movimientos'),
    path('movimiento/', views.registrar_movimiento, name='registrar_movimiento'),
    
    # Vistas de Cliente (Scoping)
    path('catalogo/', views.catalogo_cliente, name='catalogo_cliente'),
    
    # CRUD categorias
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/crear/', views.crear_categoria, name='crear_categoria'),
    path('categorias/editar/<int:pk>/', views.editar_categoria, name='editar_categoria'),
    path('categorias/eliminar/<int:pk>/', views.eliminar_categoria, name='eliminar_categoria'),
    
    # Reportes y Exportación
    path('exportar/excel/', views.exportar_excel, name='exportar_excel'),
    path('exportar/pdf/', views.exportar_pdf, name='exportar_pdf'), 
    
    #CRUD Proveedores
    path('proveedores/', views.lista_proveedores, name='lista_proveedores'),
    path('proveedores/crear/', views.crear_proveedor, name='crear_proveedor'),
    path('proveedores/editar/<int:pk>/', views.editar_proveedor, name='editar_proveedor'),
    path('proveedores/eliminar/<int:pk>/', views.eliminar_proveedor, name='eliminar_proveedor'),
]