from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

# Registramos el modelo de Usuario con sus campos personalizados
class UsuarioAdmin(UserAdmin):
    # Añadimos el campo 'rol' a los formularios de creación y edición
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Rol', {'fields': ('rol',)}),
    )
    # Mostramos el rol en la lista de usuarios del panel
    list_display = ['username', 'email', 'rol', 'is_staff']

admin.site.register(Usuario, UsuarioAdmin)
