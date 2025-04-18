from django.urls import path, include
from .import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.usuario, name="usuario"),
    path('registrar/', views.registrar_usuario, name='registrar_usuario'),
    path('lista/', views.lista_usuarios, name='lista_usuarios'),
]