from django.urls import path
from . import views

app_name = 'vistorias'

urlpatterns = [
    path('', views.lista_vistorias, name='lista_vistorias'),  # Página inicial do app
    path('nova/', views.criar_vistoria, name='criar_vistoria'),  # Formulário de criação de vistoria
    path('<int:vistoria_id>/equipamentos/', views.equipamentos_para_vistoria, name='equipamentos_para_vistoria'),
    path('<int:vistoria_id>/equipamento/<int:equipamento_id>/avaliar/', views.vistoria_equipamento_form, name='formulario_vistoria_equipamento'),
]

