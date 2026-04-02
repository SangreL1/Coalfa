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

def load_products():
    with transaction.atomic():
        # 1. Create/Get Suppliers
        bidfood, _ = Proveedor.objects.get_or_create(nombre="Bidfood Chile S.A.", defaults={'rut': '76.111.152-3'})
        icb, _ = Proveedor.objects.get_or_create(nombre="ICB FOOD SERVICE", defaults={'rut': '77.965.620-9'})

        # 2. Data from Invoices
        # Format: (Proveedor, Nombre, Unidad, Cantidad, Precio, Categoria, Guia/Factura)
        data = [
            # Bidfood (Invoice 03391167)
            (bidfood, "ACEITE DE OLIVA DELICATO 1X 5 LT", "UN", 2.0, 24008, "ABARROTES", "03391167"),
            (bidfood, "AZUCAR 10 X 1 KG", "UN", 200.0, 788, "ABARROTES", "03391167"),
            (bidfood, "CALDO CONCENTRADO DE POLLO TKF 1X1 KG", "UN", 10.0, 2105, "ABARROTES", "03391167"),
            (bidfood, "TE HIERBAS SURTIDAS SUPREMO 1X100 UN", "UN", 60.0, 4617, "ABARROTES", "03391167"),
            (bidfood, "MERMELADA DE FRAMBUESA 1X1 KG", "UN", 10.0, 3807, "ABARROTES", "03391167"),
            (bidfood, "MERMELADA DE DURAZNO 1X1 KG", "UN", 20.0, 3093, "ABARROTES", "03391167"),
            (bidfood, "MERMELADA DE DAMASCO 1X1 KG", "UN", 30.0, 2496, "ABARROTES", "03391167"),
            (bidfood, "CREMA VEGETAL DECOR UP 12X1 LT", "UN", 24.0, 3439, "ABARROTES", "03391167"),
            (bidfood, "ESPIRALES CAROZZI 1X5 KG", "UN", 20.0, 7505, "ABARROTES", "03391167"),
            (bidfood, "SPAGUETTI 1X5 KG", "UN", 20.0, 7517, "ABARROTES", "03391167"),
            (bidfood, "CHOCOLATE DULCE EN POLVO 1X1 KG", "UN", 10.0, 5630, "ABARROTES", "03391167"),
            (bidfood, "CHOCOLATE AMARGO EN POLVO 1X1 KG", "UN", 10.0, 8947, "ABARROTES", "03391167"),
            (bidfood, "COCO RALLADO 1X250 GR", "UN", 30.0, 2097, "ABARROTES", "03391167"),
            (bidfood, "MAYONESA CAROZZI 10X1 KG", "UN", 100.0, 1800, "ABARROTES", "03391167"),
            (bidfood, "MOSTAZA 10X1 KG", "UN", 40.0, 1020, "ABARROTES", "03391167"),
            (bidfood, "TRIPLE CONCENTRADO DE TOMATE 1X3 KG", "UN", 16.0, 7413, "ABARROTES", "03391167"),
            (bidfood, "ARROZ IMP. TUCAPEL BLUE BONNET G2 10X1 KG", "UN", 200.0, 1176, "ABARROTES", "03391167"),
            (bidfood, "KETCHUP CAROZZI 10X1 KG", "UN", 40.0, 1570, "ABARROTES", "03391167"),
            (bidfood, "COCKTAIL DE FRUTAS SMART CHOICE IMP. 3 KG", "UN", 18.0, 5364, "ABARROTES", "03391167"),
            (bidfood, "COSTILLAR ADOBO CHILENO (MM)", "KG", 252.92, 4190, "CARNES", "03391167"),
            (bidfood, "LAVALOZA INDUSTRIAL DEFORT 2X5 LT", "CAJA", 10.0, 10750, "LIMPIEZA", "03391167"),
            
            # Bidfood (Invoice 03391169)
            (bidfood, "PAPAS PREFRITAS SAZONADA STAR 12MM 5X2 KG", "UN", 50.0, 2837, "CONGELADOS", "03391169"),
            
            # Additional from OC 12114
            (bidfood, "TRIGO MOTE", "KG", 10.0, 2185, "ABARROTES", "12114"),
            
            # ICB (Invoice 5520444)
            (icb, "PAPAS DUQUESAS 2.5kg x 4 (C4)", "UN", 2.0, 26000, "CONGELADOS", "5520444"),
            (icb, "PULPA PIERNA CERDO 1/16 IWP BRASIL 21 k", "KG", 114.78, 3890, "CARNES", "5520444"),
            
            # ICB (Invoice 55520411 / OC 5520411)
            (icb, "GANSO CAT V VACIO PARAGUAY", "KG", 83.75, 7090, "CARNES", "55520411"),
            (icb, "PAPAS DUQUESAS 2.5kg x 4 (C4)", "UN", 4.0, 26000, "CONGELADOS", "55520411"),
        ]

        recepcion_date = datetime.date(2026, 4, 1)
        vencimiento_date = datetime.date(2027, 4, 1) # Default 1 year

        for prov, name, unit, qty, price, cat, doc_ref in data:
            # Create/Get Product
            prod, created = Producto.objects.get_or_create(
                nombre=name,
                defaults={'categoria': cat, 'unidad_medida': unit}
            )
            
            # Create Lote
            lote = Lote.objects.create(
                producto=prod,
                proveedor=prov,
                cantidad=qty,
                precio_unitario=price,
                fecha_recepcion=recepcion_date,
                fecha_vencimiento=vencimiento_date,
                numero_guia=doc_ref,
                estado='ACTIVO'
            )
            print(f"Added: {name} ({qty} {unit}) from {prov.nombre} - Fact/OC: {doc_ref}")

if __name__ == "__main__":
    load_products()
    print("All products loaded successfully.")
