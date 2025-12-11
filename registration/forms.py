from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from Agenda.models import PerfilUsuario, Rol


class RegistroPacienteForm(UserCreationForm):
    nombre = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Nombre"}
        ),
    )
    apellido = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Apellido"}
        ),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Correo electrónico"}
        ),
    )
    direccion = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Dirección"}
        ),
    )
    telefono = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Teléfono"}
        ),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre de usuario"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Contraseña"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Confirmar contraseña"}
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["nombre"]
        user.last_name = self.cleaned_data["apellido"]
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()
            # Crear el perfil de paciente
            rol_paciente, created = Rol.objects.get_or_create(nombre="Paciente")
            PerfilUsuario.objects.create(
                user=user,
                direccion=self.cleaned_data.get("direccion", ""),
                telefono=self.cleaned_data.get("telefono", ""),
                rol=rol_paciente,
            )
        return user
