"""
Management command: import_inventario
Lee el Excel 'Planilla de invntario 28-02-26.xlsx' y carga todos los
Productos (y, si tienen stock, un Lote de stock inicial) en la BD.

Uso:
    python manage.py import_inventario
    python manage.py import_inventario --excel ruta/al/archivo.xlsx
    python manage.py import_inventario --dry-run   (solo muestra, no guarda)
"""

import datetime
import os

from django.core.management.base import BaseCommand

try:
    import openpyxl
except ImportError:
    openpyxl = None

from inventario.models import Lote, Producto

# ─── Mapeo CONCEPTO  →  categoria de Producto ─────────────────────────────────
MAPA_CATEGORIA = {
    # Abarrotes
    "abarrotes aceite": "ABARROTES",
    "abarrotes cafetería": "ABARROTES",
    "abarrotes cafeter": "ABARROTES",
    "abarrotes condimentos": "ABARROTES",
    "abarrotes conservas dulces": "ABARROTES",
    "abarrotes conservas saladas": "ABARROTES",
    "abarrotes farinaceos": "ABARROTES",
    "abarrotes jugos en polvos y concentrados": "ABARROTES",
    "abarrotes postres en polvo": "ABARROTES",
    "abarrotes repostería": "ABARROTES",
    "abarrotes reposter": "ABARROTES",
    "abarrotes sachet portion": "ABARROTES",
    "abarrotes sopas y cremas": "ABARROTES",
    # Carnes
    "carne pollo": "CARNES",
    "carne vacuno": "CARNES",
    "carne de cerdo": "CARNES",
    "carne de pavo": "CARNES",
    "cecinas": "CARNES",
    "embutidos": "CARNES",
    "hamburguesa": "CARNES",
    # Pescados
    "pescados y mariscos": "PESCADOS",
    # Lácteos
    "lácteos cremas": "LACTEOS",
    "lacteos cremas": "LACTEOS",
    "lácteos leches": "LACTEOS",
    "lacteos leches": "LACTEOS",
    "lácteos quesos": "LACTEOS",
    "lacteos quesos": "LACTEOS",
    "lácteos yogurt": "LACTEOS",
    "lacteos yogurt": "LACTEOS",
    "huevos": "LACTEOS",
    # Frutas/Verduras
    "frutas frescas": "FRUTAS",
    "verduras frescas": "FRUTAS",
    # Congelados
    "alim.congelados": "CONGELADOS",
    "helados y pulpas": "CONGELADOS",
    "croquetas": "CONGELADOS",
    # Bebidas
    "bebidas": "BEBIDAS",
    "agua con y sin sabor": "BEBIDAS",
    "agua en bidones": "BEBIDAS",
    "jugos líquidos": "BEBIDAS",
    "jugos liquidos": "BEBIDAS",
    "vino,licores y cerveza": "BEBIDAS",
    # Limpieza
    "aseo desinfección": "LIMPIEZA",
    "aseo desinfecci": "LIMPIEZA",
    "aseo general": "LIMPIEZA",
    # Panadería / Repostería  →  OTRO
    "pan elaborado": "OTRO",
    "pan y materias primas": "OTRO",
    "postres repostería": "OTRO",
    "postres reposter": "OTRO",
    "preparados": "OTRO",
    "confites dulces": "OTRO",
    "confites salados": "OTRO",
    "desechable cubiertos": "OTRO",
    "desechable general": "OTRO",
    "desechable contenedores": "OTRO",
    "desechable pocillos": "OTRO",
    "desechable vasos": "OTRO",
}


def _mapear_categoria(concepto: str) -> str:
    if not concepto:
        return "OTRO"
    key = concepto.strip().lower()
    # Busca exacto
    if key in MAPA_CATEGORIA:
        return MAPA_CATEGORIA[key]
    # Busca por prefijo (maneja tildes / encoding)
    for k, v in MAPA_CATEGORIA.items():
        if key.startswith(k) or k.startswith(key[:10]):
            return v
    return "OTRO"


# ─── Mapeo UM  →  unidad_medida ───────────────────────────────────────────────
MAPA_UNIDAD = {
    "KG": "KG",
    "LT": "L",
    "UND": "UN",
    "UNID": "UN",
    "UM": "UN",
    "G": "G",
    "ML": "ML",
    "CAJA": "CAJA",
}


def _mapear_unidad(um: str) -> str:
    if not um:
        return "UN"
    return MAPA_UNIDAD.get(str(um).strip().upper(), "UN")


