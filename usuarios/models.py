from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    ROLES = [
        ('SUPERUSUARIO', 'Superusuario'),
        ('ADMIN', 'Administrador'),
        ('TRABAJADOR', 'Trabajador'),
        ('CLIENTE', 'Cliente'),
    ]
    
    rol = models.CharField(max_length=20, choices=ROLES, default='CLIENTE')

    def save(self, *args, **kwargs):
        # Si el usuario es marcado como superusuario de Django, 
        # le asignamos automáticamente el rol de SUPERUSUARIO del sistema.
        if self.is_superuser and self.rol != 'SUPERUSUARIO':
            self.rol = 'SUPERUSUARIO'
        super().save(*args, **kwargs)