#!/usr/bin/env python3
"""
Script de prueba para verificar las mejoras en Newton-Raphson
"""

import sys
import os
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solverANS.settings')
django.setup()

from solverApp.metodos.newton import newton_raphson

def test_newton_raphson():
    """
    Pruebas del método Newton-Raphson mejorado
    """
    
    print("=== PRUEBAS DEL MÉTODO NEWTON-RAPHSON MEJORADO ===\n")
    
    # Caso 1: Función simple con convergencia rápida
    print("1. Función: x**2 - 4, x0 = 3 (debería converger a 2)")
    resultado, error, pasos = newton_raphson("x**2 - 4", 3, 1e-6)
    print(f"   Resultado: {resultado}")
    print(f"   Error: {error}")
    print(f"   Iteraciones: {len(pasos)}")
    print()
    
    # Caso 2: Función con raíz en el origen
    print("2. Función: x**3, x0 = 1 (debería converger a 0)")
    resultado, error, pasos = newton_raphson("x**3", 1, 1e-6)
    print(f"   Resultado: {resultado}")
    print(f"   Error: {error}")
    print(f"   Iteraciones: {len(pasos)}")
    print()
    
    # Caso 3: Función exponencial
    print("3. Función: exp(x) - 2, x0 = 0 (debería converger a ln(2) ≈ 0.693)")
    resultado, error, pasos = newton_raphson("exp(x) - 2", 0, 1e-6)
    print(f"   Resultado: {resultado}")
    print(f"   Error: {error}")
    print(f"   Iteraciones: {len(pasos)}")
    print()
    
    # Caso 4: Función trigonométrica
    print("4. Función: sin(x), x0 = 1 (debería converger a 0)")
    resultado, error, pasos = newton_raphson("sin(x)", 1, 1e-6)
    print(f"   Resultado: {resultado}")
    print(f"   Error: {error}")
    print(f"   Iteraciones: {len(pasos)}")
    print()
    
    # Caso 5: Función problemática (derivada pequeña)
    print("5. Función: x**2 - 2*x + 1, x0 = 0.5 (f'(x) puede ser pequeña)")
    resultado, error, pasos = newton_raphson("x**2 - 2*x + 1", 0.5, 1e-6)
    print(f"   Resultado: {resultado}")
    print(f"   Error: {error}")
    print(f"   Iteraciones: {len(pasos)}")
    print()
    
    # Caso 6: Función con múltiples raíces
    print("6. Función: x**3 - 6*x**2 + 11*x - 6, x0 = 0 (raíces en 1, 2, 3)")
    resultado, error, pasos = newton_raphson("x**3 - 6*x**2 + 11*x - 6", 0, 1e-6)
    print(f"   Resultado: {resultado}")
    print(f"   Error: {error}")
    print(f"   Iteraciones: {len(pasos)}")
    print()
    
    # Caso 7: Función con punto inicial problemático
    print("7. Función: x**2 - 4, x0 = 0 (derivada = 0 en x0)")
    resultado, error, pasos = newton_raphson("x**2 - 4", 0, 1e-6)
    print(f"   Resultado: {resultado}")
    print(f"   Error: {error}")
    print(f"   Iteraciones: {len(pasos)}")
    print()

if __name__ == "__main__":
    test_newton_raphson()
