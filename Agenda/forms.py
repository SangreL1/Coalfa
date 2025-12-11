from django import forms
from .models import (
    Paciente,
    VisitaAtencion,
    Medico,
    Especialidad,
    FichaMedica,
    Medicamentos,
    Examenes,
)
from django.contrib.auth.models import User
from django.db.models import Q


class PacienteForm(forms.ModelForm):
    first_name = forms.CharField(
        label="Nombres", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        label="Apellidos", widget=forms.TextInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = Paciente
        fields = [
            "rut",
            "first_name",
            "last_name",
            "fecha_nacimiento",
            "sexo",
            "telefono",
            "direccion",
            "email",
        ]
        widgets = {
            "fecha_nacimiento": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "rut": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "12345678-9"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean_rut(self):
        rut = self.cleaned_data.get("rut")
        if rut:
            # Eliminar puntos y guiones para la validación
            rut = rut.replace(".", "").replace("-", "").upper()
            # Agregar lógica para formatear el RUT con guion antes del dígito verificador
            if len(rut) > 1:  # Asegurar que tiene al menos un dígito y un verificador
                cuerpo = rut[:-1]
                dv = rut[-1]
                formatted_rut = f"{cuerpo}-{dv}"
                return formatted_rut
        return rut

    def clean_first_name(self):
        return self.cleaned_data["first_name"].title()

    def clean_last_name(self):
        return self.cleaned_data["last_name"].title()

    def clean_email(self):
        return self.cleaned_data["email"].lower()

    def clean_fecha_nacimiento(self):
        from django.utils import timezone

        fecha = self.cleaned_data.get("fecha_nacimiento")
        if fecha and fecha > timezone.now().date():
            raise forms.ValidationError("La fecha de nacimiento no puede ser futura")
        return fecha


class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name"]
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "RUT (12345678-9)"}
            ),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }
        labels = {
            "username": "RUT",
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username:
            # Eliminar puntos y guiones para la validación
            username = username.replace(".", "").replace("-", "").upper()
            # Agregar lógica para formatear el RUT con guion antes del dígito verificador
            if (
                len(username) > 1
            ):  # Asegurar que tiene al menos un dígito y un verificador
                cuerpo = username[:-1]
                dv = username[-1]
                formatted_username = f"{cuerpo}-{dv}"
                return formatted_username
        return username

    def clean_first_name(self):
        return self.cleaned_data["first_name"].title()

    def clean_last_name(self):
        return self.cleaned_data["last_name"].title()

    def clean_email(self):
        return self.cleaned_data["email"].lower()


class VisitaAtencionForm(forms.ModelForm):
    especialidad = forms.ModelChoiceField(
        queryset=Especialidad.objects.none(),
        label="Especialidad",
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    medicamentos = forms.ModelMultipleChoiceField(
        queryset=Medicamentos.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Medicamentos",
    )
    examenes = forms.ModelMultipleChoiceField(
        queryset=Examenes.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Exámenes Solicitados",
    )

    class Meta:
        model = VisitaAtencion
        fields = [
            "especialidad",
            "anamnesis",
            "diagnostico",
            "medicamentos",
            "examenes",
        ]
        widgets = {
            "anamnesis": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "diagnostico": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "medicamentos": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        medico = kwargs.pop("medico", None)
        super().__init__(*args, **kwargs)
        if medico:
            self.fields["especialidad"].queryset = medico.especialidades.all()
            if medico.especialidades.count() == 1:
                self.fields["especialidad"].initial = medico.especialidades.first()


class MedicoForm(forms.ModelForm):
    especialidades = forms.ModelMultipleChoiceField(
        queryset=Especialidad.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    class Meta:
        model = Medico
        fields = [
            "user",
            "especialidades",
            "foto",
        ]
        widgets = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrar usuarios que no sean médicos, o el usuario actual si es edición
        if self.instance.pk:
            self.fields["user"].queryset = User.objects.filter(
                Q(medico__isnull=True) | Q(pk=self.instance.user.pk)
            )
        else:
            self.fields["user"].queryset = User.objects.filter(medico__isnull=True)

        # clases para Bootstrap classes
        for name, field in self.fields.items():
            if name not in ["especialidades"]:
                field.widget.attrs["class"] = "form-control"
                if isinstance(field.widget, forms.Select):
                    field.widget.attrs["class"] = "form-select"

    def clean_user(self):
        user = self.cleaned_data.get("user")
        if user:
            # Si se está creando un nuevo médico o se cambia el usuario
            if not self.instance.pk or self.instance.user != user:
                # Verificar si el usuario ya tiene un médico asociado
                if hasattr(user, "medico"):
                    raise forms.ValidationError(
                        "El usuario seleccionado ya está asociado a un médico."
                    )
        return user


class FichaMedicaForm(forms.ModelForm):
    class Meta:
        model = FichaMedica
        fields = [
            "alergias",
            "enfermedades_cronicas",
            "medicamentos",
            "antecedentes_familiares",
        ]
        widgets = {
            "alergias": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "enfermedades_cronicas": forms.Textarea(
                attrs={"rows": 2, "class": "form-control"}
            ),
            "medicamentos": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "antecedentes_familiares": forms.Textarea(
                attrs={"rows": 2, "class": "form-control"}
            ),
        }


class MedicamentosForm(forms.ModelForm):
    class Meta:
        model = Medicamentos
        fields = ["nombre", "descripcion"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }


class EspecialidadForm(forms.ModelForm):
    class Meta:
        model = Especialidad
        fields = ["nombre"]
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre de la especialidad",
                }
            ),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre", "")
        if nombre:
            # Correcciones de tildes comunes
            correcciones = {
                "ginecologia": "Ginecología",
                "obstetricia": "Obstetricia",
                "odontologia": "Odontología",
                "medicina general": "Medicina General",
                "pediatria": "Pediatría",
                "cardiologia": "Cardiología",
                "dermatologia": "Dermatología",
                "oftalmologia": "Oftalmología",
                "neurologia": "Neurología",
                "traumatologia": "Traumatología",
            }

            nombre_lower = nombre.lower()
            if nombre_lower in correcciones:
                formatted = correcciones[nombre_lower]
            else:
                formatted = nombre.title().replace(" Y ", " y ").replace(" De ", " de ")

            if nombre != formatted:
                raise forms.ValidationError(f'Formato requerido: "{formatted}"')
            return formatted
        return nombre


class ExamenesForm(forms.ModelForm):
    class Meta:
        model = Examenes
        fields = ["nombre", "descripcion"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }
