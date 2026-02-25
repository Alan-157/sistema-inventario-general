from django.urls import path
from . import views

urlpatterns = [
    path('gestion/', views.gestion_usuarios, name='gestion_usuarios'),
    path('crear/', views.crear_usuario, name='crear_usuario'),
    path('editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),
    path('cambiar-rol/<int:user_id>/', views.cambiar_rol, name='cambiar_rol'),
    path('registrar/', views.registrar_usuario, name='registrar'),
]