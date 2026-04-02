from django.db import models
from django.core.validators import FileExtensionValidator
from coalfa.utils import rut_validator
import datetime


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
    rut = models.CharField(max_length=12, unique=True, validators=[rut_validator])
    cargo = models.CharField(max_length=100)
    area = models.CharField(max_length=20, choices=AREA_CHOICES, default="OTRO")
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default="ACTIVO", db_index=True)
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

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old_self = Empleado.objects.get(pk=self.pk)
                if old_self.estado != self.estado:
                    import datetime
                    tipo_ausencia = None
                    if self.estado == "VACACIONES":
                        tipo_ausencia = "VACACIONES"
                    elif self.estado == "LICENCIA":
                        tipo_ausencia = "LICENCIA_MEDICA"
                    
                    if tipo_ausencia:
                        # Auto-registro de ausencia o re-apertura si se cerró hoy mismo
                        hoy = datetime.date.today()
                        ausencias_hoy = PeriodoAusencia.objects.filter(empleado=self, tipo=tipo_ausencia, fecha_inicio=hoy)
                        if not ausencias_hoy.exists():
                            # Se crea con una duración tentativa de 7 días
                            PeriodoAusencia.objects.create(
                                empleado=self,
                                tipo=tipo_ausencia,
                                fecha_inicio=hoy,
                                fecha_fin=hoy + datetime.timedelta(days=7),
                                descripcion=f"Registro automático por cambio de estado a {self.get_estado_display()}"
                            )
                        else:
                            # Si existe pero está cerrada (fecha_fin < hoy), la re-abrimos
                            a = ausencias_hoy.first()
                            if a.fecha_fin < hoy:
                                a.fecha_fin = hoy + datetime.timedelta(days=7)
                                a.descripcion += f" | Re-abierta por cambio de estado a {self.get_estado_display()}"
                                a.save()
                    elif self.estado == "ACTIVO" and old_self.estado in ("VACACIONES", "LICENCIA"):
                        # Si vuelve a estar activo, cerramos el último periodo abierto
                        import datetime
                        hoy = datetime.date.today()
                        ayer = hoy - datetime.timedelta(days=1)
                        ultimo_periodo = self.ausencias.order_by("-fecha_inicio").first()
                        if ultimo_periodo and ultimo_periodo.fecha_fin >= hoy:
                            ultimo_periodo.fecha_fin = ayer
                            ultimo_periodo.save()
            except Empleado.DoesNotExist:
                pass
        super().save(*args, **kwargs)

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
    archivo = models.FileField(
        upload_to="documentos_rrhh/",
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'xls', 'xlsx'])]
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.empleado}"

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ["-fecha_subida"]


class GastoRRHH(models.Model):
    CATEGORIA_CHOICES = [
        ("PASAJES", "Pago de Pasajes"),
        ("EPP", "Artículos EPP"),
        ("CAJA_CHICA", "Gastos de Caja (Caja Chica)"),
        ("EVENTO_COFFEE", "Eventos / Coffee Break"),
        ("OTRO", "Otros Gastos"),
    ]
    fecha = models.DateField(default=datetime.date.today)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    descripcion = models.TextField(blank=True)
    responsable = models.CharField(max_length=100, blank=True)
    comprobante = models.FileField(upload_to="gastos_rrhh/", blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_categoria_display()} — ${self.monto} ({self.fecha})"

    class Meta:
        verbose_name = "Gasto RRHH"
        verbose_name_plural = "Gastos RRHH"
        ordering = ["-fecha"]


class ProductoEPP(models.Model):
    """Artículos de seguridad y ropa que maneja RRHH."""
    nombre = models.CharField(max_length=150)
    talla = models.CharField(max_length=50, blank=True)
    stock = models.FloatField(default=0)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=0, default=0) # Sin decimales por reqs previos
    
    def __str__(self):
        if self.talla:
            return f"{self.nombre} (Talla: {self.talla}) - Stock: {self.stock}"
        return f"{self.nombre} (Stock: {self.stock})"

    class Meta:
        verbose_name = "Producto EPP/Ropa"
        verbose_name_plural = "Inventario EPP/Ropa"
        unique_together = ["nombre", "talla"]


class EntregaEPP(models.Model):
    """Registro de entrega de implementos a empleados."""
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name="entregas_epp")
    producto = models.ForeignKey(ProductoEPP, on_delete=models.CASCADE)
    cantidad = models.FloatField()
    fecha = models.DateField(auto_now_add=True)
    costo_total = models.DecimalField(max_digits=12, decimal_places=0, editable=False)

    def save(self, *args, **kwargs):
        if not self.costo_total:
            self.costo_total = float(self.producto.precio_unitario) * self.cantidad
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad} {self.producto.nombre} -> {self.empleado}"

    class Meta:
        verbose_name = "Entrega de EPP"
        verbose_name_plural = "Entregas de EPP"
