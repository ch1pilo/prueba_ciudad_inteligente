from django.urls import path
from simulador import views

urlpatterns = [
    path('simulador/', views.simuladorInicio, name="simula"),
    path('api/registrar-factura/', views.registrar_factura_api, name='api_registrar_factura'),
    path('rutas/', views.visionRutas, name='rutas'),
]