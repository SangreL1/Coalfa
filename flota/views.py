import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Q, Count
from django.utils import timezone
from coalfa.decorators import operacional_required, audit_read_only
from .models import (
    Vehiculo,
    DocumentoVehiculo,
    PautaMantencion,
    RegistroMantencion,
    RegistroKilometraje,
    ChecklistPreUso,
    CostoVehiculo,
    ConfiguracionFlota,
    LogAlertaFlota,
)
from .forms import (
    VehiculoForm,
    DocumentoVehiculoForm,
    PautaMantencionForm,
    RegistroMantencionForm,
    RegistroKilometrajeForm,
    ChecklistPreUsoForm,
    CostoVehiculoForm,
    ConfiguracionFlotaForm,
)
from .services import verificar_y_enviar_alertas


# ==========================================
# 1. DASHBOARD DE FLOTA
# ==========================================
@operacional_required
def dashboard_flota(request):
    hoy = datetime.date.today()
    limite_30 = hoy + datetime.timedelta(days=30)
    limite_15 = hoy + datetime.timedelta(days=15)
    limite_7 = hoy + datetime.timedelta(days=7)

    vehiculos = Vehiculo.objects.filter(activo=True)
    total_vehiculos = vehiculos.count()
    operativos = vehiculos.filter(estado="OPERATIVO").count()
    en_taller = vehiculos.filter(estado="TALLER").count()
    fuera_servicio = vehiculos.filter(estado="FUERA_SERVICIO").count()

    # Documentos
    docs = DocumentoVehiculo.objects.filter(vehiculo__activo=True)
    docs_vencidos = docs.filter(fecha_vencimiento__lt=hoy).select_related("vehiculo")
    docs_urgentes_7 = docs.filter(fecha_vencimiento__gte=hoy, fecha_vencimiento__lte=limite_7).select_related("vehiculo")
    docs_aviso_30 = docs.filter(fecha_vencimiento__gte=hoy, fecha_vencimiento__lte=limite_30).select_related("vehiculo")

    # Mantenciones que requieren atención por km o fecha
    mantenciones_pendientes = []
    config = ConfiguracionFlota.get_solo()
    km_anticipacion = config.km_anticipacion_alerta or 1000

    for v in vehiculos:
        # Última mantención con próximo vencimiento
        m = v.mantenciones.filter(Q(proximo_km__isnull=False) | Q(proxima_fecha__isnull=False)).first()
        if m:
            estado_alerta = m.estado_alerta
            if estado_alerta in ("VENCIDA", "POR_VENCER"):
                mantenciones_pendientes.append(m)

    # Costos del mes actual
    primer_dia_mes = hoy.replace(day=1)
    costos_mes = CostoVehiculo.objects.filter(fecha__gte=primer_dia_mes).aggregate(
        total=Sum("monto"),
        combustible=Sum("monto", filter=Q(tipo="COMBUSTIBLE")),
        mantenciones=Sum("monto", filter=Q(tipo__in=["MANTENCION", "REPARACION"])),
    )

    # Kilometrajes recientes
    ultimos_km = RegistroKilometraje.objects.select_related("vehiculo").order_by("-fecha", "-creado_el")[:5]

    # Últimos checklists
    ultimos_checklists = ChecklistPreUso.objects.select_related("vehiculo").order_by("-fecha_hora")[:5]

    context = {
        "total_vehiculos": total_vehiculos,
        "operativos": operativos,
        "en_taller": en_taller,
        "fuera_servicio": fuera_servicio,
        "docs_vencidos_count": docs_vencidos.count(),
        "docs_vencidos": docs_vencidos[:6],
        "docs_urgentes_7": docs_urgentes_7[:6],
        "docs_aviso_30_count": docs_aviso_30.count(),
        "mantenciones_pendientes": mantenciones_pendientes[:6],
        "mantenciones_pendientes_count": len(mantenciones_pendientes),
        "costo_total_mes": costos_mes["total"] or 0,
        "costo_combustible_mes": costos_mes["combustible"] or 0,
        "costo_mantenciones_mes": costos_mes["mantenciones"] or 0,
        "ultimos_km": ultimos_km,
        "ultimos_checklists": ultimos_checklists,
        "config_flota": config,
    }
    return render(request, "flota/dashboard.html", context)


