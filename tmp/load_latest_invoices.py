import os
import sys
import django
import datetime
from django.db import transaction

# Setup
BASE_DIR = r'C:\Users\Coalfa\Desktop\RRHHBG\Gestios_Citas_IS'
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'san_lucas.settings') 
django.setup()

from inventario.models import Lote, Producto, Proveedor

def load_invoices():
    andina, _ = Proveedor.objects.get_or_create(nombre="Embotelladora Andina S.A.", defaults={'contacto': '911440008'})
    ariztia = Proveedor.objects.get(nombre="Ariztia")

    def add_lote(prov, doc_num, date_obj, items):
        with transaction.atomic():
            for name, qty, cat, uprice in items:
                prod, _ = Producto.objects.get_or_create(
                    nombre=name.upper(),
                    defaults={'categoria': cat}
                )
                # Ensure correct unit of medida
                if 'KG' in name.upper() or 'CEBOLLA' in name.upper() or 'POLLO' in name.upper():
                    prod.unidad_medida = 'KG'
                elif 'PACK' in name.upper() or 'UNID' in name.upper() or 'HUEVO' in name.upper():
                    prod.unidad_medida = 'UN'
                prod.save()

                Lote.objects.create(
                    producto=prod,
                    proveedor=prov,
                    # numero_lote will be auto-generated if we leave it empty or better call the generator
                    # Actually, if we leave it empty, the save() method in models.py (if it exists) or we should call it.
                    # Let's check models.py for save() method.
                    numero_guia=doc_num,
                    cantidad=qty,
                    precio_unitario=round(uprice, 2),
                    fecha_recepcion=date_obj,
                    fecha_vencimiento=date_obj + datetime.timedelta(days=180),
                    ubicacion_actual='BODEGA',
                    estado='ACTIVO',
                    responsable_registro='Carga Automatizada AI'
                )
                print(f"  [OK] Added {qty} of {name} - Total: ${round(qty * uprice, 2)}")

    print("\n--- Processing 094388184 (Coca Andina) ---")
    add_lote(andina, "094388184", datetime.date(2026, 4, 6), [
        ("ANDI NARANJA PERSONAL TT200CC X 6*4", 3, 'BEBIDAS', 6432.33),
        ("ANDF PINA PERSONAL 200CC X 6*4", 3, 'BEBIDAS', 6432.33),
        ("COCA COLA PACK LT350CC 1*6", 180, 'BEBIDAS', 4068.08),
        ("COCA COLA SIN AZUCAR LT350CC X 6", 10, 'BEBIDAS', 4068.2),
        ("SPRITE MIDCAL LT350CC X 6", 10, 'BEBIDAS', 4068.3),
        ("FANTA NARANJA ORIGINAL LT350ML X6", 10, 'BEBIDAS', 4068.0),
    ])

    print("\n--- Processing 12121 (Ariztia OC) ---")
    add_lote(ariztia, "12121", datetime.date(2026, 4, 1), [
        ("QUESO GAUDA BARRA", 120, 'LACTEOS', 5355.0),
        ("HUEVO PRIMERA *180 UNID", 36, 'LACTEOS', 37200.0),
        ("PECHUGA POLLO DESHUESADA CONGELADA", 200, 'CARNES', 4046.0),
    ])

    print("\n--- Processing 12125 (Coca Andina OC) ---")
    add_lote(andina, "12125", datetime.date(2026, 4, 2), [
        ("BEBIDA LATA 350 CC COCA COLA 180 PACK*6 UNID", 1080, 'BEBIDAS', 641.87),
        ("BEBIDA LATA 350 CC SPRITE 10 PACK*6 UNID", 60, 'BEBIDAS', 678.52),
        ("BEBIDA LATA 350 CC COCA ZERO 10 PACK*6 UNID", 60, 'BEBIDAS', 641.87),
        ("JUGOS 200 CC 1*24 SABORES SURTIDOS", 6, 'BEBIDAS', 6141.13),
        ("BEBIDA LATA 350 CC FANTA 10 PACK*6 UNID", 60, 'BEBIDAS', 641.87),
    ])

    print("\n--- Processing 38218775 (Ariztia Fac) ---")
    add_lote(ariztia, "38218775", datetime.date(2026, 4, 2), [
        ("PECHUGA POLLO SHP IQF", 163.07, 'CARNES', 4046.0),
    ])

    print("\n--- Processing 38218776 (Ariztia Fac) ---")
    add_lote(ariztia, "38218776", datetime.date(2026, 4, 2), [
        ("QUESO CHANCO BARRA RUMAY 6X1", 70.91, 'LACTEOS', 5355.0),
    ])

if __name__ == "__main__":
    load_invoices()
