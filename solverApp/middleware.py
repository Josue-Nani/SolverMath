from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

class MaintenanceModeMiddleware:
    """Middleware para manejar el modo mantenimiento"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Permitir acceso a administradores y rutas específicas
        if (request.user.is_authenticated and request.user.is_superuser) or \
           request.path.startswith('/admin/') or \
           request.path.startswith('/static/') or \
           request.path.startswith('/media/') or \
           request.path in ['/login/', '/logout/', '/accounts/login/']:
            return self.get_response(request)
        
        # Verificar si el modo mantenimiento está activo
        try:
            from .models import ConfiguracionSistema
            config = ConfiguracionSistema.obtener_configuracion()
            
            if config.mantenimiento_activo:
                # Renderizar página de mantenimiento
                context = {
                    'titulo': config.nombre_sistema,
                    'mensaje': config.mensaje_mantenimiento,
                }
                return render(request, 'maintenance.html', context, status=503)
                
        except Exception:
            # Si hay error al acceder a la configuración, continuar normalmente
            pass
        
        return self.get_response(request)
