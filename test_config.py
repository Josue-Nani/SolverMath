#!/usr/bin/env python
"""
Script para probar la configuración de métodos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solverANS.settings')
django.setup()

from solverApp.models import ConfiguracionMetodo

def test_metodo_config():
    """Probar la configuración de métodos"""
    
    print("=== ESTADO ACTUAL DE CONFIGURACIÓN DE MÉTODOS ===")
    
    metodos = ConfiguracionMetodo.objects.all()
    
    for metodo in metodos:
        print(f"\n--- {metodo.get_metodo_display()} ---")
        print(f"Habilitado: {metodo.habilitado}")
        print(f"Límite iteraciones: {metodo.limite_iteraciones}")
        print(f"Precisión: {metodo.precision}")
        print(f"Tiempo máximo: {metodo.tiempo_maximo}")
        print(f"Uso diario: {metodo.limite_uso_diario}")
        print(f"Última actualización: {metodo.fecha_actualizacion}")
        print("-" * 50)
    
    print(f"\nTotal de métodos: {metodos.count()}")
    print(f"Métodos habilitados: {metodos.filter(habilitado=True).count()}")
    print(f"Métodos deshabilitados: {metodos.filter(habilitado=False).count()}")
    
    # Test de actualización
    print("\n=== PRUEBA DE ACTUALIZACIÓN ===")
    
    # Deshabilitar método Newton
    newton_config = ConfiguracionMetodo.objects.get(metodo='newton')
    estado_anterior = newton_config.habilitado
    newton_config.habilitado = False
    newton_config.save()
    
    print(f"Newton - Estado anterior: {estado_anterior}")
    print(f"Newton - Estado actual: {newton_config.habilitado}")
    
    # Verificar que se guardó
    newton_verificado = ConfiguracionMetodo.objects.get(metodo='newton')
    print(f"Newton - Verificado desde BD: {newton_verificado.habilitado}")
    
    # Restaurar estado
    newton_config.habilitado = estado_anterior
    newton_config.save()
    
    print(f"Newton - Estado restaurado: {newton_config.habilitado}")
    
    print("\n=== PRUEBA COMPLETADA ===")

if __name__ == "__main__":
    test_metodo_config()
