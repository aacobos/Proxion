from django.urls import path
from . import views

app_name = 'equipamentos'

urlpatterns = [
    # Rotas para equipamentos
    path('', views.listar_equipamentos, name='listar_equipamentos'),
    path('cadastrar/', views.cadastrar_equipamento, name='cadastrar_equipamento'),
    path('<int:pk>/', views.detalhes_equipamento, name='detalhes_equipamento'),
    path('<int:pk>/editar/', views.editar_equipamento, name='editar_equipamento'),
    path('<int:pk>/excluir/', views.excluir_equipamento, name='excluir_equipamento'),

    # Rotas para categorias de equipamentos
    path('categorias/', views.listar_categorias, name='listar_categorias'),
    path('categorias/cadastrar/', views.cadastrar_categoria, name='cadastrar_categoria'),
    path('categorias/<int:pk>/', views.detalhes_categoria, name='detalhes_categoria'),
    path('categorias/<int:pk>/editar/', views.editar_categoria, name='editar_categoria'),
    path('categorias/<int:pk>/excluir/', views.excluir_categoria, name='excluir_categoria'),

    # Rotas para parâmetros de equipamentos
    path('parametros/', views.listar_parametros, name='listar_parametros'),
    path('parametros/cadastrar/', views.cadastrar_parametro, name='cadastrar_parametro'),
    path('parametros/<int:pk>/', views.detalhes_parametro, name='detalhes_parametro'),
    path('parametros/<int:pk>/editar/', views.editar_parametro, name='editar_parametro'),
    path('parametros/<int:pk>/excluir/', views.excluir_parametro, name='excluir_parametro'),

]
