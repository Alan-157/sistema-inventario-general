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
        fields = ['nombre', 'categoria', 'proveedor', 'precio_costo', 'precio_venta', 'stock_actual', 'stock_minimo', 'imagen']

    # Validación personalizada (U1 Clase 9)
    def clean_precio_venta(self):
        precio_venta = self.cleaned_data.get('precio_venta')
        if precio_venta <= 0:
            raise ValidationError("El precio de venta debe ser un número positivo.")
        return precio_venta

    def clean(self):
        cleaned_data = super().clean()
        costo = cleaned_data.get('precio_costo')
        venta = cleaned_data.get('precio_venta')

        if costo and venta and venta < costo:
            raise ValidationError({
                'precio_venta': "El precio de venta no puede ser menor al costo (estarías perdiendo dinero)."
            })
        return cleaned_data
        