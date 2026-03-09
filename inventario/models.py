from django.db import models
import datetime


def _generar_numero_lote(producto_nombre):
    """Genera un código de lote automático: PREFIJO-YYYY-MM-NNN"""
    prefix = "".join([p[:3].upper() for p in producto_nombre.split()[:2]])
    hoy = datetime.date.today()
    base = f"{prefix}-{hoy.year}-{hoy.month:02d}-"
    ultimo = (
        Lote.objects.filter(numero_lote__startswith=base)
        .order_by("numero_lote")
        .last()
    )
    if ultimo:
        try:
            n = int(ultimo.numero_lote.split("-")[-1]) + 1
        except (ValueError, IndexError):
            n = 1
    else:
        n = 1
    return f"{base}{n:03d}"


class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, blank=True)
    contacto = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ["nombre"]


class Producto(models.Model):
    UNIDAD_CHOICES = [
        ("KG", "Kilogramos"),
        ("G", "Gramos"),
        ("L", "Litros"),
        ("ML", "Mililitros"),
        ("UN", "Unidades"),
        ("CAJA", "Cajas"),
    ]
    CATEGORIA_CHOICES = [
        ("ABARROTES", "Abarrotes"),
        ("CARNES", "Carnes y Aves"),
        ("PESCADOS", "Pescados y Mariscos"),
        ("LACTEOS", "Lácteos y Huevos"),
        ("FRUTAS", "Frutas y Verduras"),
        ("CONGELADOS", "Congelados"),
        ("BEBIDAS", "Bebidas"),
        ("LIMPIEZA", "Aseo y Limpieza"),
        ("OTRO", "Otros"),
    ]
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default="OTRO")
    unidad_medida = models.CharField(max_length=5, choices=UNIDAD_CHOICES, default="KG")
    stock_minimo = models.FloatField(default=0, help_text="Alerta cuando el stock total baje de este valor")
    temperatura_min = models.FloatField(null=True, blank=True, help_text="°C (opcional)")
    temperatura_max = models.FloatField(null=True, blank=True, help_text="°C (opcional)")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["nombre"]


