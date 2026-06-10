import os
import sys
import django
from django.db.models import Sum

BASE_DIR = r'C:\Users\Coalfa\Desktop\RRHHBG\Gestios_Citas_IS'
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'san_lucas.settings') 
django.setup()

from inventario.models import Lote

stocks = (
    Lote.objects.filter(estado='ACTIVO', ubicacion_actual='BODEGA')
    .values('producto__nombre')
    .annotate(total=Sum('cantidad'))
    .order_by('producto__nombre')
)

for s in stocks:
    print(f"{s['producto__nombre']}: {s['total']}")
