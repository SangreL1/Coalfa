import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from coalfa.decorators import operacional_required, audit_read_only
from .models import (
    Vehiculo,
    FotoVehiculo,
    DocumentoVehiculo,
    PautaMantencion,
    RegistroMantencion,
    ChecklistPreUso,
    ConfiguracionFlota,
    LogAlertaFlota,
)
from .forms import (
    VehiculoForm,
    DocumentoVehiculoForm,
    PautaMantencionForm,
    RegistroMantencionForm,
    ChecklistPreUsoForm,
    ConfiguracionFlotaForm,
)
from .services import verificar_y_enviar_alertas, enviar_correo_prueba_directo, alertar_documento_inmediato


# ==========================================
# 1. DASHBOARD DE FLOTA
# ==========================================
@operacional_required
def dashboard_flota(request):
    hoy = datetime.date.today()
    limite_30 = hoy + datetime.timedelta(days=30)
    limite_7 = hoy + datetime.timedelta(days=7)

    vehiculos = Vehiculo.objects.filter(activo=True).prefetch_related("fotos", "documentos", "mantenciones")
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

    for v in vehiculos:
        m = v.mantenciones.filter(Q(proximo_km__isnull=False) | Q(proxima_fecha__isnull=False)).first()
        if m and m.estado_alerta in ("VENCIDA", "POR_VENCER"):
            mantenciones_pendientes.append(m)

    # Últimos checklists pre-uso
    ultimos_checklists = ChecklistPreUso.objects.select_related("vehiculo").order_by("-fecha_hora")[:6]

    # Últimos vehículos (con foto portada precargada)
    ultimos_vehiculos = Vehiculo.objects.filter(activo=True).prefetch_related("fotos").order_by("-creado_el")[:6]

    context = {
        "vehiculos": vehiculos[:8],
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
        "ultimos_checklists": ultimos_checklists,
        "ultimos_vehiculos": ultimos_vehiculos,
        "config_flota": config,
        # Costos se mantienen en 0 (módulo desactivado en UI)
        "costo_total_mes": 0,
        "costo_combustible_mes": 0,
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

    vehiculos = Vehiculo.objects.all().prefetch_related("fotos", "documentos", "mantenciones")

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

            # Guardar múltiples fotos opcionales de varios ángulos
            fotos = request.FILES.getlist("fotos")
            for i, foto in enumerate(fotos):
                FotoVehiculo.objects.create(
                    vehiculo=vehiculo,
                    imagen=foto,
                    angulo="FRONTAL" if i == 0 else "GENERAL",
                    es_principal=(i == 0),
                )

            messages.success(
                request,
                f"Vehículo {vehiculo.patente} ({vehiculo.marca} {vehiculo.modelo}) registrado con {len(fotos)} fotografía(s).",
            )
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

            # Nuevas fotos si se subieron
            fotos = request.FILES.getlist("fotos")
            for foto in fotos:
                FotoVehiculo.objects.create(
                    vehiculo=vehiculo,
                    imagen=foto,
                    angulo="GENERAL",
                    es_principal=not vehiculo.fotos.exists(),
                )

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
        Vehiculo.objects.prefetch_related("fotos", "documentos", "mantenciones", "checklists"),
        pk=pk,
    )
    hoy = datetime.date.today()

    documentos = vehiculo.documentos.all().order_by("fecha_vencimiento")
    mantenciones = vehiculo.mantenciones.all().order_by("-fecha")
    checklists = vehiculo.checklists.all().order_by("-fecha_hora")[:20]
    fotos = vehiculo.fotos.all()

    context = {
        "vehiculo": vehiculo,
        "documentos": documentos,
        "mantenciones": mantenciones,
        "checklists": checklists,
        "fotos": fotos,
        "angulos": FotoVehiculo.ANGULO_CHOICES,
        "hoy": hoy,
    }
    return render(request, "flota/detalle_vehiculo.html", context)


# ==========================================
# 3. FOTOGRAFÍAS Y ÁNGULOS DEL VEHÍCULO
# ==========================================
@operacional_required
@audit_read_only
def subir_foto_vehiculo(request, vehiculo_id):
    vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_id)
    if request.method == "POST":
        fotos = request.FILES.getlist("fotos")
        angulo = request.POST.get("angulo", "GENERAL")
        descripcion = request.POST.get("descripcion", "").strip()

        count = 0
        for f in fotos:
            FotoVehiculo.objects.create(
                vehiculo=vehiculo,
                imagen=f,
                angulo=angulo,
                descripcion=descripcion,
                es_principal=not vehiculo.fotos.exists(),
            )
            count += 1

        if count > 0:
            messages.success(request, f"Se agregaron {count} fotografía(s) a la ficha de {vehiculo.patente}.")
        else:
            messages.warning(request, "No se seleccionó ninguna imagen.")

    return redirect("flota_detalle_vehiculo", pk=vehiculo.pk)


