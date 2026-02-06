from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    #Definimos los roles como constantes para evitar errores de escritura
    ADMIN = 'ADMIN'
    BODEGUERO = 'BODEGUERO'
    VISUALIZADOR = 'VISUALIZADOR'
    
    ROLES_CHOICES = [
        (ADMIN, 'Administrador'),
        (BODEGUERO, 'Bodeguero / Operador'),
        (VISUALIZADOR, 'Solo Visualización'),
    ]

    #Añadimos el campo rol al usuario
    rol = models.CharField(
        max_length=20,
        choices= ROLES_CHOICES,
        default=VISUALIZADOR,
        help_text="Usuario que solo puede ver la pagina sin acción alguna(por mientras)"
    )
    
    def __str__(self):
        return f"{self.username} - {self.get_rol_display()}"