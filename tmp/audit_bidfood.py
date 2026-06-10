import os
import sys
import django

# Setup
BASE_DIR = r'C:\Users\Coalfa\Desktop\RRHHBG\Gestios_Citas_IS'
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'san_lucas.settings') 
django.setup()

from inventario.models import Lote

def audit_bidfood():
    # Bidfood invoice 0000247236
    lotes = Lote.objects.filter(numero_guia__icontains='247236').select_related('producto')
    print(f"{'PRODUCTO':<40} | {'CANT':<5} | {'PRICE':<10} | {'TOTAL':<12}")
    print("-" * 75)
    for l in lotes:
        print(f"{l.producto.nombre[:40]:<40} | {l.cantidad:<5} | {l.precio_unitario:<10} | {l.valor_total:<12}")

if __name__ == "__main__":
    audit_bidfood()
