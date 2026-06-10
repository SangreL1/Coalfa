import os
import sys
import django
from django.db.models import Count

BASE_DIR = r'C:\Users\Coalfa\Desktop\RRHHBG\Gestios_Citas_IS'
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'san_lucas.settings') 
django.setup()

from inventario.models import RegistroServicio

res = RegistroServicio.objects.values('area').annotate(cnt=Count('id')).order_by('area')
print("AREA | COUNT")
print("-" * 20)
for r in res:
    print(f"{r['area']} | {r['cnt']}")