# ==========================================
# 2. GESTIÓN DE VEHÍCULOS (CRUD)
# ==========================================
@operacional_required
def lista_vehiculos(request):
    query = request.GET.get("q", "").strip()
    filtro_estado = request.GET.get("estado", "")
    filtro_asignacion = request.GET.get("asignacion", "")
    filtro_tipo = request.GET.get("tipo", "")

    vehiculos = Vehiculo.objects.all().prefetch_related("documentos", "mantenciones")

    if query:
        vehiculos = vehiculos.filter(
            Q(patente__icontains=query)
            | Q(marca__icontains=query)
            | Q(modelo__icontains=query)
            | Q(conductor_habitual__icontains=query)
        )

    if filtro_estado:
        vehiculos = vehiculos.filter(estado=filtro_estado)

    if filtro_asignacion:
        vehiculos = vehiculos.filter(asignacion=filtro_asignacion)

    if filtro_tipo:
        vehiculos = vehiculos.filter(tipo=filtro_tipo)

    context = {
        "vehiculos": vehiculos,
        "query": query,
        "filtro_estado": filtro_estado,
        "filtro_asignacion": filtro_asignacion,
        "filtro_tipo": filtro_tipo,
        "estados": Vehiculo.ESTADO_CHOICES,
        "asignaciones": Vehiculo.ASIGNACION_CHOICES,
        "tipos": Vehiculo.TIPO_CHOICES,
    }
    return render(request, "flota/lista_vehiculos.html", context)


@operacional_required
@audit_read_only
def crear_vehiculo(request):
    if request.method == "POST":
        form = VehiculoForm(request.POST)
        if form.is_valid():
            vehiculo = form.save()
            messages.success(request, f"Vehículo con patente {vehiculo.patente} registrado exitosamente.")
            return redirect("flota_detalle_vehiculo", pk=vehiculo.pk)
    else:
        form = VehiculoForm()

    return render(request, "flota/form_vehiculo.html", {"form": form, "titulo": "Registrar Nuevo Vehículo"})


