import os
import sys
import django
sys.path.append(r'C:\Users\Coalfa\Desktop\RRHHBG\Gestios_Citas_IS')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'san_lucas.settings') 
django.setup()

from inventario.models import Lote
from django.db.models import F, Sum
from django.core.cache import cache

total = Lote.objects.filter(estado='ACTIVO').aggregate(total_val=Sum(F('cantidad') * F('precio_unitario')))['total_val']
print(f'DB_TOTAL: {total}')

cached = cache.get('dashboard_inv_kpis')
if cached:
    print(f'CACHED_TOTAL: {cached.get("valor_total")}')
    print(f'LAST_CACHE_TIME: {cached.get("hoy")}')
else:
    print('CACHED_TOTAL: None')
