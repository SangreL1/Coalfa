from django.db import models
from django.utils import timezone
import datetime


class Vehiculo(models.Model):
    TIPO_CHOICES = [
        ("CAMIONETA", "Camioneta"),
        ("FURGON", "Furgón"),
        ("AUTO", "Automóvil / Sedán"),
        ("CAMION", "Camión"),
        ("MINIBUS", "Minibús / Van"),
        ("MOTO", "Motocicleta"),
        ("OTRO", "Otro"),
    ]

    ASIGNACION_CHOICES = [
        ("CASINO", "Casino"),
        ("FAENA", "Faena"),
        ("ADMINISTRACION", "Administración"),
        ("BODEGA", "Bodega / Logística"),
        ("OTRO", "Otro"),
    ]

    ESTADO_CHOICES = [
        ("OPERATIVO", "Operativo"),
        ("TALLER", "En Taller / Mantención"),
        ("FUERA_SERVICIO", "Fuera de Servicio"),
    ]

    patente = models.CharField(
        max_length=12,
        unique=True,
        verbose_name="Patente",
        help_text="Ej: ABCD12 o AB1234",
    )
    marca = models.CharField(max_length=60, verbose_name="Marca")
    modelo = models.CharField(max_length=60, verbose_name="Modelo")
    anio = models.PositiveIntegerField(verbose_name="Año")
    tipo = models.CharField(
        max_length=20, choices=TIPO_CHOICES, default="CAMIONETA", verbose_name="Tipo de Vehículo"
    )
    asignacion = models.CharField(
        max_length=30, choices=ASIGNACION_CHOICES, default="CASINO", verbose_name="Asignación"
    )
    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default="OPERATIVO", verbose_name="Estado Operativo"
    )

    kilometraje_actual = models.PositiveIntegerField(
        default=0, verbose_name="Kilometraje Actual (km)"
    )
    fecha_actualizacion_km = models.DateField(
        default=datetime.date.today, verbose_name="Fecha Última Actualización Km"
    )
    conductor_habitual = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Conductor / Responsable Habitual",
        help_text="Nombre de quien suele operar el vehículo",
    )
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    creado_el = models.DateTimeField(auto_now_add=True)
    actualizado_el = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"
        ordering = ["patente"]

    def save(self, *args, **kwargs):
        if self.patente:
            self.patente = self.patente.strip().upper().replace(" ", "").replace("-", "")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patente} - {self.marca} {self.modelo} ({self.get_asignacion_display()})"

    @property
    def dias_sin_actualizar_km(self):
        if self.fecha_actualizacion_km:
            return (datetime.date.today() - self.fecha_actualizacion_km).days
        return 999

    @property
    def documentos_activos(self):
        return self.documentos.all().order_by("fecha_vencimiento")

    @property
    def documentos_vencidos(self):
        hoy = datetime.date.today()
        return [doc for doc in self.documentos_activos if doc.fecha_vencimiento < hoy]

    @property
    def documentos_por_vencer_30(self):
        hoy = datetime.date.today()
        limite = hoy + datetime.timedelta(days=30)
        return [
            doc for doc in self.documentos_activos
            if hoy <= doc.fecha_vencimiento <= limite
        ]

    @property
    def foto_portada(self):
        """Retorna la instancia FotoVehiculo principal (o la primera), no la URL."""
        return self.fotos.filter(es_principal=True).first() or self.fotos.first()

    @property
    def total_fotos(self):
        return self.fotos.count()


class FotoVehiculo(models.Model):
    ANGULO_CHOICES = [
        ("FRONTAL", "Frontal"),
        ("LATERAL_IZQ", "Lateral Izquierdo"),
        ("LATERAL_DER", "Lateral Derecho"),
        ("TRASERA", "Trasera"),
        ("INTERIOR", "Interior / Tablero"),
        ("GENERAL", "General / Otro"),
    ]

    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.CASCADE, related_name="fotos", verbose_name="Vehículo"
    )
    imagen = models.ImageField(upload_to="flota/vehiculos/", verbose_name="Fotografía")
    angulo = models.CharField(
        max_length=30, choices=ANGULO_CHOICES, default="GENERAL", verbose_name="Ángulo / Vista"
    )
    descripcion = models.CharField(max_length=150, blank=True, verbose_name="Descripción (Opcional)")
    es_principal = models.BooleanField(default=False, verbose_name="Foto Principal de Portada")
    subido_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Foto de Vehículo"
        verbose_name_plural = "Fotos de Vehículos"
        ordering = ["-es_principal", "-subido_el"]

    def __str__(self):
        return f"Foto {self.get_angulo_display()} - {self.vehiculo.patente}"


