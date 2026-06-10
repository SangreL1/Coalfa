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

from inventario.models import Lote, Producto, RegistroServicio, MovimientoTrazabilidad

def deliver(area, date_str, items):
    """
    date_str: 'YYYY-MM-DD'
    items: list of (search_term, quantity)
    """
    print(f"\n>>> Area: {area} | Date: {date_str}")
    with transaction.atomic():
        for term, qty in items:
            # 1. Standardize quantity (Box to Kg conversion for Meat)
            original_qty = qty
            if any(m in term.upper() for m in ['POLLO', 'CARNE', 'VACUNO', 'CHANCHO']) and qty < 10:
                # Assuming if they ask for <10 for huge groups, they mean boxes
                # We saw 1 Caja = 10.19 Kg for Ariztia
                qty = qty * 10.19 
                print(f"  [CONV] {term}: {original_qty} BOX -> {qty} KG")

            # 2. Find product
            prod = Producto.objects.filter(nombre__icontains=term).order_by('-id').first()
            if not prod:
                print(f"  [SKIP] Product not found for term: {term}")
                continue
            
            # 3. Find Lote (Active, Bodega)
            lote = Lote.objects.filter(producto=prod, estado='ACTIVO', ubicacion_actual='BODEGA').order_by('fecha_vencimiento').first()
            if not lote:
                # Fallback to any active lote
                lote = Lote.objects.filter(producto=prod, estado='ACTIVO').order_by('fecha_vencimiento').first()
            
            if not lote:
                print(f"  [SKIP] No stock for {prod.nombre}")
                continue

            # 4. Record consumption
            RegistroServicio.objects.create(
                lote=lote,
                cantidad_servida=qty,
                area=area,
                responsable='Carga Automatizada AI',
                observaciones=f"Carga desde Solicitud Insumos. Original: {original_qty} {term}"
            )
            
            # 5. Update Lote
            lote.cantidad -= qty
            if lote.cantidad <= 0:
                lote.cantidad = 0
                lote.estado = 'CONSUMIDO'
            lote.ubicacion_actual = area
            lote.save()
            
            print(f"  [OK] Delivered {qty} {prod.unidad_medida} of {prod.nombre}")

def process_batch():
    # S01: PANADERIA, 01-04-26
    deliver('PANADERIA', '2026-04-01', [
        ('HARINA', 150), ('MANTECA', 8), ('LEVADURA', 1.5), ('SAL', 1.5)
    ])
    
    # S02: PANADERIA, 01-04-26
    deliver('PANADERIA', '2026-04-01', [
        ('BOLSA PREPICADA', 1), ('BOLSA BASURA', 1)
    ])
    
    # S02-2: MIX DESECHABLES
    deliver('LINEA', '2026-04-01', [
        ('SERVILLETA', 12), ('POTE MERMELADA', 500), ('CUCHARA TE', 700), ('GUANTES VINILO', 1),
        ('BOLSA BASURA', 10), ('PANO AMARILLO', 6)
    ])

    # S03: REPOSTERIA, 01-04-26
    deliver('REPOSTERIA', '2026-04-01', [
        ('AZUCAR', 10), ('HARINA', 10), ('MANTEQUILLA', 3), ('HUEVO', 100), ('LECHE ENTERA', 24)
    ])

    # S04 & S05: COCINA CALIENTE, 02-04-26
    deliver('COCINA_CALIENTE', '2026-04-02', [
        ('ARROZ', 23), ('ACEITE', 10), ('AZUCAR', 6), ('CHORIZO', 2), ('PECHUGA', 3), # 3->30kg conv
        ('PAPA FRITA', 110), ('HUEVO', 520)
    ])

    # S06: LINEA, 02-04-26
    deliver('LINEA', '2026-04-02', [
        ('BEBIDA', 300), ('CEREAL', 10), ('YOGURT', 500)
    ])

    # S07: COCINA CALIENTE, 03-04-26
    deliver('COCINA_CALIENTE', '2026-04-03', [
        ('VACUNO', 80), ('ZANAHORIA', 10), ('CEBOLLA', 10)
    ])

    # S08 & S09: LINEA, 03/04-04-26
    deliver('LINEA', '2026-04-04', [
        ('BOTELLA AGUA', 500), ('JUGO', 500)
    ])

    # S10: PANADERIA, 02-04-26
    deliver('PANADERIA', '2026-04-02', [
        ('HARINA', 150), ('MANTECA', 10)
    ])

    # S11: COLACION, 05-04-26
    deliver('COLACION', '2026-04-05', [
        ('PAN', 200), ('JAMON', 5), ('QUESO', 5)
    ])

    # S12: COCINA CALIENTE, 05-04-26
    deliver('COCINA_CALIENTE', '2026-04-05', [
        ('POLLO', 80), ('ARROZ', 40)
    ])

    # S13: COCINA FRIA, 05-04-26
    deliver('COCINA_FRIA', '2026-04-05', [
        ('LECHUGA', 20), ('APIO', 8), ('LIMON', 3), ('BROCOLI', 5), ('POROTO VERDE', 15),
        ('QUESO', 3.2), ('MOSTAZA', 2), ('MAYONESA', 5), ('GUANTES', 100)
    ])

    # S14: COCINA FRIA, 04-04-26
    deliver('COCINA_FRIA', '2026-04-04', [
        ('TOMATE', 15), ('LECHUGA', 30), ('LIMON', 2), ('REPOLLO', 1), ('PEPINO', 2),
        ('CILANTRO', 1), ('ARVEJA', 7), ('PRIMAVERA', 12), ('BROCOLI', 6), ('KETCHUP', 2),
        ('MAYONESA', 6), ('MOSTAZA', 1)
    ])

    # S15: COCINA FRIA, 03-04-26
    deliver('COCINA_FRIA', '2026-04-03', [
        ('LECHUGA', 20), ('TOMATE', 15), ('CILANTRO', 1), ('LIMON', 3), ('AJI', 3),
        ('COLIFLOR', 7), ('BROCOLI', 15), ('CHOCLO', 18), ('CEBOLLA CUBO', 5), ('MORRON', 1),
        ('ATUN', 5), ('MAYONESA', 6)
    ])

    # S16: COCINA FRIA, 02-04-26
    deliver('COCINA_FRIA', '2026-04-02', [
        ('PEPINO', 10), ('APIO', 2), ('ZANAHORIA', 12), ('BETARRAGA', 25), ('TOMATE', 15),
        ('LECHUGA', 10), ('LIMON', 2), ('CEBOLLIN', 1), ('RUSA', 7), ('JARDINERA', 15),
        ('PIMENTON', 1), ('CEBOLLA CUBO', 1), ('SALSA', 50), ('MAYONESA', 3), ('KETCHUP', 2),
        ('MOSTAZA', 1), ('ACEITUNA', 1), ('QUESO', 3.25)
    ])

if __name__ == "__main__":
    process_batch()
