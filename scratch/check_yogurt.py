
import os
import sys
import django
import datetime
sys.path.append(os.getcwd())
from django.db.models import Sum

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'san_lucas.settings')
django.setup()

from inventario.models import Producto, RegistroServicio

def get_yogurt_consumption():
    hoy = datetime.datetime.now()
    hace_4_semanas = hoy - datetime.timedelta(weeks=4)
    
    productos_yogurt = Producto.objects.filter(nombre__icontains='yogurt')
    if not productos_yogurt.exists():
        print("No se encontraron productos con el nombre 'yogurt'.")
        return

    print(f"Reporte de consumo de Yogurt (desde {hace_4_semanas.date()} hasta hoy):")
    print("-" * 60)
    
    total_general = 0
    
    for p in productos_yogurt:
        consumos = RegistroServicio.objects.filter(
            lote__producto=p,
            fecha__gte=hace_4_semanas
        ).values('area').annotate(total_area=Sum('cantidad_servida')).order_by('area')
        
        print(f"Producto: {p.nombre} (ID: {p.id})")
        if not consumos:
            print("  Sin registros de consumo en este periodo.")
        else:
            p_total = 0
            for c in consumos:
                area = c['area']
                cantidad = c['total_area']
                print(f"  Area: {area:<20} | Cantidad: {cantidad:>8.2f} {p.unidad_medida}")
                p_total += cantidad
            print(f"  Total {p.nombre}: {p_total:.2f} {p.unidad_medida}")
            total_general += p_total
        print("-" * 60)

    print(f"Total general Yogurt entregado: {total_general:.2f}")

if __name__ == "__main__":
    get_yogurt_consumption()