class DocumentoVehiculo(models.Model):
    TIPO_CHOICES = [
        ("REVISION_TECNICA", "Revisión Técnica"),
        ("PERMISO_CIRCULACION", "Permiso de Circulación"),
        ("SOAP", "SOAP (Seguro Obligatorio)"),
        ("GASES", "Certificado de Emisiones / Gases"),
        ("SEGURO_ADICIONAL", "Seguro Adicional / Flota"),
        ("PADRON", "Padrón del Vehículo"),
        ("OTRO", "Otro Documento"),
    ]

    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.CASCADE, related_name="documentos", verbose_name="Vehículo"
    )
    tipo_documento = models.CharField(
        max_length=30, choices=TIPO_CHOICES, verbose_name="Tipo de Documento"
    )
    nombre_personalizado = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nombre Descriptivo",
        help_text="Opcional. Útil si seleccionas 'Otro Documento' o deseas detallar póliza",
    )
    numero_documento_o_poliza = models.CharField(
        max_length=80, blank=True, verbose_name="Nº Documento / Póliza / Certificado"
    )
    entidad_emisora = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Entidad Emisora",
        help_text="Ej: PRT San Dámaso, Municipalidad, Aseguradora BCI",
    )
    fecha_emision = models.DateField(
        null=True, blank=True, verbose_name="Fecha de Emisión"
    )
    fecha_vencimiento = models.DateField(verbose_name="Fecha de Vencimiento")
    archivo = models.FileField(
        upload_to="flota/documentos/",
        null=True,
        blank=True,
        verbose_name="Archivo Adjunto (PDF o Foto)",
    )
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    creado_el = models.DateTimeField(auto_now_add=True)
    actualizado_el = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Documento de Vehículo"
        verbose_name_plural = "Documentos de Vehículos"
        ordering = ["fecha_vencimiento"]

    def __str__(self):
        nombre = self.nombre_personalizado or self.get_tipo_documento_display()
        return f"{self.vehiculo.patente} - {nombre} (Vence: {self.fecha_vencimiento.strftime('%d/%m/%Y')})"

    @property
    def titulo_completo(self):
        if self.nombre_personalizado and self.tipo_documento == "OTRO":
            return self.nombre_personalizado
        return self.get_tipo_documento_display()

    @property
    def dias_restantes(self):
        return (self.fecha_vencimiento - datetime.date.today()).days

    @property
    def estado_alerta(self):
        dias = self.dias_restantes
        if dias < 0:
            return "VENCIDO"
        elif dias <= 7:
            return "URGENTE_7"
        elif dias <= 15:
            return "ALERTA_15"
        elif dias <= 30:
            return "AVISO_30"
        return "VIGENTE"

    @property
    def badge_class(self):
        st = self.estado_alerta
        if st == "VENCIDO":
            return "badge-licencia"  # Rojo
        elif st in ("URGENTE_7", "ALERTA_15"):
            return "badge-vacaciones"  # Amarillo/Naranjo
        elif st == "AVISO_30":
            return "badge-bodega"  # Azul/Púrpura
        return "badge-activo"  # Verde


class PautaMantencion(models.Model):
    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre de la Pauta / Servicio",
        help_text="Ej: Cambio de Aceite y Filtro, Frenos, Rotación Neumáticos",
    )
    intervalo_km = models.PositiveIntegerField(
        default=10000,
        verbose_name="Intervalo de Kilómetros",
        help_text="Cada cuántos km se debe realizar (0 si no aplica por km)",
    )
    intervalo_meses = models.PositiveIntegerField(
        default=6,
        verbose_name="Intervalo de Meses",
        help_text="Cada cuántos meses se debe realizar (0 si no aplica por tiempo)",
    )
    descripcion = models.TextField(blank=True, verbose_name="Descripción / Instrucciones")
    activo = models.BooleanField(default=True, verbose_name="Activa")

    class Meta:
        verbose_name = "Pauta de Mantención"
        verbose_name_plural = "Pautas de Mantención"
        ordering = ["nombre"]

    def __str__(self):
        reglas = []
        if self.intervalo_km:
            reglas.append(f"cada {self.intervalo_km:,} km".replace(",", "."))
        if self.intervalo_meses:
            reglas.append(f"cada {self.intervalo_meses} meses")
        regla_str = " o ".join(reglas) if reglas else "Manual"
        return f"{self.nombre} ({regla_str})"


