import datetime
import logging
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.conf import settings
from .models import (
    Vehiculo,
    DocumentoVehiculo,
    RegistroMantencion,
    ConfiguracionFlota,
    LogAlertaFlota,
)

logger = logging.getLogger(__name__)


def enviar_correo_prueba_directo(correo_destino):
    """
    Envía un correo de prueba garantizado a la dirección especificada para validar
    que la conexión SMTP de PythonAnywhere o del servidor funciona correctamente.
    """
    asunto = "✅ [COALFA] Prueba Exitosa de Alertas de Flota"

    texto_plano = (
        "PRUEBA DE NOTIFICACIÓN DE FLOTA - COALFA\n"
        "=======================================\n\n"
        f"¡Hola! Este es un correo de prueba enviado exitosamente a {correo_destino}.\n\n"
        "El sistema de alertas automáticas de COALFA está configurado correctamente.\n"
        "A partir de ahora, cuando existan documentos o mantenciones por vencer (a 30, 15, 7 días o vencidos),\n"
        "recibirás un aviso consolidado similar a este.\n\n"
        "Ejemplo de lo que recibirás cuando venza un documento:\n"
        "- Patente ABCD12 (Toyota Hilux 4x4 - Faena):\n"
        "  * Revisión Técnica: Vence en 7 días\n"
        "  * SOAP: Vence en 15 días\n\n"
        "Fecha de prueba: " + timezone.now().strftime("%d/%m/%Y %H:%M") + "\n"
        "COALFA - Gestión Operacional y Flota\n"
    )

    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head><meta charset="utf-8"></head>
    <body style="margin: 0; padding: 24px 0; background-color: #0b1120; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
        <div style="max-width: 640px; margin: 0 auto; background: #11192d; border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 8px 30px rgba(0,0,0,0.5);">
            
            <!-- Cabecera -->
            <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 28px 32px; border-bottom: 3px solid #34d399;">
                <div style="font-size: 24px; font-weight: 800; color: #f97316; letter-spacing: -0.5px;">COALFA</div>
                <div style="font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 2px;">
                    Control de Flota &bull; Validación de Conexión
                </div>
            </div>

            <!-- Cuerpo -->
            <div style="padding: 32px;">
                <div style="background: rgba(52, 211, 153, 0.1); border: 1px solid rgba(52, 211, 153, 0.3); border-radius: 8px; padding: 14px 18px; margin-bottom: 24px; color: #34d399; font-weight: 600; font-size: 14px;">
                    ✅ ¡La conexión de correo funciona perfectamente!
                </div>

                <p style="font-size: 15px; color: #e2e8f0; line-height: 1.6; margin-top: 0;">
                    Este es un <strong>correo de prueba</strong> solicitado desde la configuración de alertas de Flota para <strong>{correo_destino}</strong>.
                </p>

                <p style="font-size: 14px; color: #94a3b8; line-height: 1.5;">
                    A continuación se muestra una previsualización de cómo se estructuran las alertas reales cuando un vehículo tiene documentos o mantenciones por vencer:
                </p>

                <!-- Ejemplo de Alerta Simulado -->
                <div style="margin-top: 20px; background: #0f172a; border-radius: 8px; overflow: hidden; border: 1px solid #334155;">
                    <div style="background: #1e293b; padding: 10px 16px; font-size: 11px; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.5px; font-weight: 700;">
                        Ejemplo de Alerta Preventiva
                    </div>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr style="border-bottom: 1px solid #334155;">
                            <td style="padding: 12px 16px; color: #f8fafc; font-size: 14px;">
                                <span style="background: #1e293b; padding: 3px 8px; border-radius: 4px; border: 1px solid #475569; font-weight: 700;">
                                    ABCD12
                                </span>
                                <div style="font-size: 11px; color: #94a3b8; margin-top: 4px;">Toyota Hilux 4x4 (Faena)</div>
                            </td>
                            <td style="padding: 12px 16px; color: #f1f5f9; font-size: 13px;">
                                <strong>Revisión Técnica</strong>
                                <div style="font-size: 11px; color: #94a3b8;">Vence: En 7 días</div>
                            </td>
                            <td style="padding: 12px 16px; text-align: right;">
                                <span style="display: inline-block; padding: 4px 10px; border-radius: 9999px; font-size: 11px; font-weight: 700; color: #ffffff; background-color: #f97316;">
                                    Urgente (7 Días)
                                </span>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 12px 16px; color: #f8fafc; font-size: 14px;">
                                <span style="background: #1e293b; padding: 3px 8px; border-radius: 4px; border: 1px solid #475569; font-weight: 700;">
                                    ABCD12
                                </span>
                                <div style="font-size: 11px; color: #94a3b8; margin-top: 4px;">Toyota Hilux 4x4 (Faena)</div>
                            </td>
                            <td style="padding: 12px 16px; color: #f1f5f9; font-size: 13px;">
                                <strong>Cambio de Aceite 10.000 Km</strong>
                                <div style="font-size: 11px; color: #94a3b8;">Faltan 450 km</div>
                            </td>
                            <td style="padding: 12px 16px; text-align: right;">
                                <span style="display: inline-block; padding: 4px 10px; border-radius: 9999px; font-size: 11px; font-weight: 700; color: #ffffff; background-color: #fbbf24;">
                                    Por Vencer
                                </span>
                            </td>
                        </tr>
                    </table>
                </div>

                <div style="margin-top: 32px; text-align: center;">
                    <a href="https://coalfa.pythonanywhere.com/flota/alertas/" 
                       style="display: inline-block; background-color: #f97316; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 8px; font-weight: 700; font-size: 13px;">
                        🚗 Abrir Módulo de Flota
                    </a>
                </div>
            </div>

            <!-- Pie -->
            <div style="background: #0f172a; padding: 16px 32px; text-align: center; border-top: 1px solid rgba(255,255,255,0.06); font-size: 11px; color: #64748b;">
                Fecha de prueba: {timezone.now().strftime('%d/%m/%Y %H:%M')} (Hora de Chile)
            </div>
        </div>
    </body>
    </html>
    """

    try:
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "alertas-flota@coalfa.cl")
        msg = EmailMultiAlternatives(
            subject=asunto,
            body=texto_plano,
            from_email=from_email,
            to=[correo_destino],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        # Registrar log
        LogAlertaFlota.objects.create(
            tipo="PRUEBA",
            etapa="TEST",
            destinatarios=correo_destino,
            resumen_items="Correo de prueba enviado satisfactoriamente",
            exitoso=True,
        )
        return {"enviado": True}
    except Exception as e:
        err_msg = str(e)
        logger.error(f"[Flota] Error en prueba de correo: {err_msg}", exc_info=True)
        LogAlertaFlota.objects.create(
            tipo="PRUEBA",
            etapa="TEST",
            destinatarios=correo_destino,
            resumen_items="Fallo al enviar correo de prueba",
            exitoso=False,
            error_mensaje=err_msg,
        )
        return {"enviado": False, "error": err_msg}


def verificar_y_enviar_alertas(forzar=False, correo_especifico=None):
    """
    Evalúa vencimientos de documentos y kilometraje/fechas de mantención para todos los vehículos activos.
    Agrupa los avisos y envía un correo consolidado para evitar spam, controlando duplicados.
    """
    config = ConfiguracionFlota.get_solo()
    if not config.activo and not forzar:
        return {
            "enviado": False,
            "motivo": "El envío automático de alertas de flota está desactivado en la configuración.",
            "total_alertas": 0,
        }

    destinatarios = [correo_especifico] if correo_especifico else config.get_lista_correos()
    if not destinatarios:
        return {
            "enviado": False,
            "motivo": "No hay correos destinatarios configurados en la lista.",
            "total_alertas": 0,
        }

    hoy = datetime.date.today()
    alertas_documentos = []
    alertas_mantenciones = []
    logs_a_guardar = []

    vehiculos = Vehiculo.objects.filter(activo=True).prefetch_related("documentos", "mantenciones")

    for v in vehiculos:
        # 1. EVALUAR DOCUMENTOS
        for doc in v.documentos.all():
            dias = (doc.fecha_vencimiento - hoy).days
            etapa = None
            motivo = ""
            color = "#f87171"

            if dias < 0 and config.alertar_vencidos:
                etapa = "VENCIDO"
                motivo = f"VENCIDO hace {abs(dias)} día(s)"
                color = "#ef4444"
            elif 0 <= dias <= 7 and config.alertar_7_dias:
                etapa = "7_DIAS"
                motivo = f"Urgente: vence en {dias} día(s)"
                color = "#f97316"
            elif 8 <= dias <= 15 and config.alertar_15_dias:
                etapa = "15_DIAS"
                motivo = f"Atención: vence en {dias} días"
                color = "#fbbf24"
            elif 16 <= dias <= 30 and config.alertar_30_dias:
                etapa = "30_DIAS"
                motivo = f"Aviso preventivo: vence en {dias} días"
                color = "#38bdf8"

            if etapa:
                ya_enviado = False
                if not forzar:
                    if etapa == "VENCIDO":
                        ya_enviado = LogAlertaFlota.objects.filter(
                            vehiculo=v,
                            tipo="DOCUMENTO",
                            referencia_id=str(doc.id),
                            etapa="VENCIDO",
                            fecha_envio__date=hoy,
                            exitoso=True,
                        ).exists()
                    else:
                        ya_enviado = LogAlertaFlota.objects.filter(
                            vehiculo=v,
                            tipo="DOCUMENTO",
                            referencia_id=str(doc.id),
                            etapa=etapa,
                            exitoso=True,
                        ).exists()

                if not ya_enviado or forzar:
                    item_data = {
                        "vehiculo": v,
                        "tipo": "DOCUMENTO",
                        "documento": doc,
                        "titulo": doc.titulo_completo,
                        "fecha": doc.fecha_vencimiento.strftime("%d/%m/%Y"),
                        "dias": dias,
                        "etapa": etapa,
                        "motivo": motivo,
                        "color": color,
                    }
                    alertas_documentos.append(item_data)
                    logs_a_guardar.append(
                        LogAlertaFlota(
                            vehiculo=v,
                            tipo="DOCUMENTO",
                            referencia_id=str(doc.id),
                            etapa=etapa,
                            destinatarios=", ".join(destinatarios),
                            resumen_items=f"{doc.titulo_completo} ({motivo})",
                        )
                    )

        # 2. EVALUAR MANTENCIONES
        if config.alertar_km:
            mantenciones_recientes = v.mantenciones.all()[:5]
            for m in mantenciones_recientes:
                km_restantes = m.km_restantes
                dias_fecha = m.dias_restantes_fecha

                motivo_m = ""
                etapa_m = None
                color_m = "#f87171"

                if km_restantes is not None:
                    if km_restantes <= 0:
                        etapa_m = "MANTENCION_VENCIDA_KM"
                        motivo_m = f"¡Kilometraje superado! Excedido por {abs(km_restantes):,} km".replace(",", ".")
                        color_m = "#ef4444"
                    elif km_restantes <= config.km_anticipacion_alerta:
                        etapa_m = "MANTENCION_POR_VENCER_KM"
                        motivo_m = f"Faltan solo {km_restantes:,} km para la mantención".replace(",", ".")
                        color_m = "#f97316"

                if not etapa_m and dias_fecha is not None:
                    if dias_fecha <= 0:
                        etapa_m = "MANTENCION_VENCIDA_FECHA"
                        motivo_m = f"Mantención vencida por fecha hace {abs(dias_fecha)} días"
                        color_m = "#ef4444"
                    elif dias_fecha <= 15:
                        etapa_m = "MANTENCION_POR_VENCER_FECHA"
                        motivo_m = f"Mantención programada en {dias_fecha} días"
                        color_m = "#fbbf24"

                if etapa_m:
                    ya_enviado_m = False
                    if not forzar:
                        ya_enviado_m = LogAlertaFlota.objects.filter(
                            vehiculo=v,
                            tipo="MANTENCION",
                            referencia_id=str(m.id),
                            etapa=etapa_m,
                            fecha_envio__date=hoy,
                            exitoso=True,
                        ).exists()

                    if not ya_enviado_m or forzar:
                        item_m = {
                            "vehiculo": v,
                            "tipo": "MANTENCION",
                            "mantencion": m,
                            "titulo": m.titulo,
                            "fecha": m.proxima_fecha.strftime("%d/%m/%Y") if m.proxima_fecha else "Por Km",
                            "km_objetivo": f"{m.proximo_km:,} km".replace(",", ".") if m.proximo_km else "N/A",
                            "km_actual": f"{v.kilometraje_actual:,} km".replace(",", "."),
                            "motivo": motivo_m,
                            "color": color_m,
                        }
                        alertas_mantenciones.append(item_m)
                        logs_a_guardar.append(
                            LogAlertaFlota(
                                vehiculo=v,
                                tipo="MANTENCION",
                                referencia_id=str(m.id),
                                etapa=etapa_m,
                                destinatarios=", ".join(destinatarios),
                                resumen_items=f"{m.titulo} ({motivo_m})",
                            )
                        )

    total_alertas = len(alertas_documentos) + len(alertas_mantenciones)

    if total_alertas == 0:
        return {
            "enviado": False,
            "motivo": "No se encontraron vencimientos ni mantenciones que requieran notificación en este momento. Toda la flota está al día.",
            "total_alertas": 0,
        }

    asunto = config.asunto_alerta or "[COALFA] Alerta de Flota y Vehículos"
    cuerpo_texto = _construir_texto_plano(alertas_documentos, alertas_mantenciones)
    cuerpo_html = _construir_html_alerta(alertas_documentos, alertas_mantenciones)

    exito = True
    error_str = ""

    try:
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "alertas-flota@coalfa.cl")
        msg = EmailMultiAlternatives(
            subject=asunto,
            body=cuerpo_texto,
            from_email=from_email,
            to=destinatarios,
        )
        msg.attach_alternative(cuerpo_html, "text/html")
        msg.send(fail_silently=False)

        config.ultimo_envio = timezone.now()
        config.save(update_fields=["ultimo_envio"])

    except Exception as e:
        exito = False
        error_str = str(e)
        logger.error(f"[Flota] Error al enviar correo de alerta: {error_str}", exc_info=True)

    for log in logs_a_guardar:
        log.exitoso = exito
        log.error_mensaje = error_str
        log.save()

    return {
        "enviado": exito,
        "total_alertas": total_alertas,
        "docs_count": len(alertas_documentos),
        "mantenciones_count": len(alertas_mantenciones),
        "destinatarios": destinatarios,
        "error": error_str,
    }


def _construir_texto_plano(documentos, mantenciones):
    lineas = [
        "ALERTA AUTOMÁTICA DE FLOTA Y VEHÍCULOS - COALFA",
        "================================================",
        "",
        "Se han detectado vencimientos y requerimientos de mantención que requieren atención:",
        "",
    ]

    if documentos:
        lineas.append("DOCUMENTOS CON VENCIMIENTO:")
        lineas.append("----------------------------")
        for d in documentos:
            lineas.append(
                f"- Patente {d['vehiculo'].patente} ({d['vehiculo'].marca} {d['vehiculo'].modelo} - {d['vehiculo'].get_asignacion_display()}):"
            )
            lineas.append(f"  * Documento: {d['titulo']}")
            lineas.append(f"  * Estado: {d['motivo']}")
            lineas.append(f"  * Fecha de vencimiento: {d['fecha']}")
            lineas.append("")

    if mantenciones:
        lineas.append("MANTENCIONES PROGRAMADAS / PENDIENTES:")
        lineas.append("---------------------------------------")
        for m in mantenciones:
            lineas.append(
                f"- Patente {m['vehiculo'].patente} ({m['vehiculo'].marca} {m['vehiculo'].modelo} - {m['vehiculo'].get_asignacion_display()}):"
            )
            lineas.append(f"  * Servicio: {m['titulo']}")
            lineas.append(f"  * Estado: {m['motivo']}")
            lineas.append(f"  * Km Actual: {m['km_actual']} | Km Programado: {m['km_objetivo']}")
            lineas.append("")

    lineas.append("Por favor ingresa al sistema para gestionar la documentación o registrar el mantenimiento.")
    lineas.append("COALFA Gestión Operacional")
    return "\n".join(lineas)


def _construir_html_alerta(documentos, mantenciones):
    total = len(documentos) + len(mantenciones)

    html_docs = ""
    for d in documentos:
        html_docs += f"""
        <tr style="border-bottom: 1px solid #334155;">
            <td style="padding: 12px 16px; font-weight: 700; color: #f8fafc; font-family: sans-serif;">
                <span style="background: #1e293b; padding: 4px 8px; border-radius: 6px; border: 1px solid #475569; letter-spacing: 0.5px;">
                    {d['vehiculo'].patente}
                </span>
                <div style="font-size: 11px; color: #94a3b8; font-weight: 400; margin-top: 4px;">
                    {d['vehiculo'].marca} {d['vehiculo'].modelo} ({d['vehiculo'].get_asignacion_display()})
                </div>
            </td>
            <td style="padding: 12px 16px; color: #f1f5f9; font-family: sans-serif; font-size: 14px;">
                <strong>{d['titulo']}</strong>
                <div style="font-size: 12px; color: #94a3b8;">Vence: {d['fecha']}</div>
            </td>
            <td style="padding: 12px 16px; text-align: right; font-family: sans-serif;">
                <span style="display: inline-block; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 700; color: #ffffff; background-color: {d['color']};">
                    {d['motivo']}
                </span>
            </td>
        </tr>
        """

    html_mant = ""
    for m in mantenciones:
        html_mant += f"""
        <tr style="border-bottom: 1px solid #334155;">
            <td style="padding: 12px 16px; font-weight: 700; color: #f8fafc; font-family: sans-serif;">
                <span style="background: #1e293b; padding: 4px 8px; border-radius: 6px; border: 1px solid #475569; letter-spacing: 0.5px;">
                    {m['vehiculo'].patente}
                </span>
                <div style="font-size: 11px; color: #94a3b8; font-weight: 400; margin-top: 4px;">
                    {m['vehiculo'].marca} {m['vehiculo'].modelo} ({m['vehiculo'].get_asignacion_display()})
                </div>
            </td>
            <td style="padding: 12px 16px; color: #f1f5f9; font-family: sans-serif; font-size: 14px;">
                <strong>{m['titulo']}</strong>
                <div style="font-size: 12px; color: #94a3b8;">Km Actual: {m['km_actual']} &bull; Km Objetivo: {m['km_objetivo']}</div>
            </td>
            <td style="padding: 12px 16px; text-align: right; font-family: sans-serif;">
                <span style="display: inline-block; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 700; color: #ffffff; background-color: {m['color']};">
                    {m['motivo']}
                </span>
            </td>
        </tr>
        """

    seccion_docs = ""
    if documentos:
        seccion_docs = f"""
        <div style="margin-bottom: 24px;">
            <h3 style="color: #f97316; font-size: 15px; margin: 0 0 12px; font-family: sans-serif; text-transform: uppercase; letter-spacing: 0.5px;">
                📄 Documentos con Vencimiento ({len(documentos)})
            </h3>
            <table style="width: 100%; border-collapse: collapse; background: #0f172a; border-radius: 8px; overflow: hidden; border: 1px solid #334155;">
                <thead>
                    <tr style="background: #1e293b; text-align: left; font-size: 11px; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.5px;">
                        <th style="padding: 10px 16px;">Vehículo</th>
                        <th style="padding: 10px 16px;">Documento</th>
                        <th style="padding: 10px 16px; text-align: right;">Estado</th>
                    </tr>
                </thead>
                <tbody>
                    {html_docs}
                </tbody>
            </table>
        </div>
        """

    seccion_mant = ""
    if mantenciones:
        seccion_mant = f"""
        <div style="margin-bottom: 24px;">
            <h3 style="color: #f97316; font-size: 15px; margin: 0 0 12px; font-family: sans-serif; text-transform: uppercase; letter-spacing: 0.5px;">
                🔧 Mantenciones y Servicios ({len(mantenciones)})
            </h3>
            <table style="width: 100%; border-collapse: collapse; background: #0f172a; border-radius: 8px; overflow: hidden; border: 1px solid #334155;">
                <thead>
                    <tr style="background: #1e293b; text-align: left; font-size: 11px; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.5px;">
                        <th style="padding: 10px 16px;">Vehículo</th>
                        <th style="padding: 10px 16px;">Mantención</th>
                        <th style="padding: 10px 16px; text-align: right;">Estado</th>
                    </tr>
                </thead>
                <tbody>
                    {html_mant}
                </tbody>
            </table>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
    </head>
    <body style="margin: 0; padding: 24px 0; background-color: #0b1120; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
        <div style="max-width: 680px; margin: 0 auto; background: #11192d; border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 8px 30px rgba(0,0,0,0.5);">
            
            <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 28px 32px; border-bottom: 3px solid #f97316;">
                <div style="font-size: 24px; font-weight: 800; color: #f97316; letter-spacing: -0.5px;">COALFA</div>
                <div style="font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 2px;">Gestión de Flota &bull; Alertas de Vencimiento</div>
            </div>

            <div style="padding: 32px;">
                <p style="font-size: 15px; color: #e2e8f0; line-height: 1.6; margin-top: 0;">
                    Estimado equipo, se han detectado <strong>{total} alerta(s)</strong> que requieren atención para mantener los vehículos de la empresa operativos y en regla con la normativa chilena:
                </p>

                {seccion_docs}
                {seccion_mant}

                <div style="margin-top: 32px; text-align: center;">
                    <a href="https://coalfa.pythonanywhere.com/flota/alertas/" 
                       style="display: inline-block; background-color: #f97316; color: #ffffff; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-weight: 700; font-size: 14px; box-shadow: 0 4px 14px rgba(249, 115, 22, 0.4);">
                        🚗 Ir al Módulo de Flota en el Sistema
                    </a>
                </div>
            </div>

            <div style="background: #0f172a; padding: 20px 32px; text-align: center; border-top: 1px solid rgba(255,255,255,0.06); font-size: 11px; color: #64748b;">
                Este correo fue generado automáticamente por el sistema de Control de Flota COALFA.<br>
                Fecha de emisión: {timezone.now().strftime('%d/%m/%Y %H:%M')} (Hora de Chile)
            </div>
        </div>
    </body>
    </html>
    """
