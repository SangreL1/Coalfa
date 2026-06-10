import os
import sys
import django
from django.db import transaction
import datetime

# Setup Django
BASE_DIR = r'C:\Users\Coalfa\Desktop\RRHHBG\Gestios_Citas_IS'
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'san_lucas.settings') 
django.setup()

from inventario.models import Producto, Lote, Proveedor

def reprocess_invoices():
    with transaction.atomic():
        # 1. Cleanup lotes added in the previous run
        deleted, _ = Lote.objects.filter(responsable_registro='Carga Automatizada AI').delete()
        print(f"Deleted {deleted} previous lotes.")

        # 2. Helper to map categories
        def get_category(name):
            n = name.upper()
            if any(x in n for x in ['ACEITE', 'ARROZ', 'AZUCAR', 'SALSA', 'TE ', 'CALDO', 'MERMELADA', 'TE SURTIDAS', 'CREMA VEG', 'MAYONESA', 'MOSTAZA', 'TOMATE', 'KETCHUP', 'CHOCOLATE', 'COCO', 'SEMOLA', 'JALEA', 'BAVARAIS', 'MERENGUE', 'CAPPUCCINO', 'CREMA DE']):
                return 'ABARROTES'
            if any(x in n for x in ['POLLO', 'VACUNO', 'CERDO', 'PAVO', 'CARNE', 'HAMBURGUESA', 'CECINAS', 'CHURRASCO', 'HIGADO', 'SALAME', 'PRIETA']):
                return 'CARNES'
            if any(x in n for x in ['PESCADO', 'MARISCO', 'PANGASIUS']):
                return 'PESCADOS'
            if any(x in n for x in ['FRUTA', 'VERDURA', 'SANDIA', 'UVA', 'MANZANA', 'PLATANO', 'NARANJA']):
                return 'FRUTAS'
            if any(x in n for x in ['BEBIDA', 'AGUA', 'JUGO', 'REFRESCO', 'VINO', 'LICOR']):
                return 'BEBIDAS'
            if any(x in n for x in ['CONGELADO', 'PAPAS PREFRITAS', 'PAPA DUQUESA', 'HELADO', 'PULPA FRUTA']):
                return 'CONGELADOS'
            if any(x in n for x in ['ASEO', 'LIMPIEZA', 'LAVALOZA', 'DESINFEC', 'FIBRA', 'PAÑO', 'GUANTE', 'ESCOBILLON', 'ESPONJA', 'BOLSA DE BASURA', 'MOPA', 'ROCIADOR', 'BARRE AGUA']):
                return 'LIMPIEZA'
            return 'OTRO'

        # 3. Suppliers
        confical, _ = Proveedor.objects.get_or_create(rut='76.748.381-3', defaults={'nombre': 'Distribuidora y Comercializadora Ignacio Carvajal Castro E.I.R.L.'})
        macrofood, _ = Proveedor.objects.get_or_create(rut='96.733.580-0', defaults={'nombre': 'MACRO FOOD SPA.'})
        cial, _ = Proveedor.objects.get_or_create(rut='80.186.300-0', defaults={'nombre': 'CONSORCIO INDUSTRIAL DE ALIMENTOS S.A.'})
        casnorte, _ = Proveedor.objects.get_or_create(rut='76.286.101-1', defaults={'nombre': 'COMERCIALIZADORA ASESORIAS Y SERVICIOS DEL NORTE LIMITADA'})
        icb, _ = Proveedor.objects.get_or_create(rut='77.965.620-9', defaults={'nombre': 'ICB FOOD SERVICE SPA'})
        nevada, _ = Proveedor.objects.get_or_create(rut='77.851.255-6', defaults={'nombre': 'NEVADA PREMIUM SPA'})
        nora, _ = Proveedor.objects.get_or_create(rut='6.308.725-4', defaults={'nombre': 'NORA BERTA CACERES PEREZ'})

        # factor to adjust Neto to Total (approx 1.19 + extras)
        macro_factor = 1.2076 
        confical_factor = 1.19
        general_factor = 1.19

        receipts = [
            # CONFICAL (Factura 247236)
            (confical, "247236", datetime.date(2026, 4, 2), [
                ("SELZ MINI JAMON BS 1X40X35 LEY", 600, "UN", 231 * confical_factor),
                ("SELZ MINI QUESO BS 1X40X35 LEY", 600, "UN", 231 * confical_factor),
                ("NIKOLO TRAD. 12X20X24G 2024", 120, "UN", 4938 * confical_factor),
                ("GOLPE 4X30X27G", 40, "UN", 6845 * confical_factor),
            ]),
            # MACRO FOOD (Factura 1115778)
            (macrofood, "1115778", datetime.date(2026, 4, 2), [
                ("Refresco 33 Caribeño Pera", 10, "KG", 3147 * macro_factor),
                ("Refresco 33 Caribeño Naranja", 10, "KG", 3147 * macro_factor),
                ("Refresco 33 Caribeño Frutilla", 20, "KG", 3147 * macro_factor),
                ("Refresco 33 Caribeño Melon Tuna", 10, "KG", 3147 * macro_factor),
                ("Merengue", 10, "KG", 3297 * macro_factor),
                ("Cappuccino Premium", 20, "KG", 7494 * macro_factor),
                ("Sopa De Carne Con Arroz Premium", 10, "KG", 2796 * macro_factor),
                ("Semola Con Leche", 10, "KG", 2762 * macro_factor),
                ("Bavarais Limon", 10, "KG", 4957 * macro_factor),
                ("Jalea 15 Manzana", 10, "KG", 4324 * macro_factor),
                ("Jalea 15 Piña", 10, "KG", 4324 * macro_factor),
                ("Leche Asada (Comercial)", 10, "KG", 2945 * macro_factor),
                ("Salsa de Caramelo Premium c/logo", 10, "KG", 3435 * macro_factor),
                ("Crema De Esparragos Premium", 10, "KG", 2588 * macro_factor),
                ("Crema De Choclo Premium", 10, "KG", 2588 * macro_factor),
                ("Crema De Pollo Premium", 10, "KG", 2588 * macro_factor),
                ("Crema De Verduras Premium", 10, "KG", 2654 * macro_factor),
                ("Sopa De Carne Con Fideos Premium", 10, "KG", 2792 * macro_factor),
                ("Mermelada de Frutilla (1 K)", 20, "KG", 3299 * macro_factor),
                ("Mermelada de Mora (1 K)", 10, "KG", 3299 * macro_factor),
                ("Mermelada de Guinda (1 K)", 10, "KG", 3299 * macro_factor),
                ("Mermelada de Durazno (1 K)", 10, "KG", 3299 * macro_factor),
            ]),
            # MACRO FOOD (OC 12119) - Including extra items not in 1115778
            (macrofood, "OC12119", datetime.date(2026, 4, 1), [
                ("Refresco 33 Caribeño Saborizante Frutilla", 10, "KG", 3147 * macro_factor),
                ("Sopa De Carne Con Verduras Premium", 10, "KG", 2792 * macro_factor),
            ]),
            # ICB (OC 12118) - Extra items
            (icb, "OC12118", datetime.date(2026, 4, 1), [
                ("CHURRASCO VACUNO FLOW PACK 120 g (OC)", 15.6, "KG", 19850 * general_factor / 6), # Adjusting to match OC value approx
                ("HIGADO VACUNO (OC)", 5, "KG", 3270 * general_factor),
            ]),
            # CASNORTE (Guia 3209)
            (casnorte, "G3209", datetime.date(2026, 4, 1), [
                ("FIBRA ABRASIVA ULTRA PESADA", 100, "UN", 960 * general_factor),
                ("PAÑO MULTIUSO ROLLO X20 CLASICA", 30, "UN", 5797 * general_factor),
                ("GUANTE CONVENIENTE TALLA S", 12, "UN", 2178 * general_factor),
                ("GUANTE CONVENIENTE TALLA M", 20, "UN", 2178 * general_factor),
                ("GUANTE CONVENIENTE TALLA L", 12, "UN", 2178 * general_factor),
                ("ESCOBILLON ECONOMICO 100% RECICLADO", 20, "UN", 3012 * general_factor),
                ("ESPONJA LISA VTX PRO", 60, "UN", 312 * general_factor),
                ("BOLSAS DE BASURA BIOROLLO 70X90", 20, "UN", 1125 * general_factor),
                ("REPUESTO MOPA HUMEDA ALGODON 24 OZ", 20, "UN", 5019 * general_factor),
                ("BOLSAS DE BASURA BIOROLLO 50X70", 20, "UN", 614 * general_factor),
                ("BARRE AGUA 55 CMS - VTX PRO", 10, "UN", 9220 * general_factor),
                ("ROCIADOR 1000 CC", 10, "UN", 3120 * general_factor),
            ]),
            # CIAL (Factura 49491260)
            (cial, "49491260", datetime.date(2026, 3, 31), [
                ("SALAME PIEZA 1KG LP", 15, "KG", 7692 * general_factor),
                ("PRIETA 10x400 GR LP", 12, "CJ", 5656 * general_factor),
            ]),
            # ICB (Factura 5522527)
            (icb, "5522527", datetime.date(2026, 4, 2), [
                ("ACEITE VEGETAL 5 L", 20, "UN", 8713 * general_factor),
            ]),
            # ICB (Factura 5522528)
            (icb, "5522528", datetime.date(2026, 4, 2), [
                ("CHURRASCO VACUNO FLOW PACK 120 g", 30, "UN", 19850 * general_factor),
                ("HIGADO VACUNO", 25.94, "KG", 3270 * general_factor),
            ]),
            # ICB (Factura 5524698)
            (icb, "5524698", datetime.date(2026, 4, 2), [
                ("PANGASIUS FILETE S/P 1KG 170-220G", 10, "CJ", 28000 * general_factor),
            ]),
            # NEVADA (Factura 684)
            (nevada, "684", datetime.date(2026, 4, 2), [
                ("AGUA EN BIDON DE 20 LT", 40, "UN", 1300 * general_factor),
            ]),
            # NORA CACERES (Factura 9721)
            (nora, "9721", datetime.date(2026, 4, 2), [
                ("KILOS DE SANDIA", 29.6, "KG", 672.26 * general_factor),
                ("CAJA DE UVA", 1, "CJ", 25210.08 * general_factor),
                ("CAJA DE MANZANA", 5, "CJ", 27731.09 * general_factor),
                ("CAJA DE PLATANO", 2, "CJ", 23529.45 * general_factor),
                ("CAJA DE NARANJA", 2, "CJ", 23529.45 * general_factor),
            ]),
        ]

        vencimiento_default = datetime.date(2027, 4, 1)

        for supplier, doc_num, receipt_date, items in receipts:
            for name, qty, unit, price in items:
                # 1. Product
                cat = get_category(name)
                prod, created = Producto.objects.get_or_create(
                    nombre=name,
                    defaults={'categoria': cat, 'unidad_medida': unit}
                )
                
                # 2. Lote
                lote = Lote.objects.create(
                    producto=prod,
                    proveedor=supplier,
                    cantidad=qty,
                    precio_unitario=round(price, 2),
                    fecha_recepcion=receipt_date,
                    fecha_vencimiento=vencimiento_default,
                    numero_guia=doc_num,
                    estado='ACTIVO',
                    proceso='RECEPCION',
                    ubicacion_actual='BODEGA',
                    responsable_registro='Carga Automatizada AI'
                )
        print("Inventory re-loaded with Post-IVA prices.")

if __name__ == "__main__":
    reprocess_invoices()
