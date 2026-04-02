import os
import sys
import django
from django.db import transaction
import datetime

# Setup Django
sys.path.append(r'C:\Users\Coalfa\Desktop\RRHHBG\Gestios_Citas_IS')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'san_lucas.settings') 
django.setup()

from inventario.models import Producto, Lote, Proveedor

def load_all_paperwork():
    bidfood, _ = Proveedor.objects.get_or_create(nombre="Bidfood Chile S.A.", defaults={'rut': '76.111.152-3'})
    icb, _ = Proveedor.objects.get_or_create(nombre="ICB FOOD SERVICE", defaults={'rut': '77.965.620-9'})

    # Mapping to UNIDAD_CHOICES: KG, G, L, ML, UN, CAJA
    unidades_map = {
        'UN': 'UN',
        'KG': 'KG',
        'CAJA': 'CAJA',
        'LT': 'L',
        'Unid': 'UN',
        'Kilo': 'KG',
        'CAJA_5LT': 'CAJA',
    }

    # Gross Factor
    IVA = 1.19
    hoy = datetime.date(2026, 4, 1)

    # PO 12114 Bidfood (23 items)
    po_12114 = [
        ("CREMA VEGETAL", "UN", 24, 3439, "ABARROTES"),
        ("CONCENTRADO DE TOMATE *3 KILOS", "UN", 16, 7413, "ABARROTES"),
        ("CALDO CONCENTRADO DE POLLO", "KG", 10, 2105, "ABARROTES"),
        ("COCTEL DE FRUTA * 3 KILOS", "UN", 18, 5364, "ABARROTES"),
        ("TE HIERBAS * 100 UNID", "UN", 60, 4617, "ABARROTES"),
        ("MAYONESA *1 KILO CAROZZI", "KG", 100, 1800, "ABARROTES"),
        ("MOSTAZA TRAVERSO * 1 KILO", "KG", 40, 1020, "ABARROTES"),
        ("ARROZ GRADO 2", "KG", 200, 1176, "ABARROTES"),
        ("AZUCAR * 1 KILO", "KG", 200, 788, "ABARROTES"),
        ("SPAGUETTI CAROZZI * 5 KILOS", "UN", 20, 7517, "ABARROTES"),
        ("ESPIRALES CAROZZI * 5 KILOS", "UN", 20, 7505, "ABARROTES"),
        ("ACEITE DE OLIVA * 5 LITROS", "UN", 2, 24007, "ABARROTES"),
        ("LAVALOZA INDUSTRIAL DEFOR 2*5 LITROS", "CAJA", 10, 10750, "LIMPIEZA"),
        ("KETCHUP CAROZZI * 1 KILO", "KG", 40, 1570, "ABARROTES"),
        ("MERMELADA * 1 KILO FRAMBUEZA", "KG", 10, 3806, "ABARROTES"),
        ("CHOCOLATE DULCE 1*1", "KG", 10, 5630, "ABARROTES"),
        ("CHOCOLATE AMARGO 1*1", "KG", 10, 8947, "ABARROTES"),
        ("TRIGO MOTE", "KG", 10, 2185, "ABARROTES"),
        ("COCO RALLADO *250 GR", "UN", 30, 2097, "ABARROTES"),
        ("COSTILLAR DE CERDO ADOBO", "KG", 250, 4190, "CARNES"),
        ("MERMELADA * 1 KILO DURAZNO", "UN", 20, 3093, "ABARROTES"),
        ("MERMELADA * 1 KILO DAMASCO", "UN", 30, 2496, "ABARROTES"),
        ("PAPA PREFITA 12 MM * 2 KILOS", "UN", 50, 2837, "CONGELADOS"),
    ]

    # Factura 03391167 Bidfood (21 items)
    fact_1167 = [
        ("ACEITE DE OLIVA DELICATO 1X 5 LT", "UN", 2.0, 24008, "ABARROTES"),
        ("AZUCAR 10 X 1 KG", "UN", 200.0, 788, "ABARROTES"),
        ("CALDO CONCENTRADO DE POLLO TKF 1X1 KG", "UN", 10.0, 2105, "ABARROTES"),
        ("TE HIERBAS SURTIDAS SUPREMO 1X100 UN.", "UN", 60.0, 4617, "ABARROTES"),
        ("MERMELADA DE FRAMBUESA 1X1 KG", "UN", 10.0, 3807, "ABARROTES"),
        ("MERMELADA DE DURAZNO 1X1 KG", "UN", 20.0, 3093, "ABARROTES"),
        ("MERMELADA DE DAMASCO 1X1 KG.", "UN", 30.0, 2496, "ABARROTES"),
        ("CREMA VEGETAL DECOR UP 12X1 LT", "UN", 24.0, 3439, "ABARROTES"),
        ("ESPIRALES CAROZZI 1X5 KG", "UN", 20.0, 7505, "ABARROTES"),
        ("SPAGUETTI 1X5 KG", "UN", 20.0, 7517, "ABARROTES"),
        ("CHOCOLATE DULCE EN POLVO 1X1 KG.", "UN", 10.0, 5630, "ABARROTES"),
        ("CHOCOLATE AMARGO EN POLVO 1X1 KG.", "UN", 10.0, 8947, "ABARROTES"),
        ("COCO RALLADO 1X250 GR.", "UN", 30.0, 2097, "ABARROTES"),
        ("MAYONESA CAROZZI 10X1 KG", "UN", 100.0, 1800, "ABARROTES"),
        ("MOSTAZA 10X1 KG", "UN", 40.0, 1020, "ABARROTES"),
        ("TRIPLE CONCENTRADO DE TOMATE 1X3 KG.", "UN", 16.0, 7413, "ABARROTES"),
        ("ARROZ IMP. TUCAPEL BLUE BONNET G2 10X1 KG", "UN", 200.0, 1176, "ABARROTES"),
        ("KETCHUP CAROZZI 10X1 KG", "UN", 40.0, 1570, "ABARROTES"),
        ("COCKTAIL DE FRUTAS SMART CHOICE IMP. 3 KG", "UN", 18.0, 5364, "ABARROTES"),
        ("COSTILLAR ADOBO CHILENO (MM)", "KG", 252.92, 4190, "CARNES"),
        ("LAVALOZA INDUSTRIAL DEFORT 2X5 LT", "CAJA", 10.0, 10750, "LIMPIEZA"),
    ]

    # Factura 03391169 Bidfood (1 item)
    fact_1169 = [
        ("PAPAS PREFRITAS SAZONADA STAR 12MM 5X2 KG", "UN", 50.0, 11400, "CONGELADOS") 
    ]

    # PO 12115 ICB (3 items)
    po_12115 = [
        ("PULPA PIERNA SDE CERDO SIN HUESO", "KG", 120.0, 3490, "CARNES"),
        ("PAPA DUQUESA * 10 KILOS", "CAJA", 10.0, 26000, "CONGELADOS"),
        ("VACUNO GANSO", "KG", 80.0, 6877, "CARNES"),
    ]

    # Factura 5520444 ICB (2 items)
    fact_5520444 = [
        ("PAPAS DUQUESAS 2,5kg x 4 (C4)", "UN", 2.0, 26000, "CONGELADOS"),
        ("PULPA PIERNA CERDO 1/16 IWP BRASIL 21 k", "KG", 114.78, 3490, "CARNES"),
    ]

    # Factura 55520411 ICB (2 items)
    fact_55520411 = [
        ("PAPAS DUQUESAS 2,5kg x 4 (C4)", "UN", 4.0, 26000, "CONGELADOS"),
        ("GANSO CAT V VACIO PARAGUAY", "KG", 83.75, 7090, "CARNES"),
    ]

    all_data = [
        (po_12114, bidfood, "OC 12114"),
        (fact_1167, bidfood, "Fact 03391167"),
        (fact_1169, bidfood, "Fact 03391169"),
        (po_12115, icb, "OC 12115"),
        (fact_5520444, icb, "Fact 5520444"),
        (fact_55520411, icb, "Fact 55520411"),
    ]

    from inventario.models import _generar_numero_lote

    with transaction.atomic():
        for lines, provider, ref in all_data:
            for desc, unit_key, cant, net_px, cat in lines:
                gross_px = net_px * IVA
                
                prod, _ = Producto.objects.get_or_create(
                    nombre=desc,
                    defaults={
                        'categoria': cat, 
                        'unidad_medida': unidades_map.get(unit_key, 'UN')
                    }
                )
                
                Lote.objects.create(
                    producto=prod,
                    proveedor=provider,
                    cantidad=cant,
                    precio_unitario=gross_px,
                    fecha_recepcion=hoy,
                    fecha_vencimiento=datetime.date(2026, 6, 1),
                    estado='ACTIVO',
                    numero_lote=_generar_numero_lote(prod.nombre),
                    observaciones=f"Cargado desde {ref}"
                )
                print(f"Added {cant} unts of {desc} at Gross Px: {gross_px}")

if __name__ == "__main__":
    load_all_paperwork()
    print("All paperwork lines loaded successfully.")
    print("All paperwork lines loaded successfully.")
