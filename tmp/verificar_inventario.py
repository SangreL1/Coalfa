import os, sys
sys.path.insert(0, r'c:\Users\Coalfa\Desktop\Gestios_Citas_IS')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Gestios_Citas_IS.settings')
import django; django.setup()

from inventario.models import Producto, Lote
from django.db.models import Count

print('=== RESUMEN BD ===')
print('Productos total:', Producto.objects.count())
print('Lotes ACTIVOS :', Lote.objects.filter(estado='ACTIVO').count())
print()
print('=== POR CATEGORIA ===')
for cat in Producto.objects.values('categoria').annotate(n=Count('id')).order_by('-n'):
    print(f"  {cat['categoria']:15s}: {cat['n']} productos")
print()
print('=== MUESTRA (primeros 5 productos) ===')
for p in Producto.objects.all()[:5]:
    stock = sum(l.cantidad for l in p.lotes.filter(estado='ACTIVO'))
    print(f"  [{p.categoria}] {p.nombre} | {p.unidad_medida} | stock: {stock}")
