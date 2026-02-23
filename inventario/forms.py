from django import forms
from django.core.exceptions import ValidationError
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

    def clean(self):
        cleaned_data = super().clean()
        precio_costo = cleaned_data.get("precio_costo")
        precio_venta = cleaned_data.get("precio_venta")

        # Regla de negocio: No se puede vender a menos de lo que costó
        if precio_costo and precio_venta:
            if precio_venta < precio_costo:
                raise ValidationError({
                    'precio_venta': "El precio de venta no puede ser menor al costo de adquisición."
                })
        return cleaned_data
        