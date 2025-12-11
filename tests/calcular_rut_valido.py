#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para calcular RUTs válidos para pruebas
"""

def calcular_digito_verificador(rut_sin_dv):
    """
    Calcula el dígito verificador de un RUT chileno
    """
    rut = str(rut_sin_dv)
    reversed_rut = rut[::-1]
    secuencia = [2, 3, 4, 5, 6, 7]
    suma = 0
    
    for i, digito in enumerate(reversed_rut):
        multiplicador = secuencia[i % len(secuencia)]
        suma += int(digito) * multiplicador
    
    resto = suma % 11
    dv_calculado = 11 - resto
    
    if dv_calculado == 10:
        return "K"
    elif dv_calculado == 11:
        return "0"
    else:
        return str(dv_calculado)

def generar_ruts_validos():
    """
    Genera RUTs válidos para pruebas
    """
    print("=== RUTs Válidos para Pruebas ===")
    
    # RUTs con diferentes dígitos verificadores
    ruts_base = [
        "12345678",  # Dígito verificador: 5
        "9876543",   # Dígito verificador: 2
        "11222333",  # Dígito verificador: 6
        "55667788",  # Dígito verificador: 3
        "9999999",   # Dígito verificador: 6
    ]
    
    for rut_base in ruts_base:
        dv = calcular_digito_verificador(rut_base)
        rut_completo = f"{rut_base}-{dv}"
        print(f"RUT: {rut_completo}")
        print(f"  Con puntos: {formatear_con_puntos(rut_base, dv)}")
        print(f"  Sin formato: {rut_base}{dv}")
        print()

def formatear_con_puntos(rut, dv):
    """
    Formatea un RUT con puntos
    """
    rut_str = str(rut)
    if len(rut_str) <= 3:
        return f"{rut_str}-{dv}"
    
    # Agregar puntos cada 3 dígitos desde el final
    partes = []
    while len(rut_str) > 3:
        partes.append(rut_str[-3:])
        rut_str = rut_str[:-3]
    partes.append(rut_str)
    
    rut_formateado = ".".join(reversed(partes))
    return f"{rut_formateado}-{dv}"

if __name__ == "__main__":
    generar_ruts_validos()
    
    # Ejemplo de uso
    print("\n=== Ejemplo de RUT con dígito K ===")
    # Buscar un RUT que tenga dígito verificador K
    for i in range(10000000, 10000050):
        dv = calcular_digito_verificador(str(i))
        if dv == "K":
            print(f"RUT con dígito K: {i}-{dv}")
            print(f"Formateado: {formatear_con_puntos(str(i), dv)}")
            break