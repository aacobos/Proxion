from django.shortcuts import render, get_object_or_404, redirect
from .models import Vistoria, VistoriaEquipamento, Equipamento, ParametroEquipamento, AvaliacaoParametro
from .forms import VistoriaForm

def equipamentos_para_vistoria(request, vistoria_id):
    vistoria = get_object_or_404(Vistoria, id=vistoria_id)

    equipamentos = Equipamento.objects.filter(
        cliente=vistoria.cliente,
    )

    if request.GET.get("ver_todos") != "1":
        # Mostrar só os que ainda não foram vistoriados nesta vistoria, se "ver todos" não for selecionado
        equipamentos_vistoriados_ids = VistoriaEquipamento.objects.filter(
            vistoria=vistoria
        ).values_list('equipamento_id', flat=True)
        equipamentos = equipamentos.exclude(id__in=equipamentos_vistoriados_ids)

    context = {
        'vistoria': vistoria,
        'equipamentos': equipamentos,
    }

    return render(request, 'vistorias/equipamentos_para_vistoria.html', context)

def vistoria_equipamento_form(request, vistoria_id, equipamento_id):
    vistoria = get_object_or_404(Vistoria, id=vistoria_id)
    equipamento = get_object_or_404(Equipamento, id=equipamento_id)

    parametros_categoria = equipamento.categoria.parametros.all()
    parametros_personalizados = equipamento.parametros_personalizados.all()
    parametros = list(set(parametros_categoria) | set(parametros_personalizados))

    situacao_choices = AvaliacaoParametro.SITUACAO_CHOICES
    status_choices = Equipamento.STATUS_CHOICES

    if request.method == 'POST':
        novo_status = request.POST.get('status')

        # Atualiza o status do equipamento se necessário
        if novo_status:
            equipamento.status = novo_status
            equipamento.save()

        # Sempre cria uma nova VistoriaEquipamento
        vistoria_equipamento = VistoriaEquipamento.objects.create(
            vistoria=vistoria,
            equipamento=equipamento,
            status_final=novo_status if novo_status else equipamento.status,
        )

        # Salvar avaliações dos parâmetros
        for parametro in parametros:
            valor = request.POST.get(f'parametro_{parametro.id}')
            if valor:
                AvaliacaoParametro.objects.create(
                    vistoria_equipamento=vistoria_equipamento,
                    parametro=parametro,
                    situacao=valor
                )

        return redirect('vistorias:equipamentos_para_vistoria', vistoria_id=vistoria.id)

    return render(request, 'vistorias/vistoria_equipamento_form.html', {
        'vistoria': vistoria,
        'equipamento': equipamento,
        'parametros': parametros,
        'situacao_choices': situacao_choices,
        'status_choices': status_choices,
    })

def lista_vistorias(request):
    vistorias = Vistoria.objects.all()
    return render(request, 'vistorias/lista_vistorias.html', {'vistorias': vistorias})

def criar_vistoria(request):
    if request.method == 'POST':
        form = VistoriaForm(request.POST)
        if form.is_valid():
            vistoria = form.save()
            return redirect('vistorias:equipamentos_para_vistoria', vistoria_id=vistoria.id)
    else:
        form = VistoriaForm()
    return render(request, 'vistorias/criar_vistoria.html', {'form': form})