class Lote(models.Model):
    UBICACION_CHOICES = [
        ("BODEGA", "Bodega"),
        ("COCINA_FRIA", "Cocina Fría"),
        ("COCINA_CALIENTE", "Cocina Caliente"),
        ("REPOSTERIA", "Repostería"),
        ("LINEA", "Línea (Servicio)"),
        ("CAMARA_1", "Cámara 1"),
        ("CAMARA_2", "Cámara 2"),
        ("CAMARA_3", "Cámara 3"),
        ("CAMARA_4", "Cámara 4"),
        ("CAMARA_5", "Cámara 5"),
        ("OTRO", "Otro"),
    ]
    ESTADO_CHOICES = [
        ("ACTIVO", "Activo"),
        ("CONSUMIDO", "Consumido"),
        ("VENCIDO", "Vencido"),
        ("DESCARTADO", "Descartado"),
    ]
    PROCESO_CHOICES = [
        ("RECEPCION", "Recepción de Bodega"),
        ("MARINADO", "Marinado"),
        ("PORCIONADO", "Porcionado"),
        ("COCCION", "Cocción"),
        ("PREPARACION", "Preparación / Mezcla"),
        ("HORNEADO", "Horneado"),
        ("ENFRIADO", "Enfriado"),
        ("OTRO", "Otro"),
    ]

    # — Identificación —
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="lotes")
    proveedor = models.ForeignKey(
        Proveedor, on_delete=models.SET_NULL, null=True, blank=True, related_name="lotes"
    )
    numero_lote = models.CharField(max_length=60, unique=True, blank=True)
    numero_lote_proveedor = models.CharField(
        max_length=80, blank=True, verbose_name="Lote del Proveedor"
    )
    numero_guia = models.CharField(
        max_length=80, blank=True, verbose_name="Nº Guía / Factura"
    )

    # — Cantidades, Precios y Fechas —
    cantidad = models.FloatField()
    precio_unitario = models.FloatField(default=0, help_text="Costo por unidad de medida")
    fecha_recepcion = models.DateField()
    fecha_vencimiento = models.DateField()

    # — Control Sanitario —
    temperatura_recepcion = models.FloatField(
        null=True, blank=True, verbose_name="Temperatura recepción (°C)"
    )
    proceso = models.CharField(
        max_length=20,
        choices=PROCESO_CHOICES,
        default="RECEPCION",
        verbose_name="Proceso de origen",
    )

    # — Trazabilidad —
    lotes_padres = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        related_name="lotes_hijos",
        verbose_name="Lotes de origen (insumos)",
    )

    # — Estado, Ubicación, Responsable —
    ubicacion_actual = models.CharField(
        max_length=30, choices=UBICACION_CHOICES, default="BODEGA"
    )
    ubicacion_detalle = models.CharField(
        max_length=100, blank=True, help_text="Ej: Pasillo 2, Estante B"
    )
    estado = models.CharField(
        max_length=12, choices=ESTADO_CHOICES, default="ACTIVO"
    )
    responsable_registro = models.CharField(
        max_length=100, blank=True, verbose_name="Responsable de registro"
    )
    observaciones = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.numero_lote:
            self.numero_lote = _generar_numero_lote(self.producto.nombre)
        super().save(*args, **kwargs)

    @property
    def dias_restantes(self):
        return (self.fecha_vencimiento - datetime.date.today()).days

    @property
    def valor_total(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"[{self.numero_lote}] {self.producto.nombre}"

    class Meta:
        verbose_name = "Lote"
        verbose_name_plural = "Lotes"
        ordering = ["fecha_vencimiento"]


class MovimientoTrazabilidad(models.Model):
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE, related_name="movimientos")
    desde = models.CharField(max_length=30, choices=Lote.UBICACION_CHOICES)
    hacia = models.CharField(max_length=30, choices=Lote.UBICACION_CHOICES)
    cantidad = models.FloatField(null=True, blank=True, verbose_name="Cantidad despachada")
    fecha = models.DateTimeField(auto_now_add=True)
    responsable = models.CharField(max_length=80, blank=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.lote.numero_lote}: {self.desde} → {self.hacia}"

    class Meta:
        verbose_name = "Movimiento de Trazabilidad"
        verbose_name_plural = "Movimientos de Trazabilidad"
        ordering = ["-fecha"]


class RegistroServicio(models.Model):
    """Registro de salida a línea / consumo final."""
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE, related_name="servicios")
    cantidad_servida = models.FloatField()
    responsable = models.CharField(max_length=100, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Servicio {self.lote.numero_lote} — {self.fecha:%d/%m/%Y %H:%M}"

    class Meta:
        verbose_name = "Registro de Servicio"
        verbose_name_plural = "Registros de Servicio"
        ordering = ["-fecha"]


class TareaBodega(models.Model):
    """To-do list del panel de bodega."""
    texto = models.CharField(max_length=200)
    completada = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creado_por = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.texto

    class Meta:
        verbose_name = "Tarea de Bodega"
        verbose_name_plural = "Tareas de Bodega"
        ordering = ["completada", "-fecha_creacion"]

class RegistroTemperaturaCamara(models.Model):
    CAMARA_CHOICES = [
        ("CAMARA_1", "Cámara 1"),
        ("CAMARA_2", "Cámara 2"),
        ("CAMARA_3", "Cámara 3"),
        ("CAMARA_4", "Cámara 4"),
        ("CAMARA_5", "Cámara 5"),
    ]
    camara = models.CharField(max_length=20, choices=CAMARA_CHOICES)
    temperatura = models.FloatField(verbose_name="Temperatura (°C)")
    fecha_hora = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey("coalfa.Usuario", on_delete=models.SET_NULL, null=True, blank=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_camara_display()} — {self.temperatura}°C ({self.fecha_hora:%d/%m %H:%M})"

    class Meta:
        verbose_name = "Registro de Temperatura de Cámara"
        verbose_name_plural = "Registros de Temperatura de Cámaras"
        ordering = ["-fecha_hora"]
