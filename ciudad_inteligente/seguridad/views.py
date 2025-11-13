import os
import uuid
import random
import base64
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from deepface import DeepFace
from django.contrib.auth.models import User

from seguridad import models
from seguridad.models import UsuarioRostro, UsuariosDatosPersonales, TipoUsuario

def facial(request):
    return render(request, "facial.html")

def home(request):
    return render(request, "ini.html")

def logi(request):
    return render(request, "login.html")

def correo(request):
    return render(request, "correo.html")

@login_required
def logueado(request):
    return render(request, 'logueado.html')

def logueo (request):
    if request.method == 'POST':
        try:
            user = request.POST.get('nombre')
            contrasena = request.POST.get('pasword')

            print(f'{user} {contrasena}')

            usuario = authenticate(request, username=user, password=contrasena)
            

            if usuario is not None:
                login(request, usuario)
                print (f'logueado con exito')
                return redirect('logueado')
            else:
                print(f'{usuario}')
                print(f'error al loguear')
                return redirect('login')
        except Exception as e:
            print (f'el error es {e}')
            return redirect ('login')




@csrf_exempt
def upload_photo(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    photo = request.FILES.get("photo")
    if not photo:
        return JsonResponse({"error": "No se recibió ninguna foto"}, status=400)

    filename = f"capturas/{uuid.uuid4().hex}.jpg"
    saved_path = default_storage.save(filename, ContentFile(photo.read()))
    full_path = default_storage.path(saved_path)

    autorizado = comprobacionRostro(full_path)
    default_storage.delete(saved_path)

    if autorizado:
        try:
            rostroUser = UsuarioRostro.objects.get(nombre_archivo=autorizado)
            usuario = rostroUser.usuario
            login(request, usuario)
            return JsonResponse({"autorizado": True, "redirect_url": "/inicio/"})
        except UsuarioRostro.DoesNotExist:
            print(f"[INFO] No se encontró UsuarioRostro con foto: {autorizado}")

    return JsonResponse({"autorizado": False})


def comprobacionRostro(query_img):
    db_path = default_storage.path("faces_db")
    if not os.path.exists(db_path) or not os.listdir(db_path):
        print(f"[AVISO] La base de datos de rostros está vacía: {db_path}")
        return False

    try:
        result = DeepFace.find(img_path=query_img, db_path=db_path, enforce_detection=False)
        if not result[0].empty:
            best_match = result[0].iloc[0]
            nombre_foto = os.path.basename(best_match["identity"])
            print("Coincidencia:", nombre_foto, "Distancia:", best_match["distance"])
            return nombre_foto
        else:
            print("[INFO] No se encontró coincidencia facial.")
            return False
    except ValueError as e:
        print(f"[ERROR] DeepFace falló: {e}")
        return False
    from django.http import JsonResponse
import json

def verificar_correo(request):
    print('Iniciando verificación de correo...')
    if request.method == 'POST':
        try:
            correo = request.POST.get('correo')
            print(f'Correo recibido: {correo}')
            usuario = User.objects.filter(email=correo).first()

            if not usuario:
                print('Correo no registrado.')
                return JsonResponse({
                    'success': False, 
                    'error': 'El correo no está registrado.'
                })

            print(f'Usuario encontrado: {usuario.username}')

            # Tu lógica de generación de token (se mantiene igual)
            letras = list('abcdefghijklmnopqrstuvwxyz')
            numeros = list(range(10))
            simbolos = ['!', '@', '#', '$', '%', '^', '&', '*']

            token = ''.join([
                random.choice(letras) + str(random.choice(numeros)) + random.choice(simbolos)
                for _ in range(4)
            ])

            print(f'Token generado: {token}')
            solicitud = models.SolicitudAcceso.objects.create(usuario=usuario, token=token)
            print('Token guardado en la base de datos.')

            url = request.build_absolute_uri(reverse('aceptar_solicitud', args=[token]))
            print(f'URL generada: {url}')

            mensaje = f"""
            Hola {usuario.username},

            Haz clic en el siguiente enlace para aceptar la solicitud de acceso:

            {url}
            """

            send_mail(
                'Solicitud de acceso',
                mensaje,
                'sulbaranangel31@gmail.com',
                [correo],
                fail_silently=False,
            )

            print('Correo enviado exitosamente.')
            
            return JsonResponse({
                'success': True,
                'message': 'Correo enviado correctamente. Revisa tu bandeja de entrada.'
            })

        except Exception as e:
            print(f'Error al procesar la solicitud: {e}')
            return JsonResponse({
                'success': False,
                'error': 'Ocurrió un error inesperado.'
            })

    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    })

