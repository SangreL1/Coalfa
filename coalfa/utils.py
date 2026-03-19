import re

def validar_rut(rut: str) -> bool:
    """ Valida matemáticamente un RUT chileno. """
    rut = rut.upper().replace("-", "").replace(".", "").replace(" ", "")
    
    if not rut or len(rut) < 2:
        return False
        
    rut_cuerpo = rut[:-1]
    dv_ingresado = rut[-1]
    
    if not rut_cuerpo.isdigit():
        return False
        
    if dv_ingresado not in "0123456789K":
        return False
        
    try:
        rut_cuerpo = int(rut_cuerpo)
    except ValueError:
        return False

    multiplo = 2
    suma = 0
    while rut_cuerpo > 0:
        suma += (rut_cuerpo % 10) * multiplo
        rut_cuerpo //= 10
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
