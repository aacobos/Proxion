from django.shortcuts import render, get_object_or_404, redirect
from .models import Equipamento, CategoriaEquipamento, ParametroEquipamento
from .forms import EquipamentoForm, ParametroEquipamentoForm
from django.contrib import messages

# Listar equipamentos
def listar_equipamentos(request):
    equipamentos = Equipamento.objects.all()
    return render(request, 'equipamentos/listar_equipamentos.html', {'equipamentos': equipamentos})

# Criar novo equipamento
def cadastrar_equipamento(request):
    if request.method == 'POST':
        form = EquipamentoForm(request.POST)
        if form.is_valid():
            equipamento = form.save()
            messages.success(request, 'Equipamento cadastrado com sucesso!')
            return redirect('equipamentos:listar_equipamentos')
    else:
        form = EquipamentoForm()
    return render(request, 'equipamentos/cadastrar_equipamento.html', {'form': form})

# Editar equipamento
def editar_equipamento(request, pk):
    equipamento = get_object_or_404(Equipamento, pk=pk)
    if request.method == 'POST':
        form = EquipamentoForm(request.POST, instance=equipamento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipamento atualizado com sucesso!')
            return redirect('equipamentos:listar_equipamentos')
    else:
        form = EquipamentoForm(instance=equipamento)
    return render(request, 'equipamentos/cadastrar_equipamento.html', {'form': form})

# Detalhes do equipamento
def detalhes_equipamento(request, pk):
    equipamento = get_object_or_404(Equipamento, pk=pk)
    return render(request, 'equipamentos/detalhes_equipamento.html', {'equipamento': equipamento})

# Excluir equipamento
def excluir_equipamento(request, pk):
    equipamento = get_object_or_404(Equipamento, pk=pk)
    if request.method == 'POST':
        equipamento.delete()
        messages.success(request, 'Equipamento excluído com sucesso!')
        return redirect('equipamentos:listar_equipamentos')
    return render(request, 'equipamentos/confirmar_exclusao.html', {'equipamento': equipamento})

# Listar categorias
def listar_categorias(request):
    categorias = CategoriaEquipamento.objects.all()
    return render(request, 'categorias/listar_categorias.html', {'categorias': categorias})

# Cadastrar nova categoria
def cadastrar_categoria(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        parametros_ids = request.POST.getlist('parametros')

        if nome:
            categoria = CategoriaEquipamento.objects.create(nome=nome)
            categoria.parametros.set(parametros_ids)
            categoria.save()
            messages.success(request, 'Categoria cadastrada com sucesso!')
            return redirect('equipamentos:listar_categorias')
        else:
            messages.error(request, 'O nome da categoria é obrigatório.')

    parametros = ParametroEquipamento.objects.all()
    return render(request, 'categorias/cadastrar_categoria.html', {'parametros': parametros})

# Editar categoria existente
def editar_categoria(request, pk):
    categoria = get_object_or_404(CategoriaEquipamento, pk=pk)

    if request.method == 'POST':
        nome = request.POST.get('nome')
        parametros_ids = request.POST.getlist('parametros')

        if nome:
            categoria.nome = nome
            categoria.save()

            # Atualiza os parâmetros, mesmo se lista estiver vazia
            categoria.parametros.set(parametros_ids)

            messages.success(request, 'Categoria atualizada com sucesso!')
            return redirect('equipamentos:listar_categorias')
        else:
            messages.error(request, 'O nome da categoria é obrigatório.')

    parametros = ParametroEquipamento.objects.all()
    return render(request, 'categorias/editar_categoria.html', {
        'categoria': categoria,
        'parametros': parametros
    })

# Detalhes da categoria
def detalhes_categoria(request, pk):
    categoria = get_object_or_404(CategoriaEquipamento, pk=pk)
    return render(request, 'categorias/detalhes_categoria.html', {'categoria': categoria})

# Excluir categoria com confirmação
def excluir_categoria(request, pk):
    categoria = get_object_or_404(CategoriaEquipamento, pk=pk)
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoria excluída com sucesso.')
        return redirect('equipamentos:listar_categorias')
    return render(request, 'categorias/confirmar_exclusao.html', {'categoria': categoria})

# Listar parâmetros
def listar_parametros(request):
    parametros = ParametroEquipamento.objects.all()
    return render(request, 'parametros/listar_parametros.html', {'parametros': parametros})

# Cadastrar parâmetros
def cadastrar_parametro(request):
    if request.method == 'POST':
        form = ParametroEquipamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Parâmetro cadastrado com sucesso.')
            return redirect('equipamentos:listar_parametros')
    else:
        form = ParametroEquipamentoForm()
    
    return render(request, 'parametros/cadastrar_parametro.html', {'form': form})

# Editar parâmetro
def editar_parametro(request, pk):
    parametro = get_object_or_404(ParametroEquipamento, pk=pk)
    if request.method == 'POST':
        form = ParametroEquipamentoForm(request.POST, instance=parametro)
        if form.is_valid():
            form.save()
            messages.success(request, 'Parâmetro atualizado com sucesso.')
            return redirect('equipamentos:listar_parametros')
    else:
        form = ParametroEquipamentoForm(instance=parametro)

    return render(request, 'parametros/editar_parametro.html', {'form': form, 'parametro': parametro})

# Detalhes do parâmetro
def detalhes_parametro(request, pk):
    parametro = get_object_or_404(ParametroEquipamento, pk=pk)
    return render(request, 'parametros/detalhes_parametro.html', {'parametro': parametro})

# Excluir parâmetro
def excluir_parametro(request, pk):
    parametro = get_object_or_404(ParametroEquipamento, pk=pk)
    if request.method == 'POST':
        parametro.delete()
        messages.success(request, 'Parâmetro excluído com sucesso!')
        return redirect('equipamentos:listar_parametros')
    return render(request, 'parametros/confirmar_exclusao.html', {'parametro': parametro})