def aceptar_solicitud(request, token):
    solicitud = models.SolicitudAcceso.objects.filter(token=token, usado=False).first()
    
    if solicitud:
        solicitud.usado = True
        solicitud.save()
        usuario = solicitud.usuario
        login(request, usuario)
        messages.success(request, f'¡Bienvenido {usuario.username}! Has iniciado sesión correctamente.')
        return redirect('logueado')  
        
    else:
        messages.error(request, 'Token inválido o ya fue usado.')
        return redirect('logueo')  


@login_required
def vistaUsuarios(request):
    usuarios_comunes = UsuariosDatosPersonales.objects.filter(tipo_usuario=TipoUsuario.COMUN)
    return render(request, "usuariosVista.html", {'usuariosTotales':usuarios_comunes})

@login_required
def usuariosCrear(request):
    if request.method == 'POST':
        try:
            nombre_usuario = request.POST.get('nombre_usuario')
            clave = request.POST.get('clave')
            clave1 = request.POST.get('clave1')
            correo = request.POST.get('correo')
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido')
            cedula = request.POST.get('cedula')

            print(f'{clave} {clave1}')

            if clave != clave1:
                messages.info(request, 'Las contraseñas deben ser iguales')
                print (f'las contraseñas deben ser iguales')
                return redirect ('usuariosCrear')
            
            print(f'cedula es un: {type(cedula)}')
            if type(cedula) == str:
                print (f'si es string')
                try:             
                    print(cedula)    
                    c = int(cedula)
                    print(f'tipo formato {type(c)}')
                    cantidad_numeros = len(cedula)
                    print (f' {cantidad_numeros}') 
                    if cantidad_numeros != 8 and cantidad_numeros != 7:
                        messages.info(request, 'la cantidad de numeros en el campo cedula es erronea debe tener de 7 o 8 digitos')
                        print('la cantidad de numeros es erronea')
                        return redirect ('usuariosCrear')
                         
                except:
                    messages.info(request, 'el formato debe ser numerico ')
                    print(f'error con el formato de la cedula')
                    return redirect ('usuariosCrear')
                    
            
            if User.objects.filter(username=nombre_usuario).exists():
                messages.info(request, 'el usuario ya exise por favor ingrese otro usuario')
                print(f'error de usuario')
                return redirect ('usuariosCrear')
            if models.UsuariosDatosPersonales.objects.filter(cedula=cedula).exists():
                messages.info(request, f'el usuario con esta cedula ya {cedula} existe ya exise por favor verifique la cedula')
                print(f'error de cedula')
                return redirect ('usuariosCrear')
            
            tipo_usuario=None
            if 'adminSwitch' in request.POST and 'comunSwitch' not in request.POST:     
                tipo_usuario = TipoUsuario.ADMIN
            elif 'comunSwitch' in request.POST and 'adminSwitch' not in request.POST:       
                tipo_usuario = TipoUsuario.COMUN
            elif 'adminSwitch' in request.POST and 'comunSwitch' in request.POST:  
                messages.info(request, 'Ambos tipos de usuario fueron seleccionados. Esto no está permitido.')     
                print("Ambos tipos de usuario fueron seleccionados. Esto no está permitido.")
            else:
                messages.info(request, 'No se seleccionó ningún tipo de usuario.') 
                print("No se seleccionó ningún tipo de usuario.")



            foto_subida = request.FILES.get('foto_subida')
            foto_capturada_data = request.POST.get('foto_capturada')

        
            nombre_img = f"{nombre_usuario}_{random.randint(1,999)}.jpg"
            foto_final=None

            
            if foto_capturada_data:
                try:
                    format, imgstr = foto_capturada_data.split(';base64,')
                    foto_final = ContentFile(base64.b64decode(imgstr), name=nombre_img)
                except Exception as e:
                    print("Error al procesar imagen capturada:", e)

            elif foto_subida:
                foto_final = foto_subida

            if foto_final == None:
                messages.info(request, 'por favor suba una imagen para datos biometricos')
                return redirect('usuariosCrear')

            print ('probamos aqui')
            campos = [nombre_usuario, clave, correo, nombre, apellido, cedula, tipo_usuario, foto_final]
            for i in campos: 
                print (i)
            if all(c and str(c).strip() for c in campos):
                print('se cumple?')
                if User.objects.filter(username = nombre_usuario).exists():
                    return redirect ('vistaUsuarios')
                
                usuarioC = User.objects.create_user(
                    username=nombre_usuario,
                    password=clave,
                    email=correo
                )
                
                usuarioC.save()
                print('usuarioCreado')

                if usuarioC:
                    UsuariosDatosPersonales.objects.create(
                        usuario=usuarioC,
                        nombre=nombre,
                        apellido=apellido,
                        cedula=cedula,
                        tipo_usuario=tipo_usuario,
                    ).save()

                    UsuarioRostro.objects.create(
                        usuario=usuarioC,
                        foto=foto_final,
                        nombre_archivo=nombre_img
                    ).save()
            else:
                print("DEBUG campos:", {
                        "nombre_usuario": nombre_usuario,
                        "clave": clave,
                        "correo": correo,
                        "nombre": nombre,
                        "apellido": apellido,
                        "cedula": cedula,
                        "tipo_usuario": tipo_usuario,
                        "foto_final": foto_final,
                    })
                return redirect('usuariosCrear')


            return redirect('usuarios')
        except Exception as e:
            print (f'el error es: {e}')
            return redirect ('usuariosCrear')
    return render(request, "usuariosCreate.html")


