from django.db import models
from django.conf import settings # Importamos settings para referenciar nuestro modelo de usuario personalizado
from django.utils.text import slugify
import random
import string

# 1. MODELO DE CATEGORÍA
# Permite agrupar productos para organizar el inventario y facilitar búsquedas masivas.
class Categoria(models.Model):
    # unique=True evita duplicados y crea un índice en la DB para búsquedas rápidas.
    nombre = models.CharField(max_length=100, unique=True) 
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

# 2. MODELO DE PROVEEDOR
# Es vital para la gestión de compras y contacto cuando el stock esté bajo.
class Proveedor(models.Model):
    nombre = models.CharField(max_length=150)
    # En Chile el RUT es el identificador único, lo usamos como clave de búsqueda.
    rut = models.CharField(max_length=12, unique=True, help_text="Ej: 12.345.678-9")
    contacto = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField()

    def __str__(self):
        return self.nombre

# 3. MODELO DE PRODUCTO
# El núcleo del sistema. Diseñado para ser eficiente incluso con 100k+ registros.
class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    # El SKU es el índice principal. MySQL lo indexa automáticamente al ser unique,
    # permitiendo encontrar productos instantáneamente entre miles de filas.
    sku = models.CharField(max_length=50, unique=True, blank=True) 
    
    # on_delete=models.PROTECT evita que borren una categoría si tiene productos (Seguridad de datos).
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True)
    
    # AJUSTE PARA CHILE: Usamos IntegerField ya que en CLP no manejamos decimales.
    # Esto hace las operaciones matemáticas más rápidas y exactas.
    precio_costo = models.IntegerField(help_text="Precio de compra unitario (pesos)")
    precio_venta = models.IntegerField(help_text="Precio de venta final (pesos)")
    
    # Stock con PositiveIntegerField para prevenir errores de lógica (stock negativo).
    stock_actual = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=10) # Umbral para las alertas de reposición
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    
    def save(self, *args, **kwargs):
        # Solo generamos el SKU si el producto es nuevo (no tiene SKU aún)
        if not self.sku:
            # 1. Tomamos las primeras 3 letras de la categoría (en mayúsculas)
            prefijo_cat = self.categoria.nombre[:3].upper()
            
            # 2. Tomamos las primeras 3 letras del nombre del producto
            prefijo_prod = self.nombre[:3].upper()
            
            # 3. Generamos un sufijo aleatorio de 4 dígitos para asegurar que sea único
            aleatorio = ''.join(random.choices(string.digits, k=4))
            
            # 4. Construimos el SKU final: EJ: ELE-TEL-5521
            self.sku = f"{prefijo_cat}-{prefijo_prod}-{aleatorio}"
            
        # Llamamos al método save original para que guarde en la DB
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.sku})"

# 4. MODELO DE HISTORIAL (KARDEX)
# Registra cada movimiento de stock para auditoría (quién hizo qué, cuándo y por qué).
class HistorialMovimiento(models.Model):
    # Opciones fijas para estandarizar los tipos de movimiento en la base de datos.
    TIPO_MOVIMIENTO = [
        ('ENTRADA', 'Entrada de Mercadería'),
        ('SALIDA', 'Salida / Venta'),
        ('AJUSTE', 'Ajuste de Inventario (Mermas/Errores)'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    # Registramos qué usuario (de nuestra app 'usuarios') realizó la acción.
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    tipo = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO)
    cantidad = models.IntegerField() # Cantidad que se movió
    motivo = models.TextField(blank=True, help_text="Explicación del movimiento")
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo}: {self.producto.nombre} por {self.usuario}"