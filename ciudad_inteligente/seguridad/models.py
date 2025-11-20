from django.db import models
from django.contrib.auth.models import User

class SolicitudAcceso(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solicitudes')
    token = models.CharField(max_length=100, unique=True)
    creado = models.DateTimeField(auto_now_add=True)
    usado = models.BooleanField(default=False)

    def __str__(self):
        return f"Solicitud de {self.usuario.username} - Token: {self.token}"


class Generos(models.TextChoices):
    HOMBRE = 'HOMBRE', 'HOMBRE'
    MUJER = 'MUJER', 'MUJER'

class Bot(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    edad = models.IntegerField()
    cedula=models.CharField(max_length=200)
    activo = models.BooleanField(default=True)
    discapacidad=models.BooleanField(default=False)
    embarazo=models.BooleanField(default=False)
    suscripcion = models.BooleanField(default=True)
    genero = models.CharField(
        max_length=10,
        choices=Generos.choices,
    )  
        
class TipoUsuario(models.TextChoices):
    ADMIN = 'ADMIN', 'Administrador'
    COMUN = 'COMUN', 'Común'

class UsuariosDatosPersonales(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre=models.CharField(max_length=200)
    apellido=models.CharField(max_length=200)
    cedula=models.CharField(max_length=200)
    estatus = models.BooleanField(default=True)
    avatar = models.CharField(max_length=50)
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TipoUsuario.choices,
        default=TipoUsuario.COMUN
    )

class UsuarioRostro(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    foto = models.ImageField(upload_to='faces_db/')
    nombre_archivo = models.CharField(max_length=100, blank=True)