@operacional_required
@audit_read_only
def editar_vehiculo(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    if request.method == "POST":
        form = VehiculoForm(request.POST, instance=vehiculo)
        if form.is_valid():
            vehiculo = form.save()
            messages.success(request, f"Vehículo {vehiculo.patente} actualizado correctamente.")
            return redirect("flota_detalle_vehiculo", pk=vehiculo.pk)
    else:
        form = VehiculoForm(instance=vehiculo)

    return render(
        request,
        "flota/form_vehiculo.html",
        {"form": form, "vehiculo": vehiculo, "titulo": f"Editar Vehículo {vehiculo.patente}"},
    )


@operacional_required
@audit_read_only
def eliminar_vehiculo(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    if request.method == "POST":
        patente = vehiculo.patente
        vehiculo.delete()
        messages.success(request, f"Vehículo {patente} eliminado del sistema.")
        return redirect("flota_lista_vehiculos")
    return render(request, "flota/confirmar_eliminar.html", {"objeto": vehiculo, "tipo": "Vehículo"})


@operacional_required
def detalle_vehiculo(request, pk):
    vehiculo = get_object_or_404(
        Vehiculo.objects.prefetch_related(
            "documentos", "mantenciones", "kilometrajes", "checklists", "costos"
        ),
        pk=pk,
    )
    hoy = datetime.date.today()

    documentos = vehiculo.documentos.all().order_by("fecha_vencimiento")
    mantenciones = vehiculo.mantenciones.all().order_by("-fecha")
    kilometrajes = vehiculo.kilometrajes.all().order_by("-fecha", "-creado_el")[:20]
    checklists = vehiculo.checklists.all().order_by("-fecha_hora")[:15]
    costos = vehiculo.costos.all().order_by("-fecha", "-creado_el")[:20]

    # Cálculos y estadísticas del vehículo
    total_gastos = vehiculo.costos.aggregate(total=Sum("monto"))["total"] or 0
    total_combustible = (
        vehiculo.costos.filter(tipo="COMBUSTIBLE").aggregate(total=Sum("monto"))["total"] or 0
    )
    total_litros = (
        vehiculo.costos.filter(tipo="COMBUSTIBLE").aggregate(litros=Sum("litros"))["litros"] or 0
    )

    context = {
        "vehiculo": vehiculo,
        "documentos": documentos,
        "mantenciones": mantenciones,
        "kilometrajes": kilometrajes,
        "checklists": checklists,
        "costos": costos,
        "total_gastos": total_gastos,
        "total_combustible": total_combustible,
        "total_litros": round(total_litros, 2),
        "hoy": hoy,
    }
    return render(request, "flota/detalle_vehiculo.html", context)


# ==========================================
# 3. GESTIÓN DE DOCUMENTOS CON VENCIMIENTO
# ==========================================
@operacional_required
@audit_read_only
def agregar_documento(request, vehiculo_id=None):
    vehiculo = None
    if vehiculo_id:
        vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_id)

    if request.method == "POST":
        form = DocumentoVehiculoForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save()
            messages.success(
                request,
                f"Documento '{doc.titulo_completo}' registrado para el vehículo {doc.vehiculo.patente}.",
            )
            return redirect("flota_detalle_vehiculo", pk=doc.vehiculo.pk)
    else:
        initial = {"vehiculo": vehiculo} if vehiculo else {}
        form = DocumentoVehiculoForm(initial=initial)

    return render(
        request,
        "flota/form_documento.html",
        {"form": form, "vehiculo": vehiculo, "titulo": "Agregar Documento con Vencimiento"},
    )


@operacional_required
@audit_read_only
def editar_documento(request, pk):
    doc = get_object_or_404(DocumentoVehiculo, pk=pk)
    if request.method == "POST":
        form = DocumentoVehiculoForm(request.POST, request.FILES, instance=doc)
        if form.is_valid():
            doc = form.save()
            messages.success(request, f"Documento de {doc.vehiculo.patente} actualizado.")
            return redirect("flota_detalle_vehiculo", pk=doc.vehiculo.pk)
    else:
        form = DocumentoVehiculoForm(instance=doc)

    return render(
        request,
        "flota/form_documento.html",
        {"form": form, "vehiculo": doc.vehiculo, "titulo": f"Editar Documento - {doc.vehiculo.patente}"},
    )


@operacional_required
@audit_read_only
def eliminar_documento(request, pk):
    doc = get_object_or_404(DocumentoVehiculo, pk=pk)
    vehiculo_pk = doc.vehiculo.pk
    if request.method == "POST":
        titulo = doc.titulo_completo
        doc.delete()
        messages.success(request, f"Documento '{titulo}' eliminado.")
        return redirect("flota_detalle_vehiculo", pk=vehiculo_pk)
    return render(request, "flota/confirmar_eliminar.html", {"objeto": doc, "tipo": "Documento"})


# ==========================================
# 4. GESTIÓN DE MANTENCIONES
# ==========================================
@operacional_required
def lista_mantenciones(request):
    query = request.GET.get("q", "").strip()
    vehiculo_id = request.GET.get("vehiculo", "")
    tipo_servicio = request.GET.get("tipo", "")

    mantenciones = RegistroMantencion.objects.select_related("vehiculo", "pauta").order_by("-fecha")

    if query:
        mantenciones = mantenciones.filter(
            Q(vehiculo__patente__icontains=query)
            | Q(titulo__icontains=query)
            | Q(taller__icontains=query)
        )
    if vehiculo_id:
        mantenciones = mantenciones.filter(vehiculo_id=vehiculo_id)
    if tipo_servicio:
        mantenciones = mantenciones.filter(tipo_servicio=tipo_servicio)

    context = {
        "mantenciones": mantenciones,
        "vehiculos": Vehiculo.objects.filter(activo=True),
        "pautas": PautaMantencion.objects.filter(activo=True),
        "tipos": RegistroMantencion.TIPO_SERVICIO_CHOICES,
        "query": query,
        "vehiculo_id": vehiculo_id,
        "tipo_servicio": tipo_servicio,
    }
    return render(request, "flota/lista_mantenciones.html", context)


@operacional_required
@audit_read_only
def agregar_mantencion(request, vehiculo_id=None):
    vehiculo = None
    if vehiculo_id:
        vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_id)

    if request.method == "POST":
        form = RegistroMantencionForm(request.POST, request.FILES)
        if form.is_valid():
            mant = form.save(commit=False)
            if not mant.responsable and request.user.is_authenticated:
                mant.responsable = request.user.get_full_name() or str(request.user)
            mant.save()

            # Registrar también automáticamente como costo si tiene valor > 0
            if mant.costo and mant.costo > 0:
                CostoVehiculo.objects.create(
                    vehiculo=mant.vehiculo,
                    tipo="MANTENCION" if mant.tipo_servicio == "PREVENTIVA" else "REPARACION",
                    fecha=mant.fecha,
                    monto=mant.costo,
                    kilometraje=mant.kilometraje,
                    proveedor=mant.taller,
                    comprobante=mant.comprobante,
                    observaciones=f"Generado automáticamente desde mantención: {mant.titulo}",
                    responsable=mant.responsable,
                )

            messages.success(
                request,
                f"Mantención '{mant.titulo}' registrada para {mant.vehiculo.patente}. Próximo km: {mant.proximo_km or 'No asignado'}.",
            )
            return redirect("flota_detalle_vehiculo", pk=mant.vehiculo.pk)
    else:
        initial = {}
        if vehiculo:
            initial = {"vehiculo": vehiculo, "kilometraje": vehiculo.kilometraje_actual}
        form = RegistroMantencionForm(initial=initial)

    return render(
        request,
        "flota/form_mantencion.html",
        {"form": form, "vehiculo": vehiculo, "titulo": "Registrar Nueva Mantención"},
    )


