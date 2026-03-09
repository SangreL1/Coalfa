from django import forms


class LoginForm(forms.Form):
    rut = forms.CharField(
        label="RUT",
        max_length=12,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Ej: 12345678-9",
                "class": "form-input",
                "id": "id_rut",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "••••••••",
                "class": "form-input",
                "id": "id_password",
                "autocomplete": "current-password",
            }
        ),
    )
