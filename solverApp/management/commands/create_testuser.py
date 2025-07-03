from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from solverApp.models import Perfil

class Command(BaseCommand):
    help = 'Crea un usuario de prueba para el login'

    def handle(self, *args, **options):
        # Datos del usuario de prueba
        username = 'testuser'
        password = 'testpass123'
        email = 'test@example.com'
        
        # Comprobar si ya existe
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'El usuario {username} ya existe'))
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Contraseña actualizada para el usuario {username}'))
        else:
            # Crear usuario
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f'Usuario {username} creado con éxito'))
            
            # Crear perfil
            perfil, created = Perfil.objects.get_or_create(
                user=user,
                defaults={
                    'nombre_completo': 'Usuario de Prueba',
                    'carrera': 'Ingeniería de Pruebas',
                    'carnet': 'TP12345',
                    'ciclo': 'I-2025',
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Perfil creado para el usuario {username}'))
            else:
                self.stdout.write(self.style.WARNING(f'El perfil ya existía para {username}'))

        # Mostrar credenciales para facilitar pruebas
        self.stdout.write(self.style.SUCCESS(
            f'\nCredenciales de prueba:\n'
            f'  Usuario: {username}\n'
            f'  Contraseña: {password}\n'
        ))