@operacional_required
@audit_read_only
def eliminar_mantencion(request, pk):
    mant = get_object_or_404(RegistroMantencion, pk=pk)
    vehiculo_pk = mant.vehiculo.pk
    if request.method == "POST":
        titulo = mant.titulo
        mant.delete()
        messages.success(request, f"Registro de mantención '{titulo}' eliminado.")
        return redirect("flota_detalle_vehiculo", pk=vehiculo_pk)
    return render(request, "flota/confirmar_eliminar.html", {"objeto": mant, "tipo": "Mantención"})


# ==========================================
# 5. REGISTRO DE KILOMETRAJE RÁPIDO (EXPRESS / MÓVIL)
# ==========================================
@operacional_required
@audit_read_only
def registrar_kilometraje_express(request):
    """
    Formulario ultra rápido pensado para conductores o administradores desde el celular.
    """
    vehiculo_id = request.GET.get("vehiculo")
    vehiculo_precargado = None
    if vehiculo_id:
        vehiculo_precargado = Vehiculo.objects.filter(pk=vehiculo_id, activo=True).first()

    if request.method == "POST":
        form = RegistroKilometrajeForm(request.POST)
        if form.is_valid():
            km_reg = form.save()
            messages.success(
                request,
                f"✅ Odómetro actualizado: {km_reg.vehiculo.patente} a {km_reg.kilometraje:,} km.".replace(",", "."),
            )
            # Si vino con parámetro next, volver allí
            next_url = request.POST.get("next") or request.GET.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("flota_dashboard")
    else:
        initial = {}
        if vehiculo_precargado:
            initial = {
                "vehiculo": vehiculo_precargado,
                "kilometraje": vehiculo_precargado.kilometraje_actual,
                "conductor_o_responsable": vehiculo_precargado.conductor_habitual or (request.user.get_full_name() if request.user.is_authenticated else ""),
            }
        elif request.user.is_authenticated:
            initial = {"conductor_o_responsable": request.user.get_full_name()}
        form = RegistroKilometrajeForm(initial=initial)

    ultimos = RegistroKilometraje.objects.select_related("vehiculo").order_by("-fecha", "-creado_el")[:10]

    return render(
        request,
        "flota/registro_kilometraje.html",
        {"form": form, "vehiculo_precargado": vehiculo_precargado, "ultimos": ultimos},
    )


# ==========================================
# 6. CHECKLIST RÁPIDO PRE-USO (MÓVIL)
# ==========================================
@operacional_required
@audit_read_only
def checklist_preuso(request, vehiculo_id=None):
    vehiculo = None
    if vehiculo_id:
        vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_id)

    if request.method == "POST":
        form = ChecklistPreUsoForm(request.POST)
        if form.is_valid():
            chk = form.save()
            if chk.aprobado_para_circular:
                messages.success(request, f"✅ Checklist registrado: Vehículo {chk.vehiculo.patente} APTO para circular.")
            else:
                messages.warning(
                    request,
                    f"⚠️ Checklist registrado: Vehículo {chk.vehiculo.patente} CON OBSERVACIONES / NO APTO. Revisar novedades.",
                )
            return redirect("flota_detalle_vehiculo", pk=chk.vehiculo.pk)
    else:
        initial = {}
        if vehiculo:
            initial = {
                "vehiculo": vehiculo,
                "kilometraje": vehiculo.kilometraje_actual,
                "conductor": vehiculo.conductor_habitual or (request.user.get_full_name() if request.user.is_authenticated else ""),
            }
        elif request.user.is_authenticated:
            initial = {"conductor": request.user.get_full_name()}
        form = ChecklistPreUsoForm(initial=initial)

    return render(
        request,
        "flota/checklist_preuso.html",
        {"form": form, "vehiculo": vehiculo, "titulo": "Checklist Rápido Pre-Uso de Vehículo"},
    )


