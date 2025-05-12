from django.shortcuts import render, get_object_or_404, redirect
from .models import Cliente
from .forms import ClienteForm
from django.contrib import messages

from django.db.models import Q

from vistorias.models import Vistoria
from equipamentos.models import Equipamento

def listar_clientes(request):
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', 'nome_fantasia')
    direction = request.GET.get('direction', 'asc')
    order_field = f"-{sort}" if direction == 'desc' else sort

    clientes = Cliente.objects.all()

    if query:
        clientes = clientes.filter(
            Q(nome_fantasia__icontains=query) |
            Q(razao_social__icontains=query) |
            Q(cnpj__icontains=query) |
            Q(sigla__icontains=query)
        )

    clientes = clientes.order_by(order_field)

    # Atribui diretamente nos objetos cliente
    for cliente in clientes:
        ultima_vistoria = Vistoria.objects.filter(cliente=cliente).order_by('-data').first()
        cliente.ultima_vistoria_data = ultima_vistoria.data if ultima_vistoria else '—'
        cliente.total_equipamentos = Equipamento.objects.filter(cliente=cliente).count()

    colunas = [
        ('nome_fantasia', 'Empresa'),
        ('sigla', 'Código do Cliente'),
        ('cnpj', 'CNPJ'),
        ('responsavel', 'Responsável'),
        ('numero_contrato', 'Telefone'),
    ]

    context = {
        'clientes': clientes,
        'query': query,
        'sort': sort,
        'direction': direction,
        'colunas': colunas,
    }

    return render(request, 'clientes/listar_clientes.html', context)

def cadastrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('clientes:listar_clientes')
    else:
        form = ClienteForm()
    return render(request, 'clientes/cadastrar_cliente.html', {'form': form})

def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('clientes:listar_clientes')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clientes/editar_cliente.html', {'form': form, 'cliente': cliente})

def detalhes_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    return render(request, 'clientes/detalhes_cliente.html', {'cliente': cliente})

def excluir_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente excluído com sucesso!')
        return redirect('clientes:listar_clientes')
    return render(request, 'clientes/excluir_cliente.html', {'cliente': cliente})
