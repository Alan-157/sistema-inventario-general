from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Usuario
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .forms import RegistroUsuarioForm

def es_admin_o_super(user):
    return user.is_authenticated and (user.rol in ['ADMIN', 'SUPERUSUARIO'] or user.is_superuser)

@login_required
@user_passes_test(es_admin_o_super)
def gestion_usuarios(request):
    # Cambio: usamos request.user en lugar de user
    if request.user.rol == 'ADMIN':
        # El Admin no ve a los Superusuarios (Scoping - U2 Clase 5)
        usuarios = Usuario.objects.exclude(rol='SUPERUSUARIO').exclude(is_superuser=True)
    else:
        # El Superusuario ve a todo el mundo
        usuarios = Usuario.objects.all()
    
    return render(request, 'usuarios/gestion_usuarios.html', {'usuarios': usuarios})

@login_required
@user_passes_test(es_admin_o_super)
def cambiar_rol(request, user_id):
    usuario_a_editar = get_object_or_404(Usuario, id=user_id)
    
    # Seguridad: Admin no puede editar a un Super (U2 Clase 8)
    if usuario_a_editar.rol == 'SUPERUSUARIO' and request.user.rol == 'ADMIN':
        messages.error(request, "No tienes permiso para modificar a un Superusuario.")
        return redirect('gestion_usuarios')
    
    if request.method == 'POST':
        nuevo_rol = request.POST.get('rol')
        usuario_a_editar.rol = nuevo_rol
        usuario_a_editar.save()
        messages.success(request, f"El rol de {usuario_a_editar.username} ha sido actualizado.")
    
    return redirect('gestion_usuarios')

def registrar_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.rol = 'CLIENTE'  # Asignación automática de rol
            user.save()
            messages.success(request, f"Cuenta creada para {user.username}. Ya puedes iniciar sesión.")
            return redirect('login')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'registration/registrar.html', {'form': form})


