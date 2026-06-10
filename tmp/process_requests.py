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

from inventario.models import Lote, MovimientoTrazabilidad, RegistroServicio

def deliver_batch(area, date_str, items):
    dt = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    with transaction.atomic():
        print(f"\n--- Area: {area} | Date: {date_str} ---")
        for search, qty in items:
            lotes = Lote.objects.filter(
                estado='ACTIVO', 
                ubicacion_actual='BODEGA',
                producto__nombre__icontains=search
            ).select_related('producto').order_by('fecha_vencimiento')
            
            if not lotes.exists():
                print(f"  [ERROR] No stock found for '{search}'")
                continue
            
            remaining = float(qty)
            for l in lotes:
                if remaining <= 0:
                    break
                
                can_take = min(float(l.cantidad), remaining)
                if can_take <= 0: continue

                # Record Movement
                MovimientoTrazabilidad.objects.create(
                    lote=l, desde='BODEGA', hacia=area, cantidad=can_take,
                    fecha=dt, responsable='Carga Automatizada AI', 
                    observaciones=f"Entrega Solicitud {date_str}"
                )
                # Record Consumption (Statistics)
                RegistroServicio.objects.create(
                    lote=l, cantidad_servida=can_take, area=area,
                    fecha=dt, responsable='Carga Automatizada AI',
                    observaciones=f"Consumo Solicitud {date_str}"
                )
                
                l.cantidad = float(l.cantidad) - can_take
                if l.cantidad <= 0:
                    l.estado = 'CONSUMIDO'
                    l.cantidad = 0
                else:
                    # If partially consumed, it might still be in the area
                    l.ubicacion_actual = area
                
                l.save()
                remaining -= can_take
                print(f"  [OK] Delivered {can_take} of '{l.producto.nombre}'")
            
            if remaining > 0:
                print(f"  [WARNING] Short on '{search}' by {remaining}")

def run():
    # S10 & S12: LINEA, 2026-04-01
    deliver_batch('LINEA', '2026-04-01', [
        ('TE BOLSITA', 500), ('CAFE', 2), ('TE HIERBAS', 400), ('AZUCAR', 6+6), ('LECHE', 8), ('JUGO', 5), ('MERMELADA', 5), ('HUEVO', 500), ('YOGURT', 500), ('MACEDONIA', 550), ('LOMITO', 350), ('QUESO', 20), ('MAYONESA', 2), ('SAL ', 4), ('NOVA', 4), ('SERVILLETILLA', 14+14), ('PAÑO AMARILLO', 3)
    ])

    # S11: COCINA FRIA, 2026-04-01
    deliver_batch('COCINA_FRIA', '2026-04-01', [
        ('REPOLLO', 4), ('TOMATE', 30), ('CEBOLLA', 5), ('LECHUGA', 20), ('LIMON', 3+5), ('CILANTRO', 2), ('HABAS', 8), ('CHOCLO', 26), ('BROCOLI', 7), ('CHAUCHA', 7), ('POLLO', 10), ('AJO', 1), ('OREGANO', 1), ('MAYONESA', 6), ('GUANTE VINILO TALLA M', 100)
    ])

    # S09: COCINA CALIENTE, 2026-04-01
    deliver_batch('COCINA_CALIENTE', '2026-04-01', [
        ('CORBATAS', 15), ('ACEITE', 15), ('PURE', 18), ('LECHE', 2), ('SOPA POLLO', 3), ('SOPA CARNE', 7), ('CEBOLLA', 8), ('MORRON', 4), ('ESPINACA', 30), ('AJO', 1), ('CHAMPIÑON', 8), ('VACUNO', 6), ('REPOLLO', 9), ('PAPA DUQUESA', 4), ('MAICENA', 1)
    ])

    # S04 & S05: COCINA CALIENTE, 2026-04-02
    deliver_batch('COCINA_CALIENTE', '2026-04-02', [
        ('VACUNO', 3), ('CEBOLLA', 8), ('MORRON', 2+2), ('ZANAHORIA', 1), ('HUEVO', 23+540), ('LECHE', 1), ('PASTELERA', 8), ('ARROZ', 9+4), ('ARVEJA', 2), ('REPOLLO', 3), ('AZUCAR', 2+4), ('CHORIZO', 2), ('POLLO', 3), ('PAPA FRITA', 110), ('ACEITE', 10), ('MANTECA', 2), ('LIMON', 5), ('AJI', 1)
    ])

    # S06 & S08: LINEA and REPOSTERIA, 2026-04-02
    deliver_batch('LINEA', '2026-04-02', [
        ('TE BOLSITA', 500), ('TE HIERBAS', 400), ('AZUCAR', 8), ('LECHE', 12), ('MERMELADA', 5), ('HUEVO', 480), ('YOGURT', 520), ('CAFE', 3), ('SERVILLETILLA', 18), ('CUCHARILLA', 700), ('GUANTE VINILO TALLA S', 100), ('GUANTE VINILO TALLA M', 100), ('NOVA', 2), ('BOLSA BASURA', 10), ('PAÑO AMARILLO', 6)
    ])
    deliver_batch('REPOSTERIA', '2026-04-02', [
        ('JALEA', 5), ('BAVAROIS', 6), ('VAINILLA', 1), ('HUEVO', 40), ('LECHE', 1), ('POLVO HORNEAR', 0.5), ('AZUCAR', 4), ('CHOCOLATE', 1), ('SALSA', 2), ('POTE GELATINA', 800)
    ])

    # S07 & S01: PANADERIA and LINEA, 2026-04-02/03
    deliver_batch('PANADERIA', '2026-04-02', [
        ('HARINA', 100), ('HARINA INTEGRAL', 2), ('MANTECA', 2), ('GRASA', 1), ('ACEITE', 5)
    ])
    deliver_batch('LINEA', '2026-04-03', [
        ('GUANTE VINILO TALLA M', 100), ('GUANTE VINILO TALLA S', 100), ('AZUCAR', 7), ('NOVA', 2), ('SERVILLETILLA', 14), ('CUCHARILLA', 800), ('BOLSA CAMISA', 1), ('PAÑO AMARILLO', 3), ('CAFE', 0.4)
    ])

    # S03 & S02: PANADERIA and REPOSTERIA, 2026-04-03
    deliver_batch('PANADERIA', '2026-04-03', [
        ('HARINA', 100), ('HARINA INTEGRAL', 2), ('SAL ', 2), ('MANTECA', 2), ('GRASA', 1), ('LEVADURA', 1), ('ALUSA', 1), ('TRAPO', 2), ('ESPONJA', 2), ('HUEVO', 8)
    ])
    deliver_batch('REPOSTERIA', '2026-04-03', [
        ('JALEA MANZANA', 5), ('NATILLA', 9), ('HUEVO', 75), ('AZUCAR', 4), ('MANJAR', 2), ('COCO RALLADO', 0.5), ('YOGURT', 24), ('POTE GELATINA', 800)
    ])

if __name__ == "__main__":
    run()
