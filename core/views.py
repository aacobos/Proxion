from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.utils import timezone
from datetime import timedelta

from django.db.models.functions import TruncMonth
from django.db.models import Count

from vistorias.models import Vistoria
from clientes.models import Cliente
from equipamentos.models import Equipamento


def dashboard(request):
    # Total de vistorias nos ultimos 30 dias
    hoje = timezone.now().date()
    data_limite = hoje - timedelta(days=30)
    vistorias_ultimos_30_dias = Vistoria.objects.filter(data__gte=data_limite).count()

    # Total de clientes cadastrados
    total_clientes = Cliente.objects.count()

    # Total de equipamentos cadastrados
    total_equipamentos = Equipamento.objects.count()

    # Gráfico de barras verticais/histograma de vistorias por mês
        # Agrupar por mês e contar
    vistorias_por_mes = (
        Vistoria.objects
        .annotate(mes=TruncMonth('data'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

        # Organizar os dados para o gráfico
    labels = [v['mes'].strftime('%b/%Y') for v in vistorias_por_mes]
    data = [v['total'] for v in vistorias_por_mes]

    # Gráfico de Equipamentos por Status
    equipamentos_por_status = (
    Equipamento.objects
    .values('status')
    .annotate(total=Count('id'))
    )

    status_labels = [e['status'] for e in equipamentos_por_status]
    status_data = [e['total'] for e in equipamentos_por_status]

    # Gráfico de equipamentos por clientes
    equipamentos_por_cliente = (
        Equipamento.objects.values('cliente__nome_fantasia')
        .annotate(total=Count('id'))
        .order_by('cliente__nome_fantasia')
    )
    
    clientes_labels = [item['cliente__nome_fantasia'] for item in equipamentos_por_cliente]
    equipamentos_dados = [item['total'] for item in equipamentos_por_cliente]
 

    # Contextos (informações) que serão retornados no template 
    context = {
        'vistorias_ultimos_30_dias': vistorias_ultimos_30_dias,
        'total_clientes': total_clientes,
        'total_equipamentos': total_equipamentos,
        'grafico_labels': labels,
        'grafico_dados': data,
        'grafico_status_labels': status_labels,
        'grafico_status_dados': status_data,
        'equipamentos_cliente_labels': clientes_labels,
        'equipamentos_cliente_dados': equipamentos_dados,
    }

    return render(request, 'core/dashboard.html', context)


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('core:dashboard')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'core/login.html')

@login_required
def dashboard_view(request):
    return render(request, 'core/dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('core:login')
