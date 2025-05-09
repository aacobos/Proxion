from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.utils import timezone
from datetime import timedelta

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

    context = {
        'vistorias_ultimos_30_dias': vistorias_ultimos_30_dias,
        'total_clientes': total_clientes,
        'total_equipamentos': total_equipamentos,
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
