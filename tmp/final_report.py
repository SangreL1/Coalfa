import os
import sys
import django
from django.db.models import Sum, Count

BASE_DIR = r'C:\Users\Coalfa\Desktop\RRHHBG\Gestios_Citas_IS'
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'san_lucas.settings') 
django.setup()

from inventario.models import RegistroServicio

report = (
    RegistroServicio.objects.filter(responsable='Carga Automatizada AI')
    .values('area')
    .annotate(num=Count('id'), cost=Sum('costo_total'))
    .order_by('-cost')
)

print(f"{'AREA':<20} | {'DELIVERIES':<10} | {'TOTAL COST':>12}")
print("-" * 50)
for r in report:
    print(f"{r['area']:<20} | {r['num']:<10} | ${r['cost']:>12,.2f}")
