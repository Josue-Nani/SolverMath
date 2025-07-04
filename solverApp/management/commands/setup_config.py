from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from solverApp.models import ConfiguracionSistema, ConfiguracionMetodo


class Command(BaseCommand):
    help = 'Configurar sistema por defecto'

    def handle(self, *args, **options):
        # Crear configuración del sistema
        config = ConfiguracionSistema.obtener_configuracion()
        self.stdout.write(self.style.SUCCESS(f'Configuración del sistema creada/actualizada: {config.nombre_sistema}'))
        
        # Crear configuraciones de métodos por defecto
        metodos_por_defecto = [
            ('newton', 'Método de Newton-Raphson'),
            ('biseccion', 'Método de Bisección'),
            ('secante', 'Método de la Secante'),
            ('punto_fijo', 'Método de Punto Fijo'),
            ('integracion', 'Integración Numérica'),
            ('derivacion', 'Derivación Numérica'),
        ]
        
        for metodo_key, metodo_name in metodos_por_defecto:
            metodo_config, created = ConfiguracionMetodo.objects.get_or_create(
                metodo=metodo_key,
                defaults={
                    'habilitado': True,
                    'limite_iteraciones': 100,
                    'precision': 0.0001,
                    'tiempo_maximo': 30,
                    'limite_uso_diario': 50,
                    'limite_uso_usuario': 10,
                    'descripcion': f'Configuración para {metodo_name}'
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Configuración creada para método: {metodo_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Configuración ya existe para método: {metodo_name}'))
        
        # Mostrar estadísticas
        total_metodos = ConfiguracionMetodo.objects.count()
        metodos_habilitados = ConfiguracionMetodo.objects.filter(habilitado=True).count()
        
        self.stdout.write(self.style.SUCCESS(f'Total de métodos configurados: {total_metodos}'))
        self.stdout.write(self.style.SUCCESS(f'Métodos habilitados: {metodos_habilitados}'))
        self.stdout.write(self.style.SUCCESS('Configuración completada exitosamente'))
