from django.urls import path, include
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.listar_usuarios, name='listar_usuarios'),
    path('cadastrar/', views.cadastrar_usuario, name='cadastrar_usuario'),
    path('editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),
    path('excluir/<int:pk>/', views.excluir_usuario, name='excluir_usuario'),
    path('detalhes/<int:usuario_id>/', views.detalhes_usuario, name='detalhes_usuario'),
]
