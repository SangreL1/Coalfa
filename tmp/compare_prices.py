import os
import sys
import django
import pandas as pd

# Setup
BASE_DIR = r'C:\Users\Coalfa\Desktop\RRHHBG\Gestios_Citas_IS'
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'san_lucas.settings') 
django.setup()

from inventario.models import Lote, Producto

def compare_baseline_prices():
    df = pd.read_excel('Planilla de invntario Marzo 26.xlsx')
    # Use col 1 as name and col 5? as price. Let's find columns correctly.
    # Looking at my previous inspect_excel.py output:
    # "LIBRO MAYOR AUXILIAR DE INVENTARIO": Product name
    # "Unnamed: 5": Unit Price (Maybe this is NET or BRUTO?)
    
    print(f"{'PRODUCTO (Excel)':<35} | {'PRICE (Excel)':<10} | {'PRICE (DB)':<10}")
    print("-" * 65)
    
    for _, row in df.iterrows():
        name_excel = str(row['LIBRO MAYOR AUXILIAR DE INVENTARIO']).strip()
        if not name_excel or name_excel == 'nan': continue
        
        price_excel = row['Unnamed: 5']
        if pd.isna(price_excel) or price_excel == 0: continue
        
        # Search in DB
        lote = Lote.objects.filter(producto__nombre=name_excel.upper(), responsable_registro='IMPORT_INVENTARIO').first()
        if lote:
            print(f"{name_excel[:35]:<35} | {price_excel:<10} | {lote.precio_unitario:<10}")

if __name__ == "__main__":
    compare_baseline_prices()
