from django.urls import path
from django.contrib.auth import views as auth_views # Importamos las vistas nativas
from . import views

urlpatterns = [
    path('gestion/', views.gestion_usuarios, name='gestion_usuarios'),
    path('mi-perfil/', views.mi_perfil, name='mi_perfil'),
    path('crear/', views.crear_usuario, name='crear_usuario'),
    path('editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),
    path('cambiar-rol/<int:user_id>/', views.cambiar_rol, name='cambiar_rol'),
    path('registrar/', views.registrar_usuario, name='registrar'),
    path('gestion/toggle/<int:user_id>/', views.toggle_usuario_status, name='toggle_usuario'),
    
    path('password-reset/', 
        auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), 
        name='password_reset'),
    
    path('password-reset/done/', 
        auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), 
        name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), 
        name='password_reset_confirm'),
    
    path('password-reset-complete/', 
        auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), 
        name='password_reset_complete'),
]