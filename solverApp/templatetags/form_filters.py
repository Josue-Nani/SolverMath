# filepath: c:\Users\User\OneDrive\Desktop\UES-2025\Python-2025\proyecto-nuevo\proyecto-nuevo\solverApp\templatetags\form_filters.py
from django import template
import os

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    """
    Añade clases CSS a un campo de formulario de Django
    """
    try:
        # Verificar si el objeto tiene el método as_widget (es un campo de formulario)
        if hasattr(field, 'as_widget') and callable(getattr(field, 'as_widget')):
            return field.as_widget(attrs={"class": css})
        elif hasattr(field, 'widget'):
            # Alternativa para campos de formulario
            field.widget.attrs.update({'class': css})
            return field
        else:
            # Si no es un campo de formulario, devolver tal como está
            return field
    except (AttributeError, TypeError) as e:
        # En caso de cualquier error, devolver el campo sin modificar
        print(f"Error en add_class filter: {e}")
        return field

@register.filter(name='basename')
def basename(value):
    """
    Obtiene el nombre base de un archivo (sin la ruta)
    """
    try:
        return os.path.basename(str(value))
    except:
        return value