from django.core.management.base import BaseCommand
from flota.services import verificar_y_enviar_alertas


class Command(BaseCommand):
    help = "Verifica los vencimientos de documentos y mantenciones de flota y envía alertas automáticas por correo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--forzar",
            action="store_true",
            help="Fuerza el envío ignorando filtros de duplicados del mismo día.",
        )
        parser.add_argument(
            "--email",
            type=str,
            default=None,
            help="Envía las alertas a un correo específico de prueba.",
        )

    def handle(self, *args, **options):
        forzar = options.get("forzar", False)
        email = options.get("email", None)

        self.stdout.write(self.style.NOTICE("🔍 Evaluando vencimientos y mantenciones de vehículos..."))

        resultado = verificar_y_enviar_alertas(forzar=forzar, correo_especifico=email)

        if resultado.get("enviado"):
            total = resultado.get("total_alertas", 0)
            dest = ", ".join(resultado.get("destinatarios", []))
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Alertas enviadas con éxito a {dest}. Total alertas procesadas: {total}."
                )
            )
        else:
            motivo = resultado.get("motivo") or resultado.get("error") or "Sin alertas para despachar."
            self.stdout.write(self.style.WARNING(f"ℹ️ {motivo}"))

