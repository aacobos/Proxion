from django.shortcuts import render, get_object_or_404, redirect
from .models import Vistoria, VistoriaEquipamento, AvaliacaoParametro
from equipamentos.models import Equipamento, ParametroEquipamento
from .forms import VistoriaForm
from django.utils.timezone import now
from django.contrib import messages

def listar_vistorias(request):
    vistorias = Vistoria.objects.all()
    return render(request, 'vistorias/listar_vistorias.html', {'vistorias': vistorias})

def criar_vistoria(request):
    if request.method == 'POST':
        form = VistoriaForm(request.POST)
        if form.is_valid():
            vistoria = form.save(commit=False)
            vistoria.realizada_por = request.user.usuario
            vistoria.save()
            messages.success(request, 'Vistoria criada com sucesso.')
            return redirect('vistorias:equipamentos_para_vistoria', vistoria_id=vistoria.id)
    else:
        form = VistoriaForm()
    return render(request, 'vistorias/criar_vistoria.html', {'form': form})

def equipamentos_para_vistoria(request, vistoria_id):
    vistoria = get_object_or_404(Vistoria, id=vistoria_id)
    equipamentos_base = Equipamento.objects.filter(cliente=vistoria.cliente)

    # Verifica se deve ocultar os já avaliados
    if request.GET.get("ver_todos") != "1":
        vistoriados_ids = VistoriaEquipamento.objects.filter(
            vistoria=vistoria
        ).values_list('equipamento_id', flat=True)
        equipamentos_base = equipamentos_base.exclude(id__in=vistoriados_ids)

    equipamentos_data = []

    for equipamento in equipamentos_base:
        vistoria_equipamento = VistoriaEquipamento.objects.filter(
            vistoria=vistoria, equipamento=equipamento
        ).first()

        data_ultima_vistoria = (
            VistoriaEquipamento.objects.filter(equipamento=equipamento)
            .order_by('-id').values_list('vistoria__data', flat=True).first()
        )

        equipamentos_data.append({
            'id': equipamento.id,
            'nome': equipamento.nome,
            'avaliado': vistoria_equipamento is not None,
            'data_ultima_vistoria': data_ultima_vistoria,
        })

    return render(request, 'vistorias/equipamentos_para_vistoria.html', {
        'vistoria': vistoria,
        'equipamentos': equipamentos_data,
    })


def vistoria_equipamento_form(request, vistoria_id, equipamento_id):
    vistoria = get_object_or_404(Vistoria, id=vistoria_id)
    equipamento = get_object_or_404(Equipamento, id=equipamento_id)

    parametros_categoria = equipamento.categoria.parametros.all()
    parametros_personalizados = equipamento.parametros_personalizados.all()
    parametros = list(set(parametros_categoria) | set(parametros_personalizados))

    if request.method == 'POST':
        status_final = request.POST.get('status_final')
        observacoes_gerais = request.POST.get('observacoes', '')

        vistoria_equip = VistoriaEquipamento.objects.create(
            vistoria=vistoria,
            equipamento=equipamento,
            status_final=status_final,
            observacoes=observacoes_gerais
        )

        for parametro in parametros:
            situacao = request.POST.get(f'parametro_{parametro.id}')
            obs = request.POST.get(f'observacao_{parametro.id}', '')
            if situacao:
                AvaliacaoParametro.objects.create(
                    vistoria_equipamento=vistoria_equip,
                    parametro=parametro,
                    situacao=situacao,
                    observacoes=obs
                )

        messages.success(request, 'Equipamento vistoriado com sucesso.')
        return redirect('vistorias:equipamentos_para_vistoria', vistoria_id=vistoria.id)

    return render(request, 'vistorias/vistoria_equipamento_form.html', {
        'vistoria': vistoria,
        'equipamento': equipamento,
        'parametros': parametros,
        'situacao_choices': AvaliacaoParametro.SITUACAO_CHOICES,
        'status_choices': equipamento.STATUS_CHOICES,
    })

def finalizar_vistoria(request, vistoria_id):
    vistoria = get_object_or_404(Vistoria, id=vistoria_id)
    if vistoria.status == 'finalizada':
        messages.info(request, 'Vistoria já finalizada.')
        return redirect('vistorias:listar_vistorias')

    vistoria.status = 'finalizada'
    vistoria.horario_fim = now().time()
    vistoria.save()
    messages.success(request, 'Vistoria finalizada com sucesso.')
    return redirect('vistorias:listar_vistorias')

def detalhes_vistoria(request, vistoria_id):
    vistoria = get_object_or_404(Vistoria, id=vistoria_id)
    equipamentos = vistoria.equipamentos_vistoriados.all()
    return render(request, 'vistorias/detalhes_vistoria.html', {
        'vistoria': vistoria,
        'equipamentos': equipamentos
    })