@operacional_required
def lista_checklists(request):
    checklists = ChecklistPreUso.objects.select_related("vehiculo").order_by("-fecha_hora")
    return render(request, "flota/lista_checklists.html", {"checklists": checklists})


# ==========================================
# 7. COSTOS Y COMBUSTIBLE
# ==========================================
@operacional_required
def lista_costos(request):
    query = request.GET.get("q", "").strip()
    tipo = request.GET.get("tipo", "")
    vehiculo_id = request.GET.get("vehiculo", "")

    costos = CostoVehiculo.objects.select_related("vehiculo").order_by("-fecha", "-creado_el")

    if query:
        costos = costos.filter(
            Q(vehiculo__patente__icontains=query)
            | Q(proveedor__icontains=query)
            | Q(numero_documento__icontains=query)
        )
    if tipo:
        costos = costos.filter(tipo=tipo)
    if vehiculo_id:
        costos = costos.filter(vehiculo_id=vehiculo_id)

    # Totales
    totales = costos.aggregate(
        total=Sum("monto"),
        combustible=Sum("monto", filter=Q(tipo="COMBUSTIBLE")),
        mantenciones=Sum("monto", filter=Q(tipo__in=["MANTENCION", "REPARACION"])),
        otros=Sum("monto", filter=~Q(tipo__in=["COMBUSTIBLE", "MANTENCION", "REPARACION"])),
    )

    context = {
        "costos": costos,
        "vehiculos": Vehiculo.objects.filter(activo=True),
        "tipos": CostoVehiculo.TIPO_CHOICES,
        "totales": totales,
        "query": query,
        "tipo_filtro": tipo,
        "vehiculo_id": vehiculo_id,
    }
    return render(request, "flota/lista_costos.html", context)


@operacional_required
@audit_read_only
def agregar_costo(request, vehiculo_id=None):
    vehiculo = None
    if vehiculo_id:
        vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_id)

    if request.method == "POST":
        form = CostoVehiculoForm(request.POST, request.FILES)
        if form.is_valid():
            costo = form.save(commit=False)
            if not costo.responsable and request.user.is_authenticated:
                costo.responsable = request.user.get_full_name() or str(request.user)
            costo.save()
            messages.success(
                request,
                f"Gasto de ${costo.monto:,} CLP registrado para {costo.vehiculo.patente} ({costo.get_tipo_display()}).".replace(",", "."),
            )
            return redirect("flota_detalle_vehiculo", pk=costo.vehiculo.pk)
    else:
        initial = {}
        if vehiculo:
            initial = {"vehiculo": vehiculo, "kilometraje": vehiculo.kilometraje_actual}
        form = CostoVehiculoForm(initial=initial)

    return render(
        request,
        "flota/form_costo.html",
        {"form": form, "vehiculo": vehiculo, "titulo": "Registrar Gasto / Combustible"},
    )


@operacional_required
@audit_read_only
def eliminar_costo(request, pk):
    costo = get_object_or_404(CostoVehiculo, pk=pk)
    vehiculo_pk = costo.vehiculo.pk
    if request.method == "POST":
        costo.delete()
        messages.success(request, "Registro de gasto eliminado correctamente.")
        return redirect("flota_detalle_vehiculo", pk=vehiculo_pk)
    return render(request, "flota/confirmar_eliminar.html", {"objeto": costo, "tipo": "Gasto"})


# ==========================================
# 8. PAUTAS DE MANTENCIÓN
# ==========================================
@operacional_required
def pautas_mantencion(request):
    pautas = PautaMantencion.objects.all()
    form = PautaMantencionForm()

    if request.method == "POST":
        form = PautaMantencionForm(request.POST)
        if form.is_valid():
            pauta = form.save()
            messages.success(request, f"Pauta de mantención '{pauta.nombre}' creada exitosamente.")
            return redirect("flota_pautas")

    return render(request, "flota/pautas_mantencion.html", {"pautas": pautas, "form": form})


@operacional_required
@audit_read_only
def eliminar_pauta(request, pk):
    pauta = get_object_or_404(PautaMantencion, pk=pk)
    if request.method == "POST":
        nombre = pauta.nombre
        pauta.delete()
        messages.success(request, f"Pauta '{nombre}' eliminada.")
        return redirect("flota_pautas")
    return render(request, "flota/confirmar_eliminar.html", {"objeto": pauta, "tipo": "Pauta de Mantención"})


