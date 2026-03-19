import os
import sys
import django

sys.path.append('c:\\Users\\Coalfa\\Desktop\\RRHHBG\\Gestios_Citas_IS')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Gestios_Citas_IS.settings')

from coalfa.utils import validar_rut

test_cases = [
    ("12345678-5", True),
    ("9876543-3", True),
    ("11222333-9", True),
    ("55667788-3", True),
    ("9999999-3", True),
    ("12345678-1", False),
    ("11.111.111-2", False),
    ("12.345.678-5", True),
    ("  12345678 - 5  ", True),
    ("10000013-K", True), # Digito K valid
    ("10000013-k", True), # Digito K lowercase
    ("10000013-0", False), # Digito K invalid
]

for rut, expected in test_cases:
    result = validar_rut(rut)
    print(f"RUT: {rut} | Expected: {expected} | Got: {result} | {'PASS' if result == expected else 'FAIL'}")
