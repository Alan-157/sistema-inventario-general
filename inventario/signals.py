from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import HistorialMovimiento
from django.conf import settings

@receiver(post_save, sender=HistorialMovimiento)
def alertar_stock_critico(sender, instance, created, **kwargs):
    if created:  # Solo si el movimiento se acaba de crear
        producto = instance.producto
        # Si el stock actual es menor o igual al mínimo
        if producto.stock_actual <= producto.stock_minimo:
            subject = f'⚠️ ALERTA DE STOCK CRÍTICO: {producto.nombre}'
            message = f"""
            Hola Administrador,
            
            Se ha registrado un movimiento que ha dejado un producto en nivel crítico.
            
            Producto: {producto.nombre}
            SKU: {producto.sku}
            Stock Actual: {producto.stock_actual}
            Stock Mínimo Permitido: {producto.stock_minimo}
            
            Último Movimiento: {instance.tipo} de {instance.cantidad} unidades.
            Registrado por: {instance.usuario.username}
            
            Por favor, gestione la reposición de este artículo lo antes posible.
            """
            
            # Aquí pones el correo donde quieres recibir las alertas
            admin_email = 'alan_tu_correo@ejemplo.com' 
            
            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [admin_email])
            except Exception as e:
                print(f"Error al enviar el correo: {e}")