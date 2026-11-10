from django import forms
from .models import (
    Vehiculo,
    DocumentoVehiculo,
    PautaMantencion,
    RegistroMantencion,
    RegistroKilometraje,
    ChecklistPreUso,
    CostoVehiculo,
    ConfiguracionFlota,
)


class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = [
            "patente",
            "marca",
            "modelo",
            "anio",
            "tipo",
            "asignacion",
            "estado",
            "kilometraje_actual",
            "conductor_habitual",
            "observaciones",
            "activo",
        ]
        widgets = {
            "patente": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: ABCD12", "style": "text-transform: uppercase;"}),
            "marca": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Toyota, Chevrolet, Hyundai"}),
            "modelo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Hilux 4x4, D-Max, H1"}),
            "anio": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Ej: 2022"}),
            "tipo": forms.Select(attrs={"class": "form-control"}),
            "asignacion": forms.Select(attrs={"class": "form-control"}),
            "estado": forms.Select(attrs={"class": "form-control"}),
            "kilometraje_actual": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Ej: 45000"}),
            "conductor_habitual": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre del conductor asignado"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Detalles adicionales, equipamiento especial, etc."}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class DocumentoVehiculoForm(forms.ModelForm):
    class Meta:
        model = DocumentoVehiculo
        fields = [
            "vehiculo",
            "tipo_documento",
            "nombre_personalizado",
            "numero_documento_o_poliza",
            "entidad_emisora",
            "fecha_emision",
            "fecha_vencimiento",
            "archivo",
            "observaciones",
        ]
        widgets = {
            "vehiculo": forms.Select(attrs={"class": "form-control"}),
            "tipo_documento": forms.Select(attrs={"class": "form-control"}),
            "nombre_personalizado": forms.TextInput(attrs={"class": "form-control", "placeholder": "Detalle opcional o si es Otro documento"}),
            "numero_documento_o_poliza": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nº certificado o póliza"}),
            "entidad_emisora": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: PRT San Dámaso, BCI Seguros, etc."}),
            "fecha_emision": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "fecha_vencimiento": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "archivo": forms.FileInput(attrs={"class": "form-control", "accept": ".pdf,.jpg,.jpeg,.png"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }


class PautaMantencionForm(forms.ModelForm):
    class Meta:
        model = PautaMantencion
        fields = ["nombre", "intervalo_km", "intervalo_meses", "descripcion", "activo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Cambio de Aceite y Filtro"}),
            "intervalo_km": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Ej: 10000"}),
            "intervalo_meses": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Ej: 6"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class RegistroMantencionForm(forms.ModelForm):
    class Meta:
        model = RegistroMantencion
        fields = [
            "vehiculo",
            "pauta",
            "tipo_servicio",
            "titulo",
            "fecha",
            "kilometraje",
            "taller",
            "costo",
            "proximo_km",
            "proxima_fecha",
            "comprobante",
            "responsable",
            "observaciones",
        ]
        widgets = {
            "vehiculo": forms.Select(attrs={"class": "form-control"}),
            "pauta": forms.Select(attrs={"class": "form-control"}),
            "tipo_servicio": forms.Select(attrs={"class": "form-control"}),
            "titulo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Mantención 50.000 km, aceite 10W40 y filtros"}),
            "fecha": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "kilometraje": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Ej: 50200"}),
            "taller": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Taller Central, Concesionario, etc."}),
            "costo": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Monto en CLP (sin puntos)"}),
            "proximo_km": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Ej: 60000 (Opcional, se calcula si hay pauta)"}),
            "proxima_fecha": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "comprobante": forms.FileInput(attrs={"class": "form-control", "accept": ".pdf,.jpg,.jpeg,.png"}),
            "responsable": forms.TextInput(attrs={"class": "form-control", "placeholder": "Registrado por"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class RegistroKilometrajeForm(forms.ModelForm):
    class Meta:
        model = RegistroKilometraje
        fields = [
            "vehiculo",
            "kilometraje",
            "fecha",
            "conductor_o_responsable",
            "origen_destino",
            "observaciones",
        ]
        widgets = {
            "vehiculo": forms.Select(attrs={"class": "form-control", "required": "required"}),
            "kilometraje": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Km del odómetro", "required": "required", "style": "font-size: 1.25rem; font-weight: 700;"}),
            "fecha": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "conductor_o_responsable": forms.TextInput(attrs={"class": "form-control", "placeholder": "Tu nombre o del conductor"}),
            "origen_destino": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Casino San Lucas -> Faena"}),
            "observaciones": forms.TextInput(attrs={"class": "form-control", "placeholder": "Opcional"}),
        }


class ChecklistPreUsoForm(forms.ModelForm):
    class Meta:
        model = ChecklistPreUso
        fields = [
            "vehiculo",
            "conductor",
            "kilometraje",
            "luces_ok",
            "neumaticos_ok",
            "fluidos_ok",
            "frenos_ok",
            "documentos_ok",
            "seguridad_ok",
            "carroceria_ok",
            "limpieza_ok",
            "aprobado_para_circular",
            "observaciones",
        ]
        widgets = {
            "vehiculo": forms.Select(attrs={"class": "form-control"}),
            "conductor": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre del conductor o inspector"}),
            "kilometraje": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Kilometraje al inicio del turno"}),
            "luces_ok": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "neumaticos_ok": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "fluidos_ok": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "frenos_ok": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "documentos_ok": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "seguridad_ok": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "carroceria_ok": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "limpieza_ok": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "aprobado_para_circular": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Anota cualquier detalle, rayón, ruido extraño o bombilla quemada..."}),
        }


class CostoVehiculoForm(forms.ModelForm):
    class Meta:
        model = CostoVehiculo
        fields = [
            "vehiculo",
            "tipo",
            "fecha",
            "monto",
            "litros",
            "kilometraje",
            "proveedor",
            "numero_documento",
            "comprobante",
            "responsable",
            "observaciones",
        ]
        widgets = {
            "vehiculo": forms.Select(attrs={"class": "form-control"}),
            "tipo": forms.Select(attrs={"class": "form-control"}),
            "fecha": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "monto": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Monto en CLP (ej: 45000)", "style": "font-weight: 700;"}),
            "litros": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Litros (si es combustible)", "step": "0.01"}),
            "kilometraje": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Odómetro al momento de la carga"}),
            "proveedor": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Copec, Shell, Petrobras, Taller X"}),
            "numero_documento": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nº Boleta o Factura"}),
            "comprobante": forms.FileInput(attrs={"class": "form-control", "accept": ".pdf,.jpg,.jpeg,.png"}),
            "responsable": forms.TextInput(attrs={"class": "form-control", "placeholder": "Quién realizó el gasto"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }


class ConfiguracionFlotaForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionFlota
        fields = [
            "correos_notificacion",
            "alertar_30_dias",
            "alertar_15_dias",
            "alertar_7_dias",
            "alertar_vencidos",
            "alertar_km",
            "km_anticipacion_alerta",
            "asunto_alerta",
            "activo",
        ]
        widgets = {
            "correos_notificacion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "administrador@coalfa.cl, jefe.operaciones@coalfa.cl\nsupervisor.faena@coalfa.cl",
                }
            ),
            "alertar_30_dias": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "alertar_15_dias": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "alertar_7_dias": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "alertar_vencidos": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "alertar_km": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "km_anticipacion_alerta": forms.NumberInput(attrs={"class": "form-control", "placeholder": "1000"}),
            "asunto_alerta": forms.TextInput(attrs={"class": "form-control"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