class RegistroMantencion(models.Model):
    TIPO_SERVICIO_CHOICES = [
        ("PREVENTIVA", "Mantención Preventiva"),
        ("CORRECTIVA", "Reparación / Correctiva"),
    ]

    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.CASCADE, related_name="mantenciones", verbose_name="Vehículo"
    )
    pauta = models.ForeignKey(
        PautaMantencion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="registros",
        verbose_name="Pauta Asociada (Opcional)",
    )
    tipo_servicio = models.CharField(
        max_length=20,
        choices=TIPO_SERVICIO_CHOICES,
        default="PREVENTIVA",
        verbose_name="Tipo de Servicio",
    )
    titulo = models.CharField(
        max_length=150,
        verbose_name="Título / Detalle",
        help_text="Ej: Cambio de aceite 10W40, filtro y revisión de frenos",
    )
    fecha = models.DateField(default=datetime.date.today, verbose_name="Fecha de Ejecución")
    kilometraje = models.PositiveIntegerField(
        verbose_name="Kilometraje al Momento del Servicio"
    )
    taller = models.CharField(
        max_length=120, blank=True, verbose_name="Taller / Mecánico / Proveedor"
    )
    costo = models.PositiveIntegerField(
        default=0, verbose_name="Costo Total (CLP)", help_text="Monto en pesos chilenos"
    )
    proximo_km = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Próximo Vencimiento (km)",
        help_text="Calculado o manual. Kilometraje para el próximo servicio.",
    )
    proxima_fecha = models.DateField(
        null=True,
        blank=True,
        verbose_name="Próximo Vencimiento (Fecha)",
        help_text="Calculado o manual. Fecha límite para el próximo servicio.",
    )
    comprobante = models.FileField(
        upload_to="flota/mantenciones/",
        null=True,
        blank=True,
        verbose_name="Comprobante / Factura / Orden de Trabajo",
    )
    observaciones = models.TextField(blank=True, verbose_name="Observaciones / Trabajos Realizados")
    responsable = models.CharField(
        max_length=100, blank=True, verbose_name="Responsable / Registrado por"
    )
    creado_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Registro de Mantención"
        verbose_name_plural = "Historial de Mantenciones"
        ordering = ["-fecha", "-kilometraje"]

    def __str__(self):
        return f"{self.vehiculo.patente} - {self.titulo} ({self.fecha.strftime('%d/%m/%Y')})"

    def save(self, *args, **kwargs):
        # Si tiene pauta asociada y no se definió proximo_km / proxima_fecha, calcular automáticamente
        if self.pauta:
            if not self.proximo_km and self.pauta.intervalo_km:
                self.proximo_km = self.kilometraje + self.pauta.intervalo_km
            if not self.proxima_fecha and self.pauta.intervalo_meses and self.fecha:
                # Sumar meses aproximadamente (30 días por mes)
                dias_sumar = self.pauta.intervalo_meses * 30
                self.proxima_fecha = self.fecha + datetime.timedelta(days=dias_sumar)
        super().save(*args, **kwargs)

        # Actualizar kilometraje del vehículo si este servicio registró un km mayor
        if self.kilometraje > self.vehiculo.kilometraje_actual:
            self.vehiculo.kilometraje_actual = self.kilometraje
            self.vehiculo.fecha_actualizacion_km = self.fecha
            self.vehiculo.save()

    @property
    def km_restantes(self):
        if self.proximo_km is not None:
            return self.proximo_km - self.vehiculo.kilometraje_actual
        return None

    @property
    def dias_restantes_fecha(self):
        if self.proxima_fecha:
            return (self.proxima_fecha - datetime.date.today()).days
        return None

    @property
    def estado_alerta(self):
        """Determina si la próxima mantención está al día, por vencer o vencida."""
        vencido_km = self.km_restantes is not None and self.km_restantes <= 0
        vencido_fecha = self.dias_restantes_fecha is not None and self.dias_restantes_fecha <= 0

        if vencido_km or vencido_fecha:
            return "VENCIDA"

        por_vencer_km = self.km_restantes is not None and self.km_restantes <= 1000
        por_vencer_fecha = self.dias_restantes_fecha is not None and self.dias_restantes_fecha <= 15

        if por_vencer_km or por_vencer_fecha:
            return "POR_VENCER"

        return "AL_DIA"


