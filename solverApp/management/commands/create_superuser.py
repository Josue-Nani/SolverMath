from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from solverApp.models import Perfil

class Command(BaseCommand):
    help = 'Crea un superusuario administrador para el panel de administración'

    def handle(self, *args, **options):
        username = 'admin'
        email = 'admin@solverans.com'
        password = 'admin123'
        
        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'El usuario {username} ya existe')
            )
            return
        
        # Crear el superusuario
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name='Administrador',
            last_name='Sistema'
        )
        
        # Crear perfil asociado
        perfil = Perfil.objects.create(
            user=user,
            nombre_completo='Administrador del Sistema',
            carrera='Administración de Sistemas',
            carnet='ADMIN001',
            ciclo='2025'
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Superusuario {username} creado exitosamente')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Credenciales: {username} / {password}')
        )
        self.stdout.write(
            self.style.SUCCESS('Perfil asociado creado exitosamente')
        )
