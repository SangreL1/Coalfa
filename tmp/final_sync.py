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

def final_sync():
    with transaction.atomic():
        Lote.objects.filter(responsable_registro='Carga Automatizada AI').delete()

        confical, _ = Proveedor.objects.get_or_create(rut='76.748.381-3', defaults={'nombre': 'Distribuidora y Comercializadora Ignacio Carvajal Castro E.I.R.L.'})
        macrofood, _ = Proveedor.objects.get_or_create(rut='96.733.580-0', defaults={'nombre': 'MACRO FOOD SPA.'})
        cial, _ = Proveedor.objects.get_or_create(rut='80.186.300-0', defaults={'nombre': 'CONSORCIO INDUSTRIAL DE ALIMENTOS S.A.'})
        casnorte, _ = Proveedor.objects.get_or_create(rut='76.286.101-1', defaults={'nombre': 'COMERCIALIZADORA ASESORIAS Y SERVICIOS DEL NORTE LIMITADA'})
        icb, _ = Proveedor.objects.get_or_create(rut='77.965.620-9', defaults={'nombre': 'ICB FOOD SERVICE SPA'})
        nevada, _ = Proveedor.objects.get_or_create(rut='77.851.255-6', defaults={'nombre': 'NEVADA PREMIUM SPA'})
        nora, _ = Proveedor.objects.get_or_create(rut='6.308.725-4', defaults={'nombre': 'NORA BERTA CACERES PEREZ'})

        def add_batch(supplier, doc_num, date, items, neto_total, final_total):
            factor = final_total / neto_total if neto_total > 0 else 1.19
            for name, qty, unit, neto_price in items:
                prod, _ = Producto.objects.get_or_create(nombre=name, defaults={'categoria': 'OTRO', 'unidad_medida': unit})
                Lote.objects.create(
                    producto=prod, proveedor=supplier, cantidad=qty, 
                    precio_unitario=round(neto_price * factor, 2),
                    fecha_recepcion=date, fecha_vencimiento=datetime.date(2027, 4, 1),
                    numero_guia=doc_num, responsable_registro='Carga Automatizada AI'
                )

        # Loading ALL 15 PNGs now to be sure
        
        # 1. Confical (247236) - 1.360.527
        add_batch(confical, "247236", datetime.date(2026, 4, 2), [
            ("SELZ MINI JAMON BS 1X40X35 LEY", 600, "UN", 231),
            ("SELZ MINI QUESO BS 1X40X35 LEY", 600, "UN", 231),
            ("NIKOLO TRAD. 12X20X24G 2024", 120, "UN", 4938),
            ("GOLPE 4X30X27G", 40, "UN", 6845),
        ], 1143300, 1360527)

        # 2. Macro (1115778) - 1.078.024
        add_batch(macrofood, "1115778", datetime.date(2026, 4, 2), [
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
        ], 892680, 1078024)

        # 3. Macro OC 12119 - 1.174.352 
        add_batch(macrofood, "OC12119", datetime.date(2026, 4, 1), [
            ("Saborizante Frutilla (OC)", 10, "KG", 3147),
            ("Sopa De Carne Con Verduras Premium (OC)", 10, "KG", 2792),
            ("Refresco 33 Caribeño Pera (OC)", 10, "KG", 3147),
            ("Refresco 33 Caribeño Naranja (OC)", 10, "KG", 3147),
            ("Refresco 33 Caribeño Frutilla (OC)", 20, "KG", 3147),
            ("Refresco 33 Caribeño Melon Tuna (OC)", 10, "KG", 3147),
            ("Merengue (OC)", 10, "KG", 3297),
            ("Cappuccino Premium (OC)", 20, "KG", 7494),
            ("Sopa De Carne Con Arroz (OC)", 10, "KG", 2796),
            ("Semola Con Leche (OC)", 10, "KG", 2762),
            ("Bavarais Limon (OC)", 10, "KG", 4957),
            ("Jalea 15 Manzana (OC)", 10, "KG", 4324),
            ("Jalea 15 Piña (OC)", 10, "KG", 4324),
            ("Leche Asada (OC)", 10, "KG", 2945),
            ("Salsa de Caramelo (OC)", 10, "KG", 3435),
            ("Crema De Esparragos (OC)", 10, "KG", 2588),
            ("Crema De Choclo (OC)", 10, "KG", 2588),
            ("Crema De Pollo (OC)", 10, "KG", 2588),
            ("Crema De Verduras (OC)", 10, "KG", 2654),
            ("Sopa De Carne Con Fideos (OC)", 10, "KG", 2792),
            ("Mermelada Frutilla (OC)", 20, "KG", 3299),
            ("Mermelada Mora (OC)", 10, "KG", 3299),
            ("Mermelada Guinda (OC)", 10, "KG", 3299),
            ("Mermelada Durazno (OC)", 10, "KG", 3299),
        ], 972322, 1174352)

        # 4. ICB OC 12118 - 516.769
        add_batch(icb, "OC12118", datetime.date(2026, 4, 1), [
            ("ACEITE VEGETAL 5 L (OC)", 20, "UN", 8713),
            ("PAPA DUQUESA 10 KILOS (OC)", 10, "CJ", 26000),
        ], 434260, 516769)

        # 5. ICB OC 12126 - 333.200
        add_batch(icb, "OC12126", datetime.date(2026, 4, 1), [
            ("PANGASIUS FILETE (OC)", 10, "CJ", 28000),
        ], 280000, 333200)

        # 6. Nevada OC 12123 - 61.880
        add_batch(nevada, "OC12123", datetime.date(2026, 4, 1), [
            ("AGUA EN BIDON (OC)", 40, "UN", 1300),
        ], 52000, 61880)

        # 7. CIAL OC 12110 - 181.100
        add_batch(cial, "OC12110", datetime.date(2026, 3, 30), [
            ("SALAME PIEZA 0,830 GR (OC)", 12.45, "KG", 6936),
            ("PRIETA 10*400 GRS (OC)", 3, "CJ", 21944),
        ], 152185, 181100)

        # 8. Casnorte OC 12116 - 576.722
        add_batch(casnorte, "OC12116", datetime.date(2026, 4, 1), [
            ("FIBRA LIMPIEZA ULTRA PESADA (OC)", 100, "UN", 756),
            ("PAÑO MULTIUSO ROLLO (OC)", 30, "UN", 3705),
            ("GUANTE AMARILLO L (OC)", 12, "UN", 1695),
            ("GUANTE AMARILLO M (OC)", 20, "UN", 1695),
            ("GUANTE AMARILLO S (OC)", 12, "UN", 1695),
            ("ESCOBILLON ECONOMICO (OC)", 20, "UN", 1138),
            ("ESPONJA LISA (OC)", 60, "UN", 149),
            ("BOLSA BASURA 70X90 (OC)", 20, "UN", 820),
            ("REPUESTO MOPA 24 OZ (OC)", 10, "UN", 5019),
            ("BOLSA BASURA 50X70 (OC)", 20, "UN", 820),
            ("ROCIADOR 1 LITRO (OC)", 10, "UN", 1932),
            ("BARRE AGUA 55CM (OC)", 10, "UN", 8930),
        ], 484640, 576722)

        # 9. Casnorte Guia 3209 - 753.193
        add_batch(casnorte, "G3209", datetime.date(2026, 4, 1), [
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
        ], 632935, 753193)

        # 10. CIAL Factura 49491260 - 218.070
        add_batch(cial, "49491260", datetime.date(2026, 3, 31), [
            ("SALAME PIEZA 1KG LP", 15, "KG", 7692),
            ("PRIETA 10x400 GR LP", 12, "CJ", 5656),
        ], 183252, 218070)

        # 11. ICB Fac 5522527 - 207.358
        add_batch(icb, "5522527", datetime.date(2026, 4, 2), [
            ("ACEITE VEGETAL 5 L", 20, "UN", 8713),
        ], 174250, 207358)

        # 12. ICB Fac 5522528 - 809.586
        add_batch(icb, "5522528", datetime.date(2026, 4, 2), [
            ("CHURRASCO VACUNO FLOW PACK 120 g", 30, "UN", 19850),
            ("HIGADO VACUNO", 25.94, "KG", 3270),
        ], 680324, 809586)

        # 13. ICB Fac 5524698 - 333.200
        add_batch(icb, "5524698", datetime.date(2026, 4, 2), [
            ("PANGASIUS FILETE S/P 1KG 170-220G", 10, "CJ", 28000),
        ], 280000, 333200)

        # 14. Nevada Fac 684 - 61.880
        add_batch(nevada, "684", datetime.date(2026, 4, 2), [
            ("AGUA EN BIDON DE 20 LT", 40, "UN", 1300),
        ], 52000, 61880)

        # 15. Nora Fac 9721 - 330.680
        add_batch(nora, "9721", datetime.date(2026, 4, 2), [
            ("KILOS DE SANDIA", 29.6, "KG", 672.26),
            ("CAJA DE UVA", 1, "CJ", 25210.08),
            ("CAJA DE MANZANA", 5, "CJ", 27731.09),
            ("CAJA DE PLATANO", 2, "CJ", 23529.45),
            ("CAJA DE NARANJA", 2, "CJ", 23529.45),
        ], 277882, 330680)

    print("Success. Run check_total.py to verify.")

if __name__ == "__main__":
    final_sync()
