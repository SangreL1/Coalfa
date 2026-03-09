from django.db import models


class Empleado(models.Model):
    ESTADO_CHOICES = [
        ("ACTIVO", "Activo"),
        ("VACACIONES", "En Vacaciones"),
        ("LICENCIA", "Con Licencia"),
        ("FINIQUITADO", "Finiquitado"),
    ]
    AREA_CHOICES = [
        ("BODEGA", "Bodega"),
        ("COCINA", "Cocina"),
        ("REPOSTERIA", "Repostería"),
        ("LINEA", "Línea"),
        ("ADMINISTRACION", "Administración"),
        ("RRHH", "Recursos Humanos"),
        ("OTRO", "Otro"),
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, unique=True)
    cargo = models.CharField(max_length=100)
    area = models.CharField(max_length=20, choices=AREA_CHOICES, default="OTRO")
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default="ACTIVO")
    fecha_ingreso = models.DateField(null=True, blank=True)
    
    # New fields from spreadsheet
    fecha_nacimiento = models.DateField(null=True, blank=True)
    nacionalidad = models.CharField(max_length=50, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    estado_civil = models.CharField(max_length=20, blank=True)
    fecha_contrato = models.DateField(null=True, blank=True)
    anexo_1 = models.DateField(null=True, blank=True)
    anexo_2 = models.DateField(null=True, blank=True)
    turno = models.CharField(max_length=50, blank=True)
    horario = models.CharField(max_length=100, blank=True)
    emergencia_nombre = models.CharField(max_length=100, blank=True)
    emergencia_telefono = models.CharField(max_length=20, blank=True)
    observaciones = models.TextField(blank=True)
    
    foto = models.ImageField(upload_to="empleados/fotos/", blank=True, null=True)

    def __str__(self):
        return f"{self.apellido}, {self.nombre} ({self.rut})"

    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ["apellido", "nombre"]


class PeriodoAusencia(models.Model):
    TIPO_CHOICES = [
        ("VACACIONES", "Vacaciones"),
        ("LICENCIA_MEDICA", "Licencia Médica"),
        ("LICENCIA_MATERNIDAD", "Licencia Maternal"),
    ]
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name="ausencias")
    tipo = models.CharField(max_length=25, choices=TIPO_CHOICES)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return f"{self.empleado} — {self.get_tipo_display()} ({self.fecha_inicio}→{self.fecha_fin})"

    class Meta:
        verbose_name = "Período de Ausencia"
        verbose_name_plural = "Períodos de Ausencia"
        ordering = ["-fecha_inicio"]


class Documento(models.Model):
    TIPO_CHOICES = [
        ("CV", "Currículum Vitae"),
        ("ANEXO", "Anexo de Contrato"),
        ("FINIQUITO", "Finiquito"),
        ("LIQUIDACION", "Liquidación de Sueldo"),
        ("CONTRATO", "Contrato"),
        ("OTRO", "Otro"),
    ]
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name="documentos")
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    descripcion = models.CharField(max_length=200, blank=True)
    archivo = models.FileField(upload_to="documentos_rrhh/")
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.empleado}"

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ["-fecha_subida"]
