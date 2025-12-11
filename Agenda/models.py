from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validar_rut_chileno(rut):
    """
    Valida un RUT chileno y verifica su dígito verificador
    Acepta diferentes formatos: 12345678-9, 12.345.678-9, 123456789
    """
    if not rut:
        raise ValidationError(_("RUT inválido"))

    # Eliminar puntos, guiones, espacios y convertir a mayúsculas
    rut = rut.replace(".", "").replace("-", "").replace(" ", "").upper()

    # Verificar que tenga entre 8 y 9 caracteres (7-8 dígitos + 1 dígito verificador)
    if len(rut) < 8 or len(rut) > 9:
        raise ValidationError(_("RUT inválido"))

    # Extraer dígito verificador (último carácter)
    dv = rut[-1]

    # Extraer cuerpo del RUT (primeros dígitos)
    cuerpo = rut[:-1]

    # Verificar que el cuerpo contenga solo dígitos
    if not cuerpo.isdigit():
        raise ValidationError(_("RUT inválido"))

    # Verificar que el dígito verificador sea válido (número o K)
    if dv not in "0123456789K":
        raise ValidationError(_("RUT inválido"))

    # Calcular dígito verificador usando el algoritmo del Módulo 11
    reversed_cuerpo = cuerpo[::-1]  # Invertir el cuerpo
    secuencia = [2, 3, 4, 5, 6, 7]  # Secuencia de multiplicadores
    suma = 0

    for i, digito in enumerate(reversed_cuerpo):
        multiplicador = secuencia[i % len(secuencia)]  # Ciclar entre 2 y 7
        suma += int(digito) * multiplicador

    resto = suma % 11
    dv_calculado = 11 - resto

    if dv_calculado == 10:
        dv_calculado = "K"
    elif dv_calculado == 11:
        dv_calculado = "0"
    else:
        dv_calculado = str(dv_calculado)

    if dv != dv_calculado:
        raise ValidationError(_("RUT inválido"))

    # Devolver el RUT en formato estándar (ej: 12345678-9)
    return f"{cuerpo}-{dv}"


class Rol(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"


class Especialidad(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if self.nombre:
            # Normalizar tildes y formato
            nombre = self.nombre.lower()
            # Correcciones específicas de tildes
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

            # Aplicar corrección si existe
            if nombre in correcciones:
                self.nombre = correcciones[nombre]
            else:
                # Formato general: primera letra mayúscula, resto minúsculas
                self.nombre = (
                    nombre.title().replace(" Y ", " y ").replace(" De ", " de ")
                )
        super().save(*args, **kwargs)


class Medicamentos(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Medicamentos"


class Examenes(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Examenes"


class Medico(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="medico", default=1
    )
    rut = models.CharField(max_length=12, unique=True, validators=[validar_rut_chileno])
    especialidades = models.ManyToManyField(Especialidad)
    roles = models.ManyToManyField(Rol, blank=True)
    foto = models.ImageField(upload_to="medicos/")

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.rut}"


class Paciente(models.Model):
    SEXO_CHOICES = [
        ("M", "Masculino"),
        ("F", "Femenino"),
        ("O", "Otro"),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="paciente", default=1
    )
    rut = models.CharField(max_length=12, unique=True, validators=[validar_rut_chileno])
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    telefono = models.CharField(max_length=20)
    direccion = models.TextField()
    email = models.EmailField()

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.rut}"


class FichaMedica(models.Model):
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE)
    alergias = models.TextField(blank=True)
    enfermedades_cronicas = models.TextField(blank=True)
    medicamentos = models.TextField(blank=True)
    antecedentes_familiares = models.TextField(blank=True)

    def __str__(self):
        return f"Ficha médica de {self.paciente}"


class VisitaAtencion(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    anamnesis = models.TextField()
    diagnostico = models.TextField()
    medicamentos = models.ManyToManyField(
        Medicamentos, blank=True, related_name="visitas"
    )
    examenes = models.ManyToManyField(Examenes, blank=True, related_name="visitas")
    especialidad = models.ForeignKey(
        Especialidad, on_delete=models.SET_NULL, null=True, blank=True
    )
    fecha_atencion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"Atención de {self.paciente} con {self.medico} del {self.fecha_atencion}"
        )
