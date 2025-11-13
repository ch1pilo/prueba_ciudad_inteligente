from django.db import models
from seguridad.models import Bot

class Ruta(models.Model):
    nombre = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#0000FF")  
    horario=models.CharField(max_length=100)

class Bus(models.Model):
    ruta_id=models.ForeignKey(Ruta, on_delete=models.CASCADE)
    placa= models.CharField(max_length=200)
    modelo_bus=models.CharField(max_length=200)
    capacidad=models.IntegerField()
    kilometraje=models.FloatField()
    year=models.IntegerField()

class Parada(models.Model):
    ruta = models.ForeignKey(Ruta, related_name="paradas", on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    coordenada = models.CharField(max_length=200)

class AccionPasajero(models.TextChoices):
    SALIDA = 'SALIDA', 'SALIDA'
    ENTRADA = 'ENTRADA', 'ENTRADA'

class Factura(models.Model):
    bot_id=models.ForeignKey(Bot, on_delete=models.CASCADE)
    rutas_id=models.ForeignKey(Ruta, on_delete=models.CASCADE)
    parada_id=models.ForeignKey(Parada, on_delete=models.CASCADE)
    fecha=models.DateField(max_length=200)
    hora=models.CharField(max_length=200)
    accion = models.CharField(
        max_length=10,
        choices=AccionPasajero.choices,
        default=AccionPasajero.ENTRADA
    )