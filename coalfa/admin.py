from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms
from .models import Usuario


class UsuarioCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ("rut", "nombre", "apellido", "rol")

    def clean_rut(self):
        rut = self.cleaned_data["rut"].upper().replace(".", "").replace(" ", "")
        return rut

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UsuarioCambioForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label="Contraseña")

    class Meta:
        model = Usuario
        fields = ("rut", "nombre", "apellido", "rol", "password", "is_active", "is_staff")


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    add_form = UsuarioCreationForm
    form = UsuarioCambioForm
    model = Usuario
    list_display = ("rut", "nombre", "apellido", "rol", "is_active")
    list_filter = ("rol", "is_active", "is_staff")
    search_fields = ("rut", "nombre", "apellido")
    ordering = ("apellido", "nombre")

    fieldsets = (
        (None, {"fields": ("rut", "password")}),
        ("Información Personal", {"fields": ("nombre", "apellido")}),
        ("Permisos", {"fields": ("rol", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Fechas", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("rut", "nombre", "apellido", "rol", "password1", "password2"),
        }),
    )
