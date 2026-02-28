from django.urls import path
from . import views

urlpatterns = [
    # Ruta raíz de la app para evitar el 404
    path('', views.dashboard, name='index'), 
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('producto/detalle/json/<int:pk>/', views.detalle_producto_json, name='detalle_producto_json'),
    path('reporte/inventario-pdf/', views.reporte_inventario_pdf, name='reporte_inventario_pdf'),
    
    # CRUD de Productos (Unidad 1 y 2)
    path('producto/nuevo/', views.crear_producto, name='crear_producto'),
    path('producto/<int:pk>/', views.detalle_producto, name='detalle_producto'),
    path('producto/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:pk>/', views.eliminar_producto_logico, name='eliminar_producto_logico'),
    path('productos/eliminados/', views.productos_eliminados, name='productos_eliminados'),
    path('productos/reactivar/<int:pk>/', views.reactivar_producto, name='reactivar_producto'),
    
    # Movimientos y Stock
    path('movimientos/historial/', views.lista_movimientos, name='lista_movimientos'),
    path('movimiento/detalle/<int:pk>/', views.detalle_movimiento, name='detalle_movimiento'),
    path('movimiento/', views.registrar_movimiento, name='registrar_movimiento'),
    path('movimientos/editar/<int:pk>/', views.editar_movimiento, name='editar_movimiento'),
    path('movimientos/eliminar/<int:pk>/', views.eliminar_movimiento, name='eliminar_movimiento'),
    path('movimientos/anulados/', views.movimientos_anulados, name='movimientos_anulados'),
    path('movimientos/restaurar/<int:pk>/', views.restaurar_movimiento, name='restaurar_movimiento'),
    
    # CRUD categorias
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/detalle/<int:pk>/', views.detalle_categoria, name='detalle_categoria'),
    path('categoria/json/<int:pk>/', views.detalle_categoria_json, name='detalle_categoria_json'),
    path('categorias/crear/', views.crear_categoria, name='crear_categoria'),
    path('categorias/editar/<int:pk>/', views.editar_categoria, name='editar_categoria'),
    path('categorias/eliminar/<int:pk>/', views.eliminar_categoria, name='eliminar_categoria'),
    
    # Reportes y Exportación
    path('exportar/excel/', views.exportar_excel, name='exportar_excel'),
    path('exportar/pdf/', views.exportar_pdf, name='exportar_pdf'), 
    path('reporte/ventas-pdf/', views.reporte_ventas_pdf, name='reporte_ventas_pdf'),
    
    #CRUD Proveedores
    path('proveedores/', views.lista_proveedores, name='lista_proveedores'),
    path('proveedor/json/<int:pk>/', views.detalle_proveedor_json, name='detalle_proveedor_json'),
    path('proveedor/detalle/<int:pk>/', views.detalle_proveedor, name='detalle_proveedor'),
    path('proveedores/crear/', views.crear_proveedor, name='crear_proveedor'),
    path('proveedores/editar/<int:pk>/', views.editar_proveedor, name='editar_proveedor'),
    path('proveedores/eliminar/<int:pk>/', views.eliminar_proveedor, name='eliminar_proveedor'),
    
    #PEDIDOS # Vistas de Cliente (Scoping)
    path('catalogo/', views.catalogo_cliente, name='catalogo_cliente'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('gestion-pedidos/', views.gestion_pedidos, name='gestion_pedidos'),
    path('pedidos/detalle/<int:pk>/', views.detalle_pedido, name='detalle_pedido'),
    path('cambiar-estado-pedido/<int:pedido_id>/<str:nuevo_estado>/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
    path('crear-pedido/', views.crear_pedido, name='crear_pedido'),
    path('pedido/aprobar/<int:pedido_id>/', views.aprobar_pedido, name='aprobar_pedido'),
    path('pedido/rechazar/<int:pedido_id>/', views.rechazar_pedido, name='rechazar_pedido'),
    path('pedido/pdf/<int:pedido_id>/', views.generar_pdf_pedido, name='generar_pdf_pedido'),
]