class RegistroKilometraje(models.Model):
    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.CASCADE, related_name="kilometrajes", verbose_name="Vehículo"
    )
    kilometraje = models.PositiveIntegerField(verbose_name="Kilometraje Registrado (km)")
    fecha = models.DateField(default=datetime.date.today, verbose_name="Fecha")
    conductor_o_responsable = models.CharField(
        max_length=100, verbose_name="Conductor / Registrado por"
    )
    origen_destino = models.CharField(
        max_length=150, blank=True, verbose_name="Ruta / Destino (Opcional)"
    )
    observaciones = models.CharField(max_length=255, blank=True, verbose_name="Observaciones")
    creado_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Registro de Kilometraje"
        verbose_name_plural = "Registros de Kilometraje"
        ordering = ["-fecha", "-creado_el"]

    def __str__(self):
        return f"{self.vehiculo.patente} - {self.kilometraje:,} km ({self.fecha.strftime('%d/%m/%Y')})".replace(",", ".")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Actualizar kilometraje del vehículo si es mayor
        if self.kilometraje > self.vehiculo.kilometraje_actual:
            self.vehiculo.kilometraje_actual = self.kilometraje
            self.vehiculo.fecha_actualizacion_km = self.fecha
            self.vehiculo.save()


class ChecklistPreUso(models.Model):
    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.CASCADE, related_name="checklists", verbose_name="Vehículo"
    )
    fecha_hora = models.DateTimeField(default=timezone.now, verbose_name="Fecha y Hora")
    conductor = models.CharField(max_length=100, verbose_name="Conductor / Inspector")
    kilometraje = models.PositiveIntegerField(verbose_name="Kilometraje Actual")

    # Ítems de inspección rápida
    luces_ok = models.BooleanField(
        default=True, verbose_name="Luces (altas, bajas, viraje, freno y reversa)"
    )
    neumaticos_ok = models.BooleanField(
        default=True, verbose_name="Neumáticos (presión, desgaste visible y tuercas)"
    )
    fluidos_ok = models.BooleanField(
        default=True, verbose_name="Niveles de fluidos (aceite de motor, agua/refrigerante, frenos)"
    )
    frenos_ok = models.BooleanField(
        default=True, verbose_name="Frenos y freno de estacionamiento"
    )
    documentos_ok = models.BooleanField(
        default=True, verbose_name="Documentación vigente a bordo (Revisión técnica, SOAP, permiso)"
    )
    seguridad_ok = models.BooleanField(
        default=True, verbose_name="Elementos de seguridad (extintor vigente, gata, rueda repuesto, chaleco)"
    )
    carroceria_ok = models.BooleanField(
        default=True, verbose_name="Carrocería, espejos y parabrisas sin trizaduras graves"
    )
    limpieza_ok = models.BooleanField(
        default=True, verbose_name="Limpieza interior de cabina y visibilidad"
    )

    aprobado_para_circular = models.BooleanField(
        default=True, verbose_name="¿Vehículo Apto para Operar?"
    )
    observaciones = models.TextField(
        blank=True, verbose_name="Observaciones / Novedades Detectadas"
    )
    creado_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Checklist Pre-Uso"
        verbose_name_plural = "Checklists Pre-Uso"
        ordering = ["-fecha_hora"]

    def __str__(self):
        estado = "APROBADO" if self.aprobado_para_circular else "CON OBSERVACIONES"
        return f"{self.vehiculo.patente} - {estado} ({self.fecha_hora.strftime('%d/%m/%Y %H:%M')})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.kilometraje > self.vehiculo.kilometraje_actual:
            self.vehiculo.kilometraje_actual = self.kilometraje
            self.vehiculo.fecha_actualizacion_km = self.fecha_hora.date()
            self.vehiculo.save()


