import os
import sys
import django
import pandas as pd
import json

# Setup
BASE_DIR = r'C:\Users\Coalfa\Desktop\RRHHBG\Gestios_Citas_IS'
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'san_lucas.settings') 
django.setup()

from inventario.models import Lote, Producto, RegistroServicio

def audit():
    # 1. Check Apr 6 Consumption
    print("--- CONSUMO ABRIL 6 ---")
    consumos = RegistroServicio.objects.filter(fecha__date='2026-04-06').select_related('lote', 'lote__producto')
    for c in consumos:
        print(f"[{c.area}] {c.lote.producto.nombre}: {c.cantidad_servida} {c.lote.producto.unidad_medida} (Lote: {c.lote.numero_lote})")

    # 2. Check Prices of some recent Lotes
    print("\n--- PRECIOS LOTES RECIENTES (Facturas 094388184, 12121, etc) ---")
    lotes = Lote.objects.filter(numero_guia__in=['094388184', '12121', '12125', '38218775', '38218776']).select_related('producto')
    for l in lotes:
        print(f"Doc: {l.numero_guia} | {l.producto.nombre}: Cant: {l.cantidad} Up: {l.precio_unitario} Total: {l.valor_total}")

if __name__ == "__main__":
    audit()
