from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Perfil

class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            'placeholder': 'correo@ejemplo.com',
            'class': 'w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-transparent backdrop-blur-sm'
        })
    )
    nombre_completo = forms.CharField(
        max_length=100,
        label="Nombre completo",
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombre completo',
            'class': 'w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-transparent backdrop-blur-sm'
        })
    )
    carrera = forms.CharField(
        max_length=100,
        label="Carrera",
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: Ingeniería en Sistemas',
            'class': 'w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-transparent backdrop-blur-sm'
        })
    )
    carnet = forms.CharField(
        max_length=20,
        label="Carnet",
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: LC12345',
            'class': 'w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-transparent backdrop-blur-sm'
        })
    )
    ciclo = forms.CharField(
        max_length=20,
        label="Ciclo",
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: II-2025',
            'class': 'w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-transparent backdrop-blur-sm'
        })
    )
    foto = forms.ImageField(
        label="Fotografía de perfil",
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white file:bg-cyan-600 file:text-white file:border-0 file:px-4 file:py-2 file:rounded-md hover:file:bg-cyan-700 focus:outline-none focus:ring-2 focus:ring-cyan-400'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2',
                  'nombre_completo', 'carrera', 'carnet', 'ciclo', 'foto']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS a los campos heredados
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-transparent backdrop-blur-sm',
            'placeholder': 'Nombre de usuario'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-transparent backdrop-blur-sm',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-transparent backdrop-blur-sm',
            'placeholder': 'Confirmar contraseña'
        })

    def save(self, commit=True):
        user = super().save(commit)
        if commit:
            user.email = self.cleaned_data['email']
            user.save()
            perfil, created = Perfil.objects.get_or_create(user=user)
            perfil.nombre_completo = self.cleaned_data['nombre_completo']
            perfil.carrera = self.cleaned_data['carrera']
            perfil.carnet = self.cleaned_data['carnet']
            perfil.ciclo = self.cleaned_data['ciclo']
            perfil.foto = self.cleaned_data.get('foto')
            perfil.save()
        return user


class LoginUsuarioForm(AuthenticationForm):
    username = forms.CharField(label='Nombre de usuario')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)

from django import forms
from .models import Perfil

class EditarPerfilForm(forms.ModelForm):
    # Campos del usuario
    username = forms.CharField(
        max_length=150,
        label="Nombre de usuario",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered input-primary w-full text-lg',
            'placeholder': 'Nombre de usuario'
        })
    )
    email = forms.EmailField(
        label="Correo electrónico",
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'input input-bordered input-primary w-full text-lg',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    
    class Meta:
        model = Perfil
        fields = ['nombre_completo', 'carrera', 'carnet', 'ciclo', 'foto']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={
                'class': 'input input-bordered input-primary w-full text-lg',
                'placeholder': 'Nombre completo'
            }),
            'carrera': forms.TextInput(attrs={
                'class': 'input input-bordered input-primary w-full text-lg',
                'placeholder': 'Carrera'
            }),
            'carnet': forms.TextInput(attrs={
                'class': 'input input-bordered input-primary w-full text-lg',
                'placeholder': 'Carnet'
            }),
            'ciclo': forms.TextInput(attrs={
                'class': 'input input-bordered input-primary w-full text-lg',
                'placeholder': 'Ciclo'
            }),
            'foto': forms.ClearableFileInput(attrs={
                'class': 'file-input file-input-bordered file-input-primary w-full'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        # Extraer el usuario del perfil
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pre-llenar campos del usuario si existe
        if self.user:
            self.fields['username'].initial = self.user.username
            self.fields['email'].initial = self.user.email
        
        # Hacer todos los campos opcionales para permitir ediciones parciales
        for field_name, field in self.fields.items():
            field.required = False
    
    def clean(self):
        cleaned_data = super().clean()
        # Verificar que al menos un campo haya sido modificado
        has_changes = False
        
        if self.instance and self.instance.pk:
            # Comparar con valores actuales del perfil
            for field_name in ['nombre_completo', 'carrera', 'carnet', 'ciclo']:
                current_value = getattr(self.instance, field_name, '')
                new_value = cleaned_data.get(field_name, '')
                if new_value and new_value != current_value:
                    has_changes = True
                    break
            
            # Verificar cambios en foto
            if cleaned_data.get('foto'):
                has_changes = True
            
            # Verificar cambios en usuario
            if self.user:
                if (cleaned_data.get('username') and cleaned_data.get('username') != self.user.username) or \
                   (cleaned_data.get('email') and cleaned_data.get('email') != self.user.email):
                    has_changes = True
        
        return cleaned_data
    
    def save(self, commit=True):
        # Guardar el perfil solo con campos que tienen valores
        perfil = super().save(commit=False)
        
        # Actualizar solo los campos que tienen valores nuevos
        for field_name in ['nombre_completo', 'carrera', 'carnet', 'ciclo']:
            value = self.cleaned_data.get(field_name)
            if value:  # Solo actualizar si hay un valor
                setattr(perfil, field_name, value)
        
        # Actualizar campos del usuario si se proporcionaron
        if self.user:
            username = self.cleaned_data.get('username')
            email = self.cleaned_data.get('email')
            
            # Solo actualizar si hay cambios
            if username and username != self.user.username:
                self.user.username = username
            if email and email != self.user.email:
                self.user.email = email
            
            if commit:
                self.user.save()
        
        if commit:
            perfil.save()
        
        return perfil
