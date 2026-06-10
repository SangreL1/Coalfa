import os
import sys
import django
from django.db.models import F, Sum

# Setup Django
BASE_DIR = r'C:\Users\Coalfa\Desktop\RRHHBG\Gestios_Citas_IS'
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'san_lucas.settings') 
django.setup()

from inventario.models import Lote

def detail():
    lotes = Lote.objects.filter(estado='ACTIVO').annotate(val=F('cantidad') * F('precio_unitario')).order_by('-fecha_recepcion')[:30]
    print(f"{'FECHA':<12} | {'DOCUMENTO':<12} | {'PRODUCTO':<40} | {'VALOR':>12}")
    print("-" * 85)
    for l in lotes:
        print(f"{str(l.fecha_recepcion):<12} | {l.numero_guia:<12} | {l.producto.nombre[:40]:<40} | ${l.val:>12,.2f}")

if __name__ == "__main__":
    detail()
