import os
import sys
import django
from django.db.models import Sum, F

# Setup Django
BASE_DIR = r'C:\Users\Coalfa\Desktop\RRHHBG\Gestios_Citas_IS'
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'san_lucas.settings') 
django.setup()

from inventario.models import Lote

def verify():
    count = Lote.objects.count()
    total_val = Lote.objects.aggregate(total=Sum(F('cantidad') * F('precio_unitario')))['total']
    
    print(f"Total Lotes in DB: {count}")
    print(f"Total Inventory Value: ${total_val:,.2f}")
    
    # Check new suppliers
    from inventario.models import Proveedor
    new_suppliers = ["76.748.381-3", "76.286.101-1", "77.851.255-6", "6.308.725-4"]
    for rut in new_suppliers:
        p = Proveedor.objects.filter(rut=rut).first()
        if p:
            print(f"Supplier Registered: {p.nombre} ({rut})")
        else:
            print(f"MISSING Supplier: {rut}")

if __name__ == "__main__":
    verify()
