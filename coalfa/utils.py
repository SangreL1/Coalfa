import re
from django.core.exceptions import ValidationError

def validar_rut(rut: str) -> bool:
    """
    Valida matemáticamente un RUT chileno.
    Acepta formatos:
    - 12.345.678-9
    - 12345678-9
    - 123456789
    """
    if not rut:
        return False
        
    # Limpiar el RUT de puntos, guiones y espacios
    rut = str(rut).upper().replace(".", "").replace("-", "").replace(" ", "")
    
    if not re.match(r"^\d{7,8}[0-9K]$", rut):
        return False
        
    rut_cuerpo = rut[:-1]
    dv_ingresado = rut[-1]
    
    multiplo = 2
    suma = 0
    for d in reversed(rut_cuerpo):
        suma += int(d) * multiplo
        multiplo += 1
        if multiplo == 8:
            multiplo = 2
            
    resto = suma % 11
    dv_esperado = 11 - resto
    
    if dv_esperado == 11:
        dv_calculado = "0"
    elif dv_esperado == 10:
        dv_calculado = "K"
    else:
        dv_calculado = str(dv_esperado)
        
    return dv_calculado == dv_ingresado

def rut_validator(value):
    """Validator function for Django models/forms."""
    if not validar_rut(value):
        raise ValidationError("El RUT ingresado no es válido.")
