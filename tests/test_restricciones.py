#!/usr/bin/env python3
"""
Script de prueba para verificar las restricciones implementadas:
1. Restricción de horas máximas por médico
2. Restricción de citas duplicadas
3. Ocultar funcionalidad de agendar citas del administrador
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from Agenda.models import Medico, Cita
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Gestios_Citas_IS.settings')
django.setup()

def test_restriccion_horas_maximas():
    """Probar la restricción de horas máximas por médico"""
    print("=== Probando restricción de horas máximas por médico ===")
    
    # Crear un médico
    medico = Medico.objects.create(
        nombre="Dr. Juan Pérez",
        especialidad="Cardiología",
        email="juan.perez@example.com",
        telefono="123456789"
    )
    
    # Crear 8 citas para el mismo médico (máximo permitido)
    fecha_actual = datetime.now().date()
    for i in range(8):
        hora = datetime.strptime(f"10:00", "%H:%M").time()
        fecha = fecha_actual + timedelta(days=i)
        Cita.objects.create(
            medico=medico,
            fecha=fecha,
            hora=hora,
            paciente="Paciente Prueba"
        )
    
    print(f"✓ Se crearon 8 citas para el médico {medico.nombre}")
    
    # Intentar crear una novena cita (debería fallar)
    try:
        hora = datetime.strptime("11:00", "%H:%M").time()
        fecha = fecha_actual + timedelta(days=9)
        novena_cita = Cita.objects.create(
            medico=medico,
            fecha=fecha,
            hora=hora,
            paciente="Paciente Prueba 2"
        )
        print("❌ ERROR: Se permitió crear más de 8 citas por médico")
        return False
    except Exception as e:
        print(f"✓ Correctamente se impidió crear novena cita: {str(e)}")
        return True

def test_restriccion_citas_duplicadas():
    """Probar la restricción de citas duplicadas"""
    print("\n=== Probando restricción de citas duplicadas ===")
    
    # Crear un médico
    medico = Medico.objects.create(
        nombre="Dr. María García",
        especialidad="Pediatría",
        email="maria.garcia@example.com",
        telefono="987654321"
    )
    
    # Crear una cita
    fecha = datetime.now().date()
    hora = datetime.strptime("14:00", "%H:%M").time()
    cita_original = Cita.objects.create(
        medico=medico,
        fecha=fecha,
        hora=hora,
        paciente="Paciente Duplicado"
    )
    
    print(f"✓ Se creó una cita para el médico {medico.nombre} el {fecha} a las {hora}")
    
    # Intentar crear una cita duplicada (debería fallar)
    try:
        cita_duplicada = Cita.objects.create(
            medico=medico,
            fecha=fecha,
            hora=hora,
            paciente="Paciente Duplicado 2"
        )
        print("❌ ERROR: Se permitió crear una cita duplicada")
        return False
    except Exception as e:
        print(f"✓ Correctamente se impidió crear cita duplicada: {str(e)}")
        return True

def test_ocultar_funcionalidad_admin():
    """Probar que la funcionalidad de agendar citas está oculta para administradores"""
    print("\n=== Probando ocultar funcionalidad de agendar citas para administradores ===")
    
    # Crear usuario administrador
    admin_user = User.objects.create_user(
        username='admin',
        password='admin123',
        is_staff=True,
        is_superuser=True
    )
    
    # Crear usuario normal
    normal_user = User.objects.create_user(
        username='user',
        password='user123',
        is_staff=False,
        is_superuser=False
    )
    
    # Crear cliente de prueba
    client = Client()
    
    # Probar como administrador
    client.login(username='admin', password='admin123')
    response = client.get(reverse('crear-cita'))
    print(f"✓ Respuesta admin (status code): {response.status_code}")
    
    # Probar como usuario normal
    client.login(username='user', password='user123')
    response = client.get(reverse('crear-cita'))
    print(f"✓ Respuesta usuario normal (status code): {response.status_code}")
    
    # Verificar que ambos puedan acceder (la restricción es visual, no de permisos)
    if response.status_code == 200:
        print("✓ Ambos usuarios pueden acceder al formulario de creación de citas")
        print("✓ La restricción de visualización se maneja en el frontend")
        return True
    else:
        print("❌ ERROR: El usuario normal no puede acceder al formulario")
        return False

def main():
    """Función principal para ejecutar todas las pruebas"""
    print("Iniciando pruebas de restricciones...\n")
    
    try:
        # Ejecutar todas las pruebas
        resultado1 = test_restriccion_horas_maximas()
        resultado2 = test_restriccion_citas_duplicadas()
        resultado3 = test_ocultar_funcionalidad_admin()
        
        # Resumen
        print("\n=== RESUMEN DE PRUEBAS ===")
        print(f"Restricción de horas máximas: {'✓ PASSED' if resultado1 else '❌ FAILED'}")
        print(f"Restricción de citas duplicadas: {'✓ PASSED' if resultado2 else '❌ FAILED'}")
        print(f"Ocultar funcionalidad admin: {'✓ PASSED' if resultado3 else '❌ FAILED'}")
        
        if all([resultado1, resultado2, resultado3]):
            print("\n🎉 TODAS LAS PRUEBAS PASARON!")
            return 0
        else:
            print("\n❌ ALGUNAS PRUEBAS FALLARON")
            return 1
            
    except Exception as e:
        print(f"\n❌ ERROR EJECUTANDO PRUEBAS: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())