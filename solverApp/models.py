from django.db import models
from django.contrib.auth.models import User

class HistorialOperacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    metodo = models.CharField(max_length=100)  # Ej: 'Newton-Raphson'
    expresion = models.TextField(blank=True, null=True)
    datos_entrada = models.TextField(null=True, blank=True)
    resultado = models.TextField()
    parametros = models.JSONField(blank=True, null=True)  # Guarda valores como x0, tolerancia, n, etc.
    tabla = models.TextField(null=True, blank=True)  # Tabla HTML o texto plano del procedimiento
    iteraciones = models.PositiveIntegerField(null=True, blank=True)  # NUEVO: para saber cuántas iteraciones hubo
    pasos = models.TextField(null=True, blank=True)  # NUEVO: para guardar el paso a paso como string o JSON
    fecha = models.DateTimeField(auto_now_add=True)
    grafica = models.TextField(null=True, blank=True) 

    def __str__(self):
        return f"{self.usuario.username} - {self.metodo} - {self.fecha:%Y-%m-%d %H:%M}"


class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre_completo = models.CharField(max_length=100)
    carrera = models.CharField(max_length=100)
    carnet = models.CharField(max_length=20)
    ciclo = models.CharField(max_length=20)
    foto = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)

    def __str__(self):
        return self.user.username


class ConfiguracionSistema(models.Model):
    """Modelo para almacenar la configuración del sistema"""
    # Configuración General
    nombre_sistema = models.CharField(max_length=100, default='SolverApp')
    descripcion_sistema = models.TextField(default='Sistema de resolución de ecuaciones')
    mantenimiento_activo = models.BooleanField(default=False)
    mensaje_mantenimiento = models.TextField(default='El sistema está en mantenimiento. Intente más tarde.')
    
    # Límites de uso
    limite_operaciones_usuario = models.IntegerField(default=100)
    limite_operaciones_dia = models.IntegerField(default=1000)
    limite_tiempo_sesion = models.IntegerField(default=3600)  # segundos
    
    # Configuración de email
    email_habilitado = models.BooleanField(default=False)
    smtp_host = models.CharField(max_length=100, blank=True)
    smtp_port = models.IntegerField(default=587)
    smtp_usuario = models.CharField(max_length=100, blank=True)
    smtp_password = models.CharField(max_length=100, blank=True)
    smtp_tls = models.BooleanField(default=True)
    
    # Configuración de notificaciones
    notificaciones_admin = models.BooleanField(default=True)
    notificaciones_usuario = models.BooleanField(default=True)
    
    # Configuración de seguridad
    intentos_login_max = models.IntegerField(default=5)
    tiempo_bloqueo_login = models.IntegerField(default=300)  # segundos
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Configuración del Sistema'
        verbose_name_plural = 'Configuraciones del Sistema'
    
    def __str__(self):
        return f"Configuración - {self.nombre_sistema}"
    
    @classmethod
    def obtener_configuracion(cls):
        """Obtiene la configuración actual del sistema"""
        config, created = cls.objects.get_or_create(id=1)
        return config


class ConfiguracionMetodo(models.Model):
    """Modelo para configurar métodos de resolución"""
    METODOS_CHOICES = [
        ('newton', 'Método de Newton-Raphson'),
        ('biseccion', 'Método de Bisección'),
        ('secante', 'Método de la Secante'),
        ('punto_fijo', 'Método de Punto Fijo'),
        ('integracion', 'Integración Numérica'),
        ('derivacion', 'Derivación Numérica'),
    ]
    
    metodo = models.CharField(max_length=50, choices=METODOS_CHOICES, unique=True)
    habilitado = models.BooleanField(default=True)
    limite_iteraciones = models.IntegerField(default=100)
    precision = models.FloatField(default=0.0001)
    tiempo_maximo = models.IntegerField(default=30)  # segundos
    
    # Límites por usuario
    limite_uso_diario = models.IntegerField(default=50)
    limite_uso_usuario = models.IntegerField(default=10)
    
    descripcion = models.TextField(blank=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Configuración de Método'
        verbose_name_plural = 'Configuraciones de Métodos'
    
    def __str__(self):
        return f"{self.get_metodo_display()} - {'Habilitado' if self.habilitado else 'Deshabilitado'}"


class LimiteUso(models.Model):
    """Modelo para rastrear el uso de los métodos por usuario"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='limites_uso')
    metodo = models.CharField(max_length=50)
    fecha = models.DateField(auto_now_add=True)
    contador = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['usuario', 'metodo', 'fecha']
        verbose_name = 'Límite de Uso'
        verbose_name_plural = 'Límites de Uso'
    
    def __str__(self):
        return f"{self.usuario.username} - {self.metodo} - {self.fecha}"
