from functools import wraps
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime, date
from .models import ConfiguracionSistema, ConfiguracionMetodo, LimiteUso, HistorialOperacion

def verificar_limite_uso(metodo):
    """
    Decorador para verificar los límites de uso de un método específico
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            try:
                # Obtener configuración del sistema y método
                config_sistema = ConfiguracionSistema.obtener_configuracion()
                config_metodo = ConfiguracionMetodo.objects.get(metodo=metodo)
                
                # Verificar si el método está habilitado
                if not config_metodo.habilitado:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False, 
                            'error': f'El método {config_metodo.get_metodo_display()} está deshabilitado temporalmente'
                        })
                    messages.error(request, f'El método {config_metodo.get_metodo_display()} está deshabilitado temporalmente')
                    return redirect('home')
                
                # Verificar límite general de operaciones por usuario
                operaciones_usuario = HistorialOperacion.objects.filter(usuario=request.user).count()
                if operaciones_usuario >= config_sistema.limite_operaciones_usuario:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False, 
                            'error': f'Has alcanzado el límite de {config_sistema.limite_operaciones_usuario} operaciones por usuario'
                        })
                    messages.error(request, f'Has alcanzado el límite de {config_sistema.limite_operaciones_usuario} operaciones por usuario')
                    return redirect('home')
                
                # Verificar límite diario del método
                hoy = date.today()
                limite_uso, created = LimiteUso.objects.get_or_create(
                    usuario=request.user,
                    metodo=metodo,
                    fecha=hoy,
                    defaults={'contador': 0}
                )
                
                if limite_uso.contador >= config_metodo.limite_uso_diario:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False, 
                            'error': f'Has alcanzado el límite diario de {config_metodo.limite_uso_diario} usos para {config_metodo.get_metodo_display()}'
                        })
                    messages.error(request, f'Has alcanzado el límite diario de {config_metodo.limite_uso_diario} usos para {config_metodo.get_metodo_display()}')
                    return redirect('home')
                
                # Incrementar contador de uso
                limite_uso.contador += 1
                limite_uso.save()
                
                # Agregar configuraciones al request para uso en la vista
                request.config_sistema = config_sistema
                request.config_metodo = config_metodo
                
                return view_func(request, *args, **kwargs)
                
            except ConfiguracionMetodo.DoesNotExist:
                # Si no existe configuración para el método, crear una por defecto
                ConfiguracionMetodo.objects.create(
                    metodo=metodo,
                    habilitado=True,
                    limite_iteraciones=100,
                    precision=0.0001,
                    tiempo_maximo=30,
                    limite_uso_diario=50,
                    limite_uso_usuario=10
                )
                return view_func(request, *args, **kwargs)
                
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False, 
                        'error': f'Error al verificar límites: {str(e)}'
                    })
                messages.error(request, f'Error al verificar límites: {str(e)}')
                return redirect('home')
        
        return wrapper
    return decorator


def requiere_configuracion_email(view_func):
    """
    Decorador para verificar que el email esté configurado antes de enviar notificaciones
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            config = ConfiguracionSistema.obtener_configuracion()
            if not config.email_habilitado or not config.smtp_host:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False, 
                        'error': 'El sistema de email no está configurado'
                    })
                messages.warning(request, 'El sistema de email no está configurado')
                return redirect('admin_config')
            
            request.config_email = config
            return view_func(request, *args, **kwargs)
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False, 
                    'error': f'Error en configuración de email: {str(e)}'
                })
            messages.error(request, f'Error en configuración de email: {str(e)}')
            return redirect('home')
    
    return wrapper


def es_superusuario_o_staff(user):
    """
    Función auxiliar para verificar si el usuario es superusuario o staff
    """
    return user.is_authenticated and (user.is_superuser or user.is_staff)
