from django.db import models
from django.conf import settings 
import random
import string

# CLASE BASE PARA REUTILIZAR CAMPOS DE AUDITORÍA
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True) # Soft Delete lógico

    class Meta:
        abstract = True

# 1. MODELO DE CATEGORÍA
class Categoria(BaseModel):
    nombre = models.CharField(max_length=100, unique=True) 
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

# 2. MODELO DE PROVEEDOR
class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    # CORRECCIÓN: Eliminamos bold=True ya que no es un argumento válido de Django
    contacto = models.CharField(max_length=100, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    direccion = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return self.nombre
    
# 3. MODELO DE PRODUCTO
class Producto(BaseModel):
    nombre = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True)
    
    # Precios en pesos chilenos (sin decimales)
    precio_costo = models.IntegerField(help_text="Precio de compra unitario (pesos)")
    precio_venta = models.IntegerField(help_text="Precio de venta final (pesos)")
    
    stock_actual = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=10)
    
    # Campo de Imagen (Clase 10)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

    def save(self, *args, **kwargs):
        # Lógica de generación de SKU automático: CAT-PROD-RANDOM
        if not self.sku:
            prefijo_cat = self.categoria.nombre[:3].upper()
            prefijo_prod = self.nombre[:3].upper()
            aleatorio = ''.join(random.choices(string.digits, k=4))
            self.sku = f"{prefijo_cat}-{prefijo_prod}-{aleatorio}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.sku})"

# 4. MODELO DE HISTORIAL (KARDEX)
class HistorialMovimiento(BaseModel):
    TIPO_MOVIMIENTO = [
        ('ENTRADA', 'Entrada de Mercadería'),
        ('SALIDA', 'Salida / Venta'),
        ('AJUSTE', 'Ajuste de Inventario (Mermas/Errores)'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    tipo = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO)
    cantidad = models.IntegerField() 
    motivo = models.TextField(blank=True, help_text="Explicación del movimiento")

    def __str__(self):
        return f"{self.tipo}: {self.producto.nombre} por {self.usuario}"