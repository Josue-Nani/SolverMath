from .models import Perfil

def user_perfil(request):
    """
    Context processor para hacer el perfil del usuario disponible en todos los templates
    """
    if request.user.is_authenticated:
        try:
            perfil = request.user.perfil
        except Perfil.DoesNotExist:
            # Crear perfil si no existe
            perfil = Perfil.objects.create(
                user=request.user,
                nombre_completo=request.user.get_full_name() or request.user.username,
                carrera='',
                carnet='',
                ciclo=''
            )
        return {'user_perfil': perfil}
    return {}
