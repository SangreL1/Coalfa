#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Archivo de prueba para validar la función de validación de RUT chileno
"""

import sys
import os

# Agregar el directorio padre al path para importar módulos del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Gestios_Citas_IS.settings')

try:
    import django
    django.setup()
except ImportError as e:
    print(f"Error al importar Django: {e}")
    print("Asegúrate de tener Django instalado y el entorno configurado correctamente.")
    sys.exit(1)


def test_validar_rut_chileno():
    """
    Prueba la función validar_rut_chileno con diferentes formatos de entrada
    """
    # Importar la función de validación dentro de la función para evitar problemas de importación
    from Agenda.models import validar_rut_chileno
    from django.core.exceptions import ValidationError

    print("Probando la función validar_rut_chileno...")

    # Casos válidos (RUTs reales con dígito verificador correcto)
    casos_validos = [
        "12345678-5",        # Formato estándar
        "12.345.678-5",      # Con puntos
        "123456785",         # Sin guion
        "10.000.013-K",      # Con dígito K mayúscula y puntos
        "10000013-k",        # Con dígito k minúscula
        "9876543-3",         # RUT corto
        "9.876.543-3",       # RUT corto con puntos
        "11222333-9",        # RUT largo
        "11.222.333-9",      # RUT largo con puntos
    ]

    # Casos inválidos
    casos_invalidos = [
        "12345678-0",  # RUT con dígito verificador incorrecto
        "12345678-25",  # Dígito verificador no válido
        "abc12345-k",  # Contiene letras en el cuerpo
        "1234567-k",  # Cuerpo demasiado corto
        "",  # Vacío
        "123",  # Muy corto
        "12345678",  # Sin dígito verificador
        "1234567812",  # Demasiados dígitos
        "12345678-A",  # Letra inválida como dígito verificador
    ]

    print("\n--- Pruebas de RUTs válidos ---")
    for rut in casos_validos:
        try:
            resultado = validar_rut_chileno(rut)
            print(f"✓ {rut} -> {resultado}")
        except ValidationError as e:
            print(f"✗ {rut} -> Error: {e.message}")

    print("\n--- Pruebas de RUTs inválidos ---")
    for rut in casos_invalidos:
        try:
            resultado = validar_rut_chileno(rut)
            print(f"✗ {rut} -> {resultado} (DEBERÍA SER INVÁLIDO)")
        except ValidationError as e:
            print(f"✓ {rut} -> Error: {e.message} (correcto)")

    print("\nPruebas completadas.")


if __name__ == "__main__":
    import os
    import sys
    import django

    # Configurar Django
    sys.path.append(
        "/home/erick/Documentos/inacap/ingenieria de software/Gestios_Citas_IS"
    )
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Gestios_Citas_IS.settings")
    django.setup()

    test_validar_rut_chileno()
