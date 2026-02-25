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
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
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
        fields = ['producto', 'tipo', 'cantidad', 'motivo']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        