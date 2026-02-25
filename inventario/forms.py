from django import forms
from django.core.exceptions import ValidationError
from .models import Producto, HistorialMovimiento, Categoria, Proveedor

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre', 'categoria', 'proveedor', 'precio_costo', 
            'precio_venta', 'stock_actual', 'stock_minimo', 'imagen'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Taladro Percutor Bosch 800W'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'precio_costo': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_imagen(self):
        imagen = self.cleaned_data.get('imagen')
        if imagen:
            extension = imagen.name.split('.')[-1].lower()
            if extension not in ['jpg', 'jpeg']:
                raise ValidationError("La imagen debe ser exclusivamente formato JPG.")
            if imagen.size > 2 * 1024 * 1024:
                raise ValidationError("El tamaño máximo permitido es 2MB.")
        return imagen

class MovimientoForm(forms.ModelForm):
    class Meta:
        model = HistorialMovimiento
        # 1. Cambiamos 'descripcion' por 'motivo' aquí
        fields = ['producto', 'tipo', 'cantidad', 'motivo'] 
        
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 15'}),
            # 2. Y aquí también en el widget
            'motivo': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Escribe el motivo del movimiento...'
            }),
        }
        
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Herramientas Eléctricas'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Breve descripción...'}),
        }
        
class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'contacto', 'telefono', 'email', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la empresa'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del representante'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 ...'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contacto@empresa.cl'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección comercial'}),
        }