# ==========================================
# 9. PANEL DE ALERTAS Y CONFIGURACIÓN DE CORREOS
# ==========================================
@operacional_required
def panel_alertas(request):
    hoy = datetime.date.today()
    config = ConfiguracionFlota.get_solo()

    # Todos los documentos con semáforo
    docs = DocumentoVehiculo.objects.filter(vehiculo__activo=True).select_related("vehiculo").order_by("fecha_vencimiento")
    docs_vencidos = [d for d in docs if d.dias_restantes < 0]
    docs_urgentes_7 = [d for d in docs if 0 <= d.dias_restantes <= 7]
    docs_alerta_15 = [d for d in docs if 8 <= d.dias_restantes <= 15]
    docs_aviso_30 = [d for d in docs if 16 <= d.dias_restantes <= 30]

    # Mantenciones
    mantenciones = RegistroMantencion.objects.filter(vehiculo__activo=True).select_related("vehiculo", "pauta")
    mant_vencidas = [m for m in mantenciones if m.estado_alerta == "VENCIDA"]
    mant_por_vencer = [m for m in mantenciones if m.estado_alerta == "POR_VENCER"]

    # Historial de alertas enviadas
    logs = LogAlertaFlota.objects.select_related("vehiculo").order_by("-fecha_envio")[:25]

    context = {
        "docs_vencidos": docs_vencidos,
        "docs_urgentes_7": docs_urgentes_7,
        "docs_alerta_15": docs_alerta_15,
        "docs_aviso_30": docs_aviso_30,
        "mant_vencidas": mant_vencidas,
        "mant_por_vencer": mant_por_vencer,
        "logs": logs,
        "config": config,
        "total_alertas": len(docs_vencidos) + len(docs_urgentes_7) + len(docs_alerta_15) + len(mant_vencidas) + len(mant_por_vencer),
    }
    return render(request, "flota/panel_alertas.html", context)


@operacional_required
@audit_read_only
def configuracion_alertas(request):
    config = ConfiguracionFlota.get_solo()

    if request.method == "POST":
        form = ConfiguracionFlotaForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Configuración de alertas por correo guardada correctamente.")
            return redirect("flota_configuracion_alertas")
    else:
        form = ConfiguracionFlotaForm(instance=config)

    logs = LogAlertaFlota.objects.order_by("-fecha_envio")[:20]

    context = {
        "form": form,
        "config": config,
        "logs": logs,
        "lista_correos": config.get_lista_correos(),
    }
    return render(request, "flota/configuracion_alertas.html", context)


@operacional_required
@audit_read_only
def disparar_alertas_ahora(request):
    """
    Ejecuta manualmente el chequeo y envío de alertas desde la interfaz web.
    """
    if request.method == "POST":
        resultado = verificar_y_enviar_alertas(forzar=True)
        if resultado.get("enviado"):
            dest_str = ", ".join(resultado.get("destinatarios", []))
            messages.success(
                request,
                f"🚀 Notificaciones enviadas exitosamente a {dest_str}. Total alertas reportadas: {resultado.get('total_alertas')}.",
            )
        else:
            motivo = resultado.get("motivo") or resultado.get("error") or "No se pudo realizar el envío."
            messages.warning(request, f"ℹ️ Envío de alertas: {motivo}")

    return redirect("flota_panel_alertas")


@operacional_required
@audit_read_only
def enviar_correo_prueba(request):
    """
    Permite enviar un correo de prueba a una dirección específica para validar SMTP.
    """
    if request.method == "POST":
        correo_test = request.POST.get("correo_prueba", "").strip()
        if not correo_test or "@" not in correo_test:
            messages.error(request, "Por favor indica un correo electrónico válido para la prueba.")
            return redirect("flota_configuracion_alertas")

        resultado = verificar_y_enviar_alertas(forzar=True, correo_especifico=correo_test)
        if resultado.get("enviado"):
            messages.success(request, f"✅ Correo de prueba enviado con éxito a '{correo_test}'. Revisa tu bandeja de entrada.")
        else:
            err = resultado.get("error") or resultado.get("motivo") or "Error desconocido."
            messages.error(request, f"❌ No se pudo enviar el correo de prueba: {err}")

    return redirect("flota_configuracion_alertas")
