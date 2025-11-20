from django.urls import path
from seguridad import views
urlpatterns = [
    path('login/', views.logi, name='login'),
    path('verificar_correo', views.verificar_correo, name='verificar_correo'),
    path('correo/', views.correo, name='correo'),
    path('aceptar_solicitud/<str:token>/', views.aceptar_solicitud, name='aceptar_solicitud'),
    path('logueo/', views.logueo, name='logueo'),
    path('', views.home, name="home"),
    path('facial/', views.facial, name="facial"),
    path('usuarios/', views.vistaUsuarios, name="usuarios"),
    path('usuariosCrear/', views.usuariosCrear, name="usuariosCrear"),
    path('logueado/', views.logueado, name='logueado'),
    path('upload-photo/', views.upload_photo, name='upload_photo'),
    path('editarUsuario/<int:id_request>', views.editarUsuario, name='editarUsuario'),
    path('editar_user/', views.editar_user, name='editar_user'), 
    path('dashBoard/', views.dashboard, name='dashboard'),
    path('bots/', views.bots, name='bots'),
    path('crear_bot/', views.crear_bot, name='crear_bot'),
    path('editarBot/<int:id>/', views.editarBot, name='editarBot'),  
    path('logout_views/', views.logout_views, name='logout_views'), 
] 