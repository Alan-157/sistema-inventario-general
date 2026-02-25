from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import Usuario
from .forms import UsuarioForm
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .forms import RegistroUsuarioForm, PerfilUsuarioForm


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

@login_required
@user_passes_test(es_admin_o_super)
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado con éxito.")
            return redirect('gestion_usuarios')
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/form_usuario.html', {'form': form, 'titulo': 'Crear Nuevo Usuario'})

@login_required
@user_passes_test(es_admin_o_super)
def editar_usuario(request, pk):
    usuario_editado = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES, instance=usuario_editado)
        if form.is_valid():
            form.save()
            messages.success(request, f"Usuario {usuario_editado.username} actualizado.")
            return redirect('gestion_usuarios')
    else:
        form = UsuarioForm(instance=usuario_editado)
    
    return render(request, 'usuarios/form_usuario.html', {
        'form': form, 
        'usuario_editado': usuario_editado, 
        'titulo': 'Editar Usuario'
    })

@login_required
def mi_perfil(request):
    form_perfil = PerfilUsuarioForm(instance=request.user)
    form_password = PasswordChangeForm(user=request.user)

    if request.method == 'POST':
        # Acción para actualizar datos personales
        if 'btn_perfil' in request.POST:
            form_perfil = PerfilUsuarioForm(request.POST, request.FILES, instance=request.user)
            if form_perfil.is_valid():
                form_perfil.save()
                messages.success(request, "¡Tu información ha sido actualizada!")
                return redirect('mi_perfil')
        
        # Acción para cambiar contraseña
        elif 'btn_password' in request.POST:
            form_password = PasswordChangeForm(user=request.user, data=request.POST)
            if form_password.is_valid():
                user = form_password.save()
                # Mantiene la sesión activa después de cambiar la clave
                update_session_auth_hash(request, user)
                messages.success(request, "¡Contraseña actualizada correctamente!")
                return redirect('mi_perfil')

    return render(request, 'usuarios/mi_perfil.html', {
        'form_perfil': form_perfil,
        'form_password': form_password
    })
    
@login_required
@user_passes_test(es_admin_o_super)
def toggle_usuario_status(request, user_id):
    usuario_a_cambiar = get_object_or_404(Usuario, id=user_id)
    
    # Seguridad: Admin no puede desactivar a un Superusuario
    if (usuario_a_cambiar.rol == 'SUPERUSUARIO' or usuario_a_cambiar.is_superuser) and request.user.rol == 'ADMIN':
        messages.error(request, "No tienes permiso para desactivar a un Superusuario.")
        return redirect('gestion_usuarios')
    
    # Seguridad: No puedes desactivarte a ti mismo
    if usuario_a_cambiar == request.user:
        messages.error(request, "No puedes desactivar tu propia cuenta.")
        return redirect('gestion_usuarios')

    # Cambiamos el estado
    usuario_a_cambiar.is_active = not usuario_a_cambiar.is_active
    usuario_a_cambiar.save()
    
    estado = "activado" if usuario_a_cambiar.is_active else "desactivado"
    messages.success(request, f"El usuario {usuario_a_cambiar.username} ha sido {estado}.")
    
    return redirect('gestion_usuarios')