@login_required
def editar_user (request):
    if request.method == 'POST':
        try:
            username = request.POST.get('nombre_usuario')
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido')
            correo = request.POST.get('correo')
            cedula = request.POST.get('cedula')
            estatus = request.POST.get('estatus')
            id = request.POST.get('id')
            
            print("=" * 50) 
            print("📋 DATOS RECIBIDOS DEL FORMULARIO:")
            print("=" * 50)
            print(f"👤 Username: '{username}'")
            print(f"📛 Nombre: '{nombre}'")
            print(f"📛 Apellido: '{apellido}'")
            print(f"📧 Correo: '{correo}'")
            print(f"🆔 Cédula: '{cedula}'")
            print(f"📊 Estatus: '{estatus}'")
            print("=" * 50)

            usser_all = User.objects.filter(username=username).exclude(id=id)

            if usser_all.exists():
                messages.info(request, 'El nombre de usuario está en uso')
                print(f'El usuario {username} ya existe en otro registro')
                return redirect('usuarios')
            else:
                # Continuar con la actualización
                print('Username disponible, continuando con actualización...')

            datosPersonales = models.UsuariosDatosPersonales.objects.filter(usuario = id).update(
                nombre = nombre,
                apellido = apellido,
                cedula = cedula,
                estatus = estatus
            )

            usuario = User.objects.filter(id = id).update(
                username = username,
                email = correo,
            )
            messages.info(request, 'usuario editado correctamente')
            return redirect('usuario')
        
        except Exception as e:
            print(f'el error es: {e}')
            messages.info(request, 'Error al actualizar los datos')
            return redirect('usuarios')


@login_required
def editarUsuario(request):
    if request.method == 'POST':
        try:
            identificador = request.POST.get('id')
            print(f'identificado {identificador}')
            id = int (identificador)
            print(f'id = {type(id)}')
            usuario = User.objects.get(id=id)
            print(usuario)
            datos = models.UsuariosDatosPersonales.objects.get(usuario = id)
            print('----------------')
            print(usuario.username)
            return render(request, 'editarUsuario.html', {"u":usuario,
                                                          'd':datos,},)

            
        except Exception as e:
            print (f'esto es: {e}')
            return redirect ('usuarios')
    else:
        print(f'error')
        return redirect ('usuarios') 
        

