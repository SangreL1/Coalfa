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

class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

class CargaExcelForm(forms.Form):
    area = forms.ChoiceField(
        label="Área que solicita",
        required=True,
        widget=forms.Select(attrs={"class": "form-control", "style": "margin-bottom: 1rem;"})
    )
    fecha_consumo = forms.DateField(
        label="Fecha de la solicitud",
        required=True,
        widget=forms.DateInput(attrs={
            "class": "form-control",
            "type": "date",
            "style": "margin-bottom: 1rem;"
        })
    )
    archivo_excel = forms.FileField(
        label="Archivos Excel de Solicitudes",
        widget=MultipleFileInput(attrs={
            "class": "form-control",
            "accept": ".xlsx, .xls",
            "multiple": True
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Lote, RegistroServicio
        # Opciones base de ubicaciones
        choices = list(Lote.UBICACION_CHOICES)
        # Áreas que ya tienen registros pero no están en la lista base (ej: COALFA)
        registradas = RegistroServicio.objects.values_list('area', flat=True).distinct()
        keys = [c[0] for c in choices]
        for r in registradas:
            if r and r not in keys:
                choices.append((r, r))
        self.fields['area'].choices = choices
