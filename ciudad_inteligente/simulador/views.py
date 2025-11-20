from django.shortcuts import render
from simulador import models
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from seguridad.models import Bot

@login_required
def simuladorInicio(request):
    
    try:
        pasajeros_data = list(Bot.objects.filter(activo=True).values(
            'id', 'nombre', 'apellido', 'cedula', 'suscripcion'
        ))
    except Exception as e:
        print(f"Error bots: {e}")
        pasajeros_data = []


    try:
        rutas_data = list(models.Ruta.objects.values(
            'id', 'nombre', 'color', 'horario'
        ))
    except Exception as e:
        print(f"Error rutas: {e}")
        rutas_data = []

    try:
        buses_data = list(models.Bus.objects.values(
            'id', 'placa', 'capacidad', 'ruta_id'
        ))
    except Exception as e:
        print(f"Error buses: {e}")
        buses_data = []

    try:
        paradas_data = list(models.Parada.objects.values(
            'id', 
            'nombre', 
            'ruta_id',
            'coordenada'  
        ))
    except Exception as e:
        print(f"Error paradas: {e}")
        paradas_data = []


    context = {
        'pasajeros_json': pasajeros_data,
        'rutas_json': rutas_data,
        'buses_json': buses_data,
        'paradas_json': paradas_data, 
    }
    
    return render(request, 'simulacion.html', context)


def visionRutas(request):
    return render(request, 'visionRuta.html')

@require_POST 
@csrf_exempt   
def registrar_factura_api(request):

    try:
        
        data = json.loads(request.body)
        
        bot_id = data.get('bot_id')
        rutas_id = data.get('rutas_id')
        parada_id = data.get('parada_id')
        accion = data.get('accion')

        bot = Bot.objects.get(pk=bot_id)
        ruta = models.Ruta.objects.get(pk=rutas_id)
        parada = models.Parada.objects.get(pk=parada_id)

        models.Factura.objects.create(
            bot_id=bot,
            rutas_id=ruta,
            parada_id=parada,
            fecha=timezone.now().date(),
            hora=timezone.now().strftime('%H:%M:%S'),
            accion=accion
        ).save()  
        
        return JsonResponse({'status': 'success', 'message': 'Factura registrada'})

    except Bot.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': f'Bot con id {bot_id} no encontrado'}, status=404)
    except models.Ruta.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': f'Ruta con id {rutas_id} no encontrada'}, status=404)
    except models.Parada.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': f'Parada con id {parada_id} no encontrada'}, status=404)
    except Exception as e:
        
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)