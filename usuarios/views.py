from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Usuario
from django.contrib import messages
from django.core.exceptions import PermissionDenied

"""def es_admin_o_super(user):
    
    "Permite acceso si el usuario es SUPERUSUARIO o ADMIN.
    El Superusuario siempre tiene permiso total (is_superuser)."
    
    if user.is_active and (user.rol in ['ADMIN', 'SUPERUSUARIO'] or user.is_superuser):
        return True
    raise PermissionDenied
    """

def solo_admin_o_super(user):
    # El Admin y Super pueden gestionar casi todo
    if user.rol in ['ADMIN', 'SUPERUSUARIO'] or user.is_superuser:
        return True
    raise PermissionDenied

def solo_superusuario(user):
    # Solo el Super puede ver configuraciones críticas
    if user.rol == 'SUPERUSUARIO' or user.is_superuser:
        return True
    raise PermissionDenied

def es_admin_o_super(user):
    return user.is_active and (user.rol in ['ADMIN', 'SUPERUSUARIO'] or user.is_superuser)

@login_required
@user_passes_test(es_admin_o_super)
def gestion_usuarios(request):
    # LÓGICA DE SCOPING (Clase 5): 
    # Si es ADMIN, filtramos para que NO vea a los SUPERUSUARIOS
    if request.user.rol == 'ADMIN':
        usuarios = Usuario.objects.exclude(rol='SUPERUSUARIO').exclude(is_superuser=True)
    else:
        # Si es SUPERUSUARIO, ve a todo el mundo
        usuarios = Usuario.objects.all()

    return render(request, 'usuarios/gestion_usuarios.html', {'usuarios': usuarios})

@login_required
@user_passes_test(es_admin_o_super)
def cambiar_rol(request, user_id):
    usuario_a_editar = get_object_or_404(Usuario, id=user_id)
    
    # Seguridad extra: Un ADMIN no puede cambiarle el rol a un SUPERUSUARIO
    if usuario_a_editar.rol == 'SUPERUSUARIO' and request.user.rol == 'ADMIN':
        raise PermissionDenied("No tienes permisos para modificar a un Superusuario.")
    
    if request.method == 'POST':
        nuevo_rol = request.POST.get('rol')
        usuario_a_editar.rol = nuevo_rol
        usuario_a_editar.save()
        messages.success(request, f"Rol de {usuario_a_editar.username} actualizado a {nuevo_rol}")
        return redirect('gestion_usuarios')
    
    return redirect('gestion_usuarios')
