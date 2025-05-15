from django.urls import path
from . import views

app_name = 'vistorias'

urlpatterns = [
    path('', views.listar_vistorias, name='listar_vistorias'),
    path('nova/', views.criar_vistoria, name='criar_vistoria'),
    path('<int:vistoria_id>/', views.detalhes_vistoria, name='detalhes_vistoria'),
    path('<int:vistoria_id>/equipamentos/', views.equipamentos_para_vistoria, name='equipamentos_para_vistoria'),
    path('<int:vistoria_id>/equipamento/<int:equipamento_id>/', views.vistoria_equipamento_form, name='vistoria_equipamento_form'),
    path('<int:vistoria_id>/finalizar/', views.finalizar_vistoria, name='finalizar_vistoria'),
    path('<int:pk>/relatorio/', views.gerar_relatorio_vistoria, name='gerar_relatorio'),
    path('<int:vistoria_id>/excluir/', views.excluir_vistoria, name='excluir_vistoria'),
    path('dados-cliente/', views.dados_cliente_ajax, name='dados_cliente_ajax'),
]
