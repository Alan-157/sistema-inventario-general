from django import forms
from .models import HistorialMovimiento, Producto

class MovimientoForm(forms.ModelForm):
    class Meta:
        model = HistorialMovimiento
        fields = ['producto', 'tipo', 'cantidad', 'motivo']
        widgets = {
            # Usamos clases de Bootstrap para que el formulario se vea bien
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        # No incluimos 'sku' porque se genera automáticamente en el save() del modelo
        fields = ['nombre', 'categoria', 'proveedor', 'precio_costo', 'precio_venta', 'stock_actual', 'stock_minimo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'precio_costo': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
        }