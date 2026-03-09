import re
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


def validar_rut(rut: str) -> bool:
    """Validates Chilean RUT format (12345678-9 or 12345678-K)."""
    rut = rut.upper().replace(".", "").replace(" ", "")
    if not re.match(r"^\d{7,8}-[\dK]$", rut):
        return False
    numero, dv = rut.split("-")
    suma, mul = 0, 2
    for d in reversed(numero):
        suma += int(d) * mul
        mul = mul + 1 if mul < 7 else 2
    resto = 11 - (suma % 11)
    verificador = "K" if resto == 10 else ("0" if resto == 11 else str(resto))
    return verificador == dv


class UsuarioManager(BaseUserManager):
    def create_user(self, rut, password=None, **extra_fields):
        rut = rut.upper().replace(".", "").replace(" ", "")
        user = self.model(rut=rut, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, rut, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("rol", "ADMIN")
        return self.create_user(rut, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    ROL_CHOICES = [
        ("ADMIN", "Administrador"),
        ("RRHH", "Recursos Humanos"),
        ("OPERACIONAL", "Operacional"),
    ]

    rut = models.CharField(max_length=12, unique=True, verbose_name="RUT")
    nombre = models.CharField(max_length=60, verbose_name="Nombre")
    apellido = models.CharField(max_length=60, verbose_name="Apellido")
    rol = models.CharField(max_length=15, choices=ROL_CHOICES, default="RRHH", verbose_name="Rol")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    is_staff = models.BooleanField(default=False, verbose_name="Es staff")
    solicitud_pendiente = models.BooleanField(default=False, verbose_name="Solicitud pendiente de aprobación")
    date_joined = models.DateTimeField(default=timezone.now, verbose_name="Fecha de registro")

    USERNAME_FIELD = "rut"
    REQUIRED_FIELDS = ["nombre", "apellido"]

    objects = UsuarioManager()

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.rut})"

    def get_full_name(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
