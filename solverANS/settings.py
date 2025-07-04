import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-f&f@(k)6do)j^@2ms2!=ob$woej4045)-298ij+^c4)@u@huh+'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'solverApp',  # Tu app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'solverApp.middleware.MaintenanceModeMiddleware',
]

ROOT_URLCONF = 'solverANS.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',  # (opcional para imágenes)
                'solverApp.context_processors.user_perfil',  # Context processor para el perfil
            ],
        },
    },
]

WSGI_APPLICATION = 'solverANS.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'es-ES'
TIME_ZONE = 'America/El_Salvador'

USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'solverApp' / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# === Archivos de imagen y multimedia (como fotos de perfil) ===
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración de autenticación
LOGIN_URL = '/login/'                 # URL para redirigir cuando se necesita login
LOGIN_REDIRECT_URL = '/'              # URL para redirigir después de un login exitoso
LOGOUT_REDIRECT_URL = '/login/'       # URL para redirigir después de un logout

# Usar el backend de sesiones por defecto (base de datos)
SESSION_COOKIE_AGE = 86400  # 24 horas
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Mantener la sesión entre cierres de navegador para pruebas
SESSION_SAVE_EVERY_REQUEST = True  # Guardar la sesión en cada solicitud
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Usar base de datos para sesiones
SESSION_COOKIE_SECURE = False  # Permitir cookies sin HTTPS durante desarrollo
