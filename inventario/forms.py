from django import forms
from .models import Lote

class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = [
            "producto", "proveedor", "numero_lote_proveedor", "numero_guia",
            "cantidad", "fecha_recepcion", "fecha_vencimiento", "temperatura_recepcion",
            "ubicacion_actual", "proceso", "responsable_registro", "observaciones"
        ]
        widgets = {
            "producto": forms.Select(attrs={"class": "form-control"}),
            "proveedor": forms.Select(attrs={"class": "form-control"}),
            "numero_lote_proveedor": forms.TextInput(attrs={"class": "form-control"}),
            "numero_guia": forms.TextInput(attrs={"class": "form-control"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "fecha_recepcion": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "fecha_vencimiento": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "temperatura_recepcion": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "ubicacion_actual": forms.Select(attrs={"class": "form-control"}),
            "proceso": forms.Select(attrs={"class": "form-control"}),
            "responsable_registro": forms.TextInput(attrs={"class": "form-control"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