@operacional_required
@audit_read_only
def eliminar_foto_vehiculo(request, pk):
    foto = get_object_or_404(FotoVehiculo, pk=pk)
    vehiculo_pk = foto.vehiculo.pk
    if request.method == "POST":
        foto.delete()
        messages.success(request, "Fotografía eliminada de la galería.")
    return redirect("flota_detalle_vehiculo", pk=vehiculo_pk)


@operacional_required
@audit_read_only
def establecer_foto_principal(request, pk):
    foto = get_object_or_404(FotoVehiculo, pk=pk)
    vehiculo = foto.vehiculo
    vehiculo.fotos.update(es_principal=False)
    foto.es_principal = True
    foto.save(update_fields=["es_principal"])
    messages.success(request, f"Foto establecida como portada principal para {vehiculo.patente}.")
    return redirect("flota_detalle_vehiculo", pk=vehiculo.pk)


@operacional_required
@audit_read_only
def actualizar_km_rapido(request, pk):
    """Permite actualizar el odómetro directamente desde la ficha del móvil sin pasos extras."""
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    if request.method == "POST":
        try:
            nuevo_km = int(request.POST.get("kilometraje", "").replace(".", "").replace(",", "").strip())
            if nuevo_km >= 0:
                vehiculo.kilometraje_actual = nuevo_km
                vehiculo.fecha_actualizacion_km = datetime.date.today()
                vehiculo.save(update_fields=["kilometraje_actual", "fecha_actualizacion_km"])
                messages.success(request, f"Odómetro de {vehiculo.patente} actualizado a {nuevo_km:,} km.".replace(",", "."))
            else:
                messages.error(request, "El kilometraje no puede ser negativo.")
        except (ValueError, TypeError):
            messages.error(request, "Ingresa un número de kilometraje válido.")
    return redirect("flota_detalle_vehiculo", pk=vehiculo.pk)


# ==========================================
# 4. GESTIÓN DE DOCUMENTOS CON VENCIMIENTO
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
            # Alerta inmediata si el documento vence pronto (≤ 30 días) o ya venció
            try:
                alertar_documento_inmediato(doc)
            except Exception:
                pass  # No bloquear el guardado por errores de correo
            messages.success(
                request,
                f"Documento '{doc.titulo_completo}' registrado para {doc.vehiculo.patente}.",
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
            # Alerta inmediata si el documento vence pronto (≤ 30 días) o ya venció
            try:
                alertar_documento_inmediato(doc)
            except Exception:
                pass
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
# 5. GESTIÓN DE MANTENCIONES
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
# 6. CHECKLIST PRE-USO
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
                    f"⚠️ Checklist registrado: Vehículo {chk.vehiculo.patente} CON OBSERVACIONES. Requiere revisión.",
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
# 7. PAUTAS DE MANTENCIÓN
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
# 8. PANEL DE ALERTAS Y CONFIGURACIÓN DE CORREOS
# ==========================================
@operacional_required
def panel_alertas(request):
    hoy = datetime.date.today()
    config = ConfiguracionFlota.get_solo()

    docs = DocumentoVehiculo.objects.filter(vehiculo__activo=True).select_related("vehiculo").order_by("fecha_vencimiento")
    docs_vencidos = [d for d in docs if d.dias_restantes < 0]
    docs_urgentes_7 = [d for d in docs if 0 <= d.dias_restantes <= 7]
    docs_alerta_15 = [d for d in docs if 8 <= d.dias_restantes <= 15]
    docs_aviso_30 = [d for d in docs if 16 <= d.dias_restantes <= 30]

    mantenciones = RegistroMantencion.objects.filter(vehiculo__activo=True).select_related("vehiculo", "pauta")
    mant_vencidas = [m for m in mantenciones if m.estado_alerta == "VENCIDA"]
    mant_por_vencer = [m for m in mantenciones if m.estado_alerta == "POR_VENCER"]

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
            messages.success(request, "Configuración de alertas por correo guardada correctamente. Esta lista queda fija en el sistema.")
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
            messages.info(request, f"ℹ️ {motivo}")

    return redirect("flota_panel_alertas")


@operacional_required
@audit_read_only
def enviar_correo_prueba(request):
    """
    Envía un correo de prueba garantizado con formato completo para verificar SMTP.
    """
    if request.method == "POST":
        correo_test = request.POST.get("correo_prueba", "").strip()
        if not correo_test or "@" not in correo_test:
            messages.error(request, "Por favor indica un correo electrónico válido para la prueba.")
            return redirect("flota_configuracion_alertas")

        resultado = enviar_correo_prueba_directo(correo_test)
        if resultado.get("enviado"):
            messages.success(
                request,
                f"✅ ¡Correo de prueba enviado con éxito a '{correo_test}'! Revisa tu bandeja de entrada o spam para ver el diseño del reporte.",
            )
        else:
            err = resultado.get("error", "Error al conectar con el servidor de correo.")
            messages.error(request, f"❌ No se pudo enviar el correo de prueba: {err}")

    return redirect("flota_configuracion_alertas")
