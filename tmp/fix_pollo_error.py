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

from inventario.models import Lote, RegistroServicio, MovimientoTrazabilidad, Producto

def fix_pollo_delivery():
    with transaction.atomic():
        # 1. Find the incorrect record
        # S05 was "COCINA CALIENTE", Date 2026-04-02 (service), loaded on 2026-04-06
        registro_incorrecto = RegistroServicio.objects.filter(
            responsable='Carga Automatizada AI',
            lote__producto__nombre__icontains='TRUTO',
            cantidad_servida=3.0,
            area='COCINA_CALIENTE'
        ).first()

        if not registro_incorrecto:
            print("  [ERROR] Could not find the incorrect Truto delivery record.")
            return

        lote_truto = registro_incorrecto.lote
        print(f"  [INFO] Found incorrect delivery: {lote_truto.producto.nombre} from lote {lote_truto.numero_lote}")

        # 2. Restore stock to Truto
        lote_truto.cantidad += 3.0
        if lote_truto.estado == 'CONSUMIDO':
            lote_truto.estado = 'ACTIVO'
        lote_truto.ubicacion_actual = 'BODEGA' # Restore it to bodega physically in the system for correction
        lote_truto.save()
        print(f"  [OK] Restored 3kg to {lote_truto.producto.nombre}")

        # 3. Find correct Pechuga Lote in BODEGA
        lote_pechuga = Lote.objects.filter(
            producto__nombre__icontains='PECHUGA',
            estado='ACTIVO',
            ubicacion_actual='BODEGA'
        ).order_by('fecha_vencimiento').first()

        if not lote_pechuga:
            # Maybe it's already in the area?
            lote_pechuga = Lote.objects.filter(
                producto__nombre__icontains='PECHUGA',
                estado='ACTIVO'
            ).order_by('fecha_vencimiento').first()

        if not lote_pechuga:
             print("  [ERROR] No Pechuga lotes found to satisfy delivery.")
             return

        print(f"  [INFO] Correcting to Pechuga: {lote_pechuga.producto.nombre} from lote {lote_pechuga.numero_lote}")

        # 4. Update the RegistroServicio
        registro_incorrecto.lote = lote_pechuga
        registro_incorrecto.observaciones += " (Corregido de Truto a Pechuga)"
        registro_incorrecto.save()

        # 5. Deduct from Pechuga
        lote_pechuga.cantidad -= 3.0
        if lote_pechuga.cantidad <= 0:
            lote_pechuga.cantidad = 0
            lote_pechuga.estado = 'CONSUMIDO'
        lote_pechuga.ubicacion_actual = 'COCINA_CALIENTE'
        lote_pechuga.save()

        # 6. Fix MovimientoTrazabilidad if exists
        movimiento = MovimientoTrazabilidad.objects.filter(
            lote=lote_truto,
            cantidad=3.0,
            hacia='COCINA_CALIENTE'
        ).first()
        if movimiento:
            movimiento.lote = lote_pechuga
            movimiento.observaciones += " (Corregido de Truto a Pechuga)"
            movimiento.save()

        print("  [SUCCESS] Delivery corrected successfully.")

if __name__ == "__main__":
    fix_pollo_delivery()
