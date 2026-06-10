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

def load_new_invoices():
    # Helper to map categories
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

    with transaction.atomic():
        # 1. Suppliers
        confical, _ = Proveedor.objects.get_or_create(rut='76.748.381-3', defaults={'nombre': 'Distribuidora y Comercializadora Ignacio Carvajal Castro E.I.R.L.'})
        macrofood, _ = Proveedor.objects.get_or_create(rut='96.733.580-0', defaults={'nombre': 'MACRO FOOD SPA.'})
        cial, _ = Proveedor.objects.get_or_create(rut='80.186.300-0', defaults={'nombre': 'CONSORCIO INDUSTRIAL DE ALIMENTOS S.A.'})
        casnorte, _ = Proveedor.objects.get_or_create(rut='76.286.101-1', defaults={'nombre': 'COMERCIALIZADORA ASESORIAS Y SERVICIOS DEL NORTE LIMITADA'})
        icb, _ = Proveedor.objects.get_or_create(rut='77.965.620-9', defaults={'nombre': 'ICB FOOD SERVICE SPA'})
        nevada, _ = Proveedor.objects.get_or_create(rut='77.851.255-6', defaults={'nombre': 'NEVADA PREMIUM SPA'})
        nora, _ = Proveedor.objects.get_or_create(rut='6.308.725-4', defaults={'nombre': 'NORA BERTA CACERES PEREZ'})

        # 2. Data
        receipts = [
            # CONFICAL (Factura 247236) - 2026-04-02
            (confical, "247236", datetime.date(2026, 4, 2), [
                ("SELZ MINI JAMON BS 1X40X35 LEY", 600, "UN", 231),
                ("SELZ MINI QUESO BS 1X40X35 LEY", 600, "UN", 231),
                ("NIKOLO TRAD. 12X20X24G 2024", 120, "UN", 4938),
                ("GOLPE 4X30X27G", 40, "UN", 6845),
            ]),
            # MACRO FOOD (Factura 1115778) - 2026-04-02
            (macrofood, "1115778", datetime.date(2026, 4, 2), [
                ("Refresco 33 Caribeño Pera", 10, "KG", 3147),
                ("Refresco 33 Caribeño Naranja", 10, "KG", 3147),
                ("Refresco 33 Caribeño Frutilla", 20, "KG", 3147),
                ("Refresco 33 Caribeño Melon Tuna", 10, "KG", 3147),
                ("Merengue", 10, "KG", 3297),
                ("Cappuccino Premium", 20, "KG", 7494),
                ("Sopa De Carne Con Arroz Premium", 10, "KG", 2796),
                ("Semola Con Leche", 10, "KG", 2762),
                ("Bavarais Limon", 10, "KG", 4957),
                ("Jalea 15 Manzana", 10, "KG", 4324),
                ("Jalea 15 Piña", 10, "KG", 4324),
                ("Leche Asada (Comercial)", 10, "KG", 2945),
                ("Salsa de Caramelo Premium c/logo", 10, "KG", 3435),
                ("Crema De Esparragos Premium", 10, "KG", 2588),
                ("Crema De Choclo Premium", 10, "KG", 2588),
                ("Crema De Pollo Premium", 10, "KG", 2588),
                ("Crema De Verduras Premium", 10, "KG", 2654),
                ("Sopa De Carne Con Fideos Premium", 10, "KG", 2792),
                ("Mermelada de Frutilla (1 K)", 20, "KG", 3299),
                ("Mermelada de Mora (1 K)", 10, "KG", 3299),
                ("Mermelada de Guinda (1 K)", 10, "KG", 3299),
                ("Mermelada de Durazno (1 K)", 10, "KG", 3299),
            ]),
            # CASNORTE (Guia 3209) - 2026-04-01
            (casnorte, "G3209", datetime.date(2026, 4, 1), [
                ("FIBRA ABRASIVA ULTRA PESADA", 100, "UN", 960),
                ("PAÑO MULTIUSO ROLLO X20 CLASICA", 30, "UN", 5797),
                ("GUANTE CONVENIENTE TALLA S", 12, "UN", 2178),
                ("GUANTE CONVENIENTE TALLA M", 20, "UN", 2178),
                ("GUANTE CONVENIENTE TALLA L", 12, "UN", 2178),
                ("ESCOBILLON ECONOMICO 100% RECICLADO", 20, "UN", 3012),
                ("ESPONJA LISA VTX PRO", 60, "UN", 312),
                ("BOLSAS DE BASURA BIOROLLO 70X90", 20, "UN", 1125),
                ("REPUESTO MOPA HUMEDA ALGODON 24 OZ", 20, "UN", 5019),
                ("BOLSAS DE BASURA BIOROLLO 50X70", 20, "UN", 614),
                ("BARRE AGUA 55 CMS - VTX PRO", 10, "UN", 9220),
                ("ROCIADOR 1000 CC", 10, "UN", 3120),
            ]),
            # CIAL (Factura 49491260) - 2026-03-31
            (cial, "49491260", datetime.date(2026, 3, 31), [
                ("SALAME PIEZA 1KG LP", 15, "KG", 7692),
                ("PRIETA 10x400 GR LP", 12, "CJ", 5656),
            ]),
            # ICB (Factura 5522527) - 2026-04-02
            (icb, "5522527", datetime.date(2026, 4, 2), [
                ("ACEITE VEGETAL 5 L", 20, "UN", 8713),
            ]),
            # ICB (Factura 5522528) - 2026-04-02
            (icb, "5522528", datetime.date(2026, 4, 2), [
                ("CHURRASCO VACUNO FLOW PACK 120 g", 30, "UN", 19850),
                ("HIGADO VACUNO", 25.94, "KG", 3270),
            ]),
            # ICB (Factura 5524698) - 2026-04-02
            (icb, "5524698", datetime.date(2026, 4, 2), [
                ("PANGASIUS FILETE S/P 1KG 170-220G", 10, "CJ", 28000),
            ]),
            # NEVADA (Factura 684) - 2026-04-02
            (nevada, "684", datetime.date(2026, 4, 2), [
                ("AGUA EN BIDON DE 20 LT", 40, "UN", 1300),
            ]),
            # NORA CACERES (Factura 9721) - 2026-04-02
            (nora, "9721", datetime.date(2026, 4, 2), [
                ("KILOS DE SANDIA", 29.6, "KG", 672.26),
                ("CAJA DE UVA", 1, "CJ", 25210.08),
                ("CAJA DE MANZANA", 5, "CJ", 27731.09),
                ("CAJA DE PLATANO", 2, "CJ", 23529.45),
                ("CAJA DE NARANJA", 2, "CJ", 23529.45),
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
                    precio_unitario=price,
                    fecha_recepcion=receipt_date,
                    fecha_vencimiento=vencimiento_default,
                    numero_guia=doc_num,
                    estado='ACTIVO',
                    proceso='RECEPCION',
                    ubicacion_actual='BODEGA',
                    responsable_registro='Carga Automatizada AI'
                )
                print(f"Created Lote: {name} - Qty: {qty} {unit} - Fact/Guia: {doc_num}")

if __name__ == "__main__":
    load_new_invoices()
    print("\n--- Processing Finished Successfully ---")
