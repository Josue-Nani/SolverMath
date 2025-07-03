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
