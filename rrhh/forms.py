from django import forms
from .models import Empleado, Documento, PeriodoAusencia

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = [
            "nombre", "apellido", "rut", "cargo", "area", 
            "email", "telefono", "estado", "fecha_ingreso",
            "fecha_nacimiento", "nacionalidad", "direccion", "estado_civil",
            "fecha_contrato", "anexo_1", "anexo_2", "turno", "horario",
            "emergencia_nombre", "emergencia_telefono", "observaciones", "foto"
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "apellido": forms.TextInput(attrs={"class": "form-control"}),
            "rut": forms.TextInput(attrs={"class": "form-control"}),
            "cargo": forms.TextInput(attrs={"class": "form-control"}),
            "area": forms.Select(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "estado": forms.Select(attrs={"class": "form-control"}),
            "fecha_ingreso": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "fecha_nacimiento": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "nacionalidad": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "estado_civil": forms.TextInput(attrs={"class": "form-control"}),
            "fecha_contrato": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "anexo_1": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "anexo_2": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "turno": forms.TextInput(attrs={"class": "form-control"}),
            "horario": forms.TextInput(attrs={"class": "form-control"}),
            "emergencia_nombre": forms.TextInput(attrs={"class": "form-control"}),
            "emergencia_telefono": forms.TextInput(attrs={"class": "form-control"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "foto": forms.FileInput(attrs={"class": "form-control"}),
        }

class DocumentoEditForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ["tipo", "descripcion"]
        widgets = {
            "tipo": forms.Select(attrs={"class": "form-control"}),
            "descripcion": forms.TextInput(attrs={"class": "form-control"}),
        }

class AusenciaForm(forms.ModelForm):
    class Meta:
        model = PeriodoAusencia
        fields = ["empleado", "tipo", "fecha_inicio", "fecha_fin", "descripcion"]
        widgets = {
            "empleado": forms.Select(attrs={"class": "form-control"}),
            "tipo": forms.Select(attrs={"class": "form-control"}),
            "fecha_inicio": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "fecha_fin": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Observaciones opcionales..."}),
        }
