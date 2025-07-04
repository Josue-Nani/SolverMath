#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solverANS.settings')
django.setup()

from django.contrib.auth.models import User
from solverApp.models import Perfil

try:
    admin = User.objects.get(username='admin')
    print("=" * 50)
    print("CREDENCIALES DEL USUARIO ADMINISTRADOR")
    print("=" * 50)
    print(f"Usuario: {admin.username}")
    print(f"Email: {admin.email}")
    print(f"Nombre: {admin.first_name} {admin.last_name}")
    print(f"Es superusuario: {admin.is_superuser}")
    print(f"Es staff: {admin.is_staff}")
    print(f"Activo: {admin.is_active}")
    print(f"Fecha de registro: {admin.date_joined}")
    print(f"Último login: {admin.last_login}")
    print("=" * 50)
    print("CONTRASEÑA: admin123")
    print("=" * 50)
    
    try:
        perfil = Perfil.objects.get(user=admin)
        print("\nPERFIL ASOCIADO:")
        print(f"Nombre completo: {perfil.nombre_completo}")
        print(f"Carrera: {perfil.carrera}")
        print(f"Carnet: {perfil.carnet}")
        print(f"Ciclo: {perfil.ciclo}")
    except Perfil.DoesNotExist:
        print("\nSin perfil asociado")
    
    print("\n" + "=" * 50)
    print("PARA ACCEDER AL PANEL DE ADMINISTRACIÓN:")
    print("1. Ve a: http://127.0.0.1:8000/")
    print("2. Inicia sesión con: admin / admin123")
    print("3. Haz clic en 'Panel Admin' en el menú principal")
    print("=" * 50)
    
except User.DoesNotExist:
    print("El usuario admin no existe")
    print("Ejecuta: python manage.py create_superuser")
