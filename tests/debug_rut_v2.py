#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def calcular_digito_verificador(rut):
    """
    Calcula el dígito verificador de un RUT chileno
    """
    # Eliminar puntos y guiones
    rut = rut.replace(".", "").replace("-", "")

    # Invertir el RUT
    reversed_rut = rut[::-1]

    print(f"RUT original: {rut}")
    print(f"RUT invertido: {reversed_rut}")

    secuencia = [2, 3, 4, 5, 6, 7]  # Secuencia de multiplicadores
    suma = 0

    for i, digito in enumerate(reversed_rut):
        multiplicador = secuencia[i % len(secuencia)]  # Ciclar entre 2 y 7
        producto = int(digito) * multiplicador
        print(f"Digito: {digito}, Multiplicador: {multiplicador}, Producto: {producto}")
        suma += producto

    print(f"Suma: {suma}")

    resto = suma % 11
    print(f"Resto: {resto}")

    dv = 11 - resto
    print(f"Dígito verificador calculado: {dv}")

    if dv == 10:
        return "K"
    elif dv == 11:
        return "0"
    else:
        return str(dv)


# Probar con un RUT conocido como válido
print("=== Prueba con RUT 7608644 ===")
rut_prueba = "7608644"
dv_calculado = calcular_digito_verificador(rut_prueba)
print(f"El dígito verificador calculado para {rut_prueba} es: {dv_calculado}")

print("\n=== Prueba con RUT 12345678 ===")
rut_prueba2 = "12345678"
dv_calculado2 = calcular_digito_verificador(rut_prueba2)
print(f"El dígito verificador calculado para {rut_prueba2} es: {dv_calculado2}")