class CostoVehiculo(models.Model):
    TIPO_CHOICES = [
        ("COMBUSTIBLE", "Combustible (Diesel / Gasolina)"),
        ("MANTENCION", "Mantención / Servicio"),
        ("REPARACION", "Reparación / Repuesto"),
        ("PEAJE", "Peajes / TAG / Estacionamiento"),
        ("LAVADO", "Lavado / Aseo"),
        ("SEGURO", "Seguro / Póliza"),
        ("OTRO", "Otro Gasto"),
    ]

    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.CASCADE, related_name="costos", verbose_name="Vehículo"
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo de Costo")
    fecha = models.DateField(default=datetime.date.today, verbose_name="Fecha del Gasto")
    monto = models.PositiveIntegerField(verbose_name="Monto Total (CLP)")
    litros = models.FloatField(
        null=True, blank=True, verbose_name="Litros Cargados (si es combustible)"
    )
    kilometraje = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Kilometraje al Cargar (opcional)"
    )
    proveedor = models.CharField(
        max_length=120, blank=True, verbose_name="Estación / Proveedor / Taller"
    )
    numero_documento = models.CharField(
        max_length=60, blank=True, verbose_name="Nº Boleta / Factura"
    )
    comprobante = models.FileField(
        upload_to="flota/costos/", null=True, blank=True, verbose_name="Comprobante Adjunto"
    )
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    responsable = models.CharField(max_length=100, blank=True, verbose_name="Registrado por")
    creado_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Costo de Vehículo"
        verbose_name_plural = "Costos y Combustible"
        ordering = ["-fecha", "-creado_el"]

    def __str__(self):
        return f"{self.vehiculo.patente} - {self.get_tipo_display()}: ${self.monto:,} CLP ({self.fecha.strftime('%d/%m/%Y')})".replace(",", ".")


class ConfiguracionFlota(models.Model):
    """
    Configuración global persistente para el envío de alertas automáticas por correo.
    """
    correos_notificacion = models.TextField(
        default="admin@coalfa.cl",
        verbose_name="Correos de Notificación",
        help_text="Direcciones de correo donde llegarán las alertas. Separar con comas o saltos de línea.",
    )
    alertar_30_dias = models.BooleanField(
        default=True, verbose_name="Aviso a 30 días del vencimiento"
    )
    alertar_15_dias = models.BooleanField(
        default=True, verbose_name="Aviso a 15 días del vencimiento"
    )
    alertar_7_dias = models.BooleanField(
        default=True, verbose_name="Aviso urgente a 7 días del vencimiento"
    )
    alertar_vencidos = models.BooleanField(
        default=True, verbose_name="Aviso diario de documentos ya vencidos"
    )
    alertar_km = models.BooleanField(
        default=True, verbose_name="Alertas de mantención por kilometraje"
    )
    km_anticipacion_alerta = models.PositiveIntegerField(
        default=1000,
        verbose_name="Km de anticipación para avisar mantención",
        help_text="Ej: avisar cuando falten 1.000 km o menos",
    )
    asunto_alerta = models.CharField(
        max_length=150,
        default="[COALFA] Alerta de Flota: Vencimientos y Mantenciones",
        verbose_name="Asunto del Correo",
    )
    activo = models.BooleanField(
        default=True, verbose_name="Envío automático activo"
    )
    ultimo_envio = models.DateTimeField(
        null=True, blank=True, verbose_name="Fecha del último envío exitoso"
    )

    class Meta:
        verbose_name = "Configuración de Flota y Alertas"
        verbose_name_plural = "Configuraciones de Flota"

    def __str__(self):
        return f"Configuración de Alertas Flota (Activo: {self.activo})"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj

    def get_lista_correos(self):
        """Retorna una lista limpia de emails válidos."""
        if not self.correos_notificacion:
            return []
        raw = self.correos_notificacion.replace("\n", ",").replace(";", ",")
        correos = [c.strip() for c in raw.split(",") if c.strip() and "@" in c]
        return list(dict.fromkeys(correos))  # Sin duplicados manteniendo orden


class LogAlertaFlota(models.Model):
    """
    Registro histórico de alertas enviadas para evitar duplicaciones en el mismo tramo o día.
    """
    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.CASCADE, null=True, blank=True, related_name="alertas_enviadas"
    )
    tipo = models.CharField(max_length=30)  # DOCUMENTO, MANTENCION, RESUMEN
    referencia_id = models.CharField(max_length=60, blank=True)
    etapa = models.CharField(max_length=30)  # 30_DIAS, 15_DIAS, 7_DIAS, VENCIDO, KM, RESUMEN_GLOBAL
    fecha_envio = models.DateTimeField(auto_now_add=True)
    destinatarios = models.TextField()
    resumen_items = models.TextField(blank=True)
    exitoso = models.BooleanField(default=True)
    error_mensaje = models.TextField(blank=True)

    class Meta:
        verbose_name = "Historial de Alerta Enviada"
        verbose_name_plural = "Historial de Alertas Enviadas"
        ordering = ["-fecha_envio"]

    def __str__(self):
        return f"[{self.fecha_envio.strftime('%d/%m/%Y %H:%M')}] {self.tipo} - {self.etapa} ({self.vehiculo.patente if self.vehiculo else 'Flota'})"