class Command(BaseCommand):
    help = "Importa el inventario desde la planilla Excel"

    def add_arguments(self, parser):
        default_excel = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),  # commands/
            "..",
            "..",
            "..",
            "Planilla de invntario 28-02-26.xlsx",
        )
        parser.add_argument(
            "--excel",
            default=os.path.normpath(default_excel),
            help="Ruta al archivo Excel",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simula la importación sin guardar nada",
        )

    def handle(self, *args, **options):
        if openpyxl is None:
            self.stderr.write(self.style.ERROR("Falta openpyxl. Instálalo: pip install openpyxl"))
            return

        ruta = options["excel"]
        dry_run = options["dry_run"]

        if not os.path.exists(ruta):
            self.stderr.write(self.style.ERROR(f"Archivo no encontrado: {ruta}"))
            return

        self.stdout.write(self.style.MIGRATE_HEADING(f"\nLeyendo: {ruta}"))
        if dry_run:
            self.stdout.write(self.style.WARNING("[DRY-RUN] No se guardara nada\n"))

        wb = openpyxl.load_workbook(ruta, data_only=True)
        ws = wb.active

        # Contadores
        creados = 0
        actualizados = 0
        lotes_creados = 0
        sin_stock = 0
        errores = 0

        fecha_hoy = datetime.date.today()
        # Fecha de vencimiento por defecto para el stock inicial: 6 meses
        mes_vto = fecha_hoy.month + 6
        anio_vto = fecha_hoy.year + (1 if mes_vto > 12 else 0)
        mes_vto = mes_vto - 12 if mes_vto > 12 else mes_vto
        fecha_vto_default = fecha_hoy.replace(year=anio_vto, month=mes_vto)

        # Palabras que identifican cabeceras o subtotales (artículo sin SKU y sin concepto)
        SKIPWORDS = {"articulo", "art\u00edculo", "sku", "concepto", "resumen", "bebidas", "huevos",
                     "sachet"}

        concepto_actual = ""  # propagar concepto de la fila anterior cuando falta

        for fila_num, row in enumerate(ws.iter_rows(min_row=7, values_only=True), start=7):
            concepto, articulo, sku, um, stock, costo_unit, _, _, _, observacion = (
                row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]
            )

            # ── Saltear filas vacías ──────────────────────────────────────────
            if not articulo or str(articulo).strip() == "":
                continue

            articulo = str(articulo).strip()
            sku_raw = str(sku).strip() if sku else ""
            observacion = str(observacion).strip() if observacion else ""

            # ── Saltear subtotales / cabeceras repetidas ──────────────────────
            # Un subtotal/encabezado es una fila sin SKU Y sin concepto.
            # Excepción: algunos artículos reales tampoco tienen SKU (ej: frutas frescas).
            # El discriminante definitivo: si el artículo en minúsculas aparece en SKIPWORDS
            # o el valor de SKU es literalmente "None" / igual al nombre de una categoría.
            articulo_lower = articulo.lower().strip()
            if not sku_raw and not concepto:
                # Solo omitir si suena a cabecera/subtotal
                if (articulo_lower in SKIPWORDS
                        or len(articulo_lower) > 60           # resumen de bloque (string muy largo)
                        or sku_raw.lower() in ("none", "")):
                    # Es subtotal – actualiza el concepto para las siguientes filas
                    concepto_actual = articulo  # puede servir como categoría
                    continue

            # Actualizar concepto_actual cuando viene definido en la fila
            if concepto:
                concepto_actual = str(concepto).strip()

            try:
                categoria = _mapear_categoria(concepto_actual)
                unidad = _mapear_unidad(str(um) if um else "")

                # ── Crear o actualizar Producto ──────────────────────────────
                descripcion = f"SKU: {sku_raw}" if sku_raw else ""
                if not dry_run:
                    producto, nuevo = Producto.objects.update_or_create(
                        nombre=articulo,
                        defaults={
                            "descripcion": descripcion,
                            "categoria": categoria,
                            "unidad_medida": unidad,
                            "stock_minimo": 0,
                        },
                    )
                else:
                    nuevo = True  # simulado

                if nuevo:
                    creados += 1
                else:
                    actualizados += 1

                # ── Crear Lote de stock inicial si hay cantidad ──────────────
                try:
                    cantidad = float(stock) if stock is not None else 0
                except (ValueError, TypeError):
                    cantidad = 0

                try:
                    precio = float(costo_unit) if costo_unit is not None else 0
                except (ValueError, TypeError):
                    precio = 0

                if cantidad > 0:
                    if not dry_run:
                        ya_existe = Lote.objects.filter(
                            producto=producto,
                            numero_lote_proveedor=sku_raw,
                            estado="ACTIVO",
                        ).exists()
                        if not ya_existe:
                            numero_lote = f"{sku_raw}-INICIAL" if sku_raw else ""
                            lote = Lote(
                                producto=producto,
                                numero_lote=numero_lote,
                                numero_lote_proveedor=sku_raw,
                                cantidad=cantidad,
                                precio_unitario=precio,
                                fecha_recepcion=fecha_hoy,
                                fecha_vencimiento=fecha_vto_default,
                                estado="ACTIVO",
                                ubicacion_actual="BODEGA",
                                observaciones=observacion,
                                responsable_registro="Importacion Excel",
                                proceso="RECEPCION",
                            )
                            lote.save()
                            lotes_creados += 1
                    else:
                        lotes_creados += 1
                else:
                    sin_stock += 1

            except Exception as exc:
                errores += 1
                self.stderr.write(
                    self.style.ERROR(f"  Fila {fila_num}: Error en '{articulo}' -> {exc}")
                )

        # ── Resumen final ────────────────────────────────────────────────────
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"[OK] Productos creados:      {creados}"))
        self.stdout.write(self.style.SUCCESS(f"[OK] Productos actualizados: {actualizados}"))
        self.stdout.write(self.style.SUCCESS(f"[OK] Lotes de stock creados: {lotes_creados}"))
        self.stdout.write(self.style.WARNING(f"[--] Productos sin stock:    {sin_stock}"))
        if errores:
            self.stdout.write(self.style.ERROR(f"[!!] Errores:                {errores}"))
        self.stdout.write("")
        if dry_run:
            self.stdout.write(self.style.WARNING("(Nada fue guardado - modo dry-run)\n"))
        else:
            self.stdout.write(self.style.MIGRATE_HEADING("Importacion completada!\n"))
