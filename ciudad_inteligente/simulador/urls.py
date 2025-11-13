from django.urls import path
from simulador import views
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = router.urls

urlpatterns = [
    path('simulador', views.simuladorInicio, name="simula"),
]