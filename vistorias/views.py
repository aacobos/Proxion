from django.shortcuts import render, get_object_or_404, redirect
from .models import Vistoria, VistoriaEquipamento, AvaliacaoParametro
from equipamentos.models import Equipamento, ParametroEquipamento
from .forms import VistoriaForm
from django.utils.timezone import now
from django.contrib import messages

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO

from django.conf import settings

from django.db.models import Count

from django.db.models import Q

def listar_vistorias(request):
    termo = request.GET.get('q', '').strip()

    vistorias = Vistoria.objects.annotate(
        qtd_equipamentos=Count('equipamentos_vistoriados')
    )

    if termo:
        vistorias = vistorias.filter(
            Q(cliente__nome_fantasia__icontains=termo) |
            Q(status__icontains=termo) |
            Q(unidade__icontains=termo) |
            Q(sublocal__icontains=termo) |
            Q(realizada_por__nome_completo__icontains=termo)
        )

    return render(request, 'vistorias/listar_vistorias.html', {
        'vistorias': vistorias,
        'termo_busca': termo,
    })


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

# Criar a view AJAX para retornar os dados do cliente
from django.http import JsonResponse
from clientes.models import Cliente

def dados_cliente_ajax(request):
    cliente_id = request.GET.get('cliente_id')
    data = {'unidade': '', 'sigla': ''}
    if cliente_id:
        try:
            cliente = Cliente.objects.get(pk=cliente_id)
            data['unidade'] = cliente.unidade or ''
            data['sigla'] = cliente.sigla or ''
        except Cliente.DoesNotExist:
            pass
    return JsonResponse(data)



def excluir_vistoria(request, vistoria_id):
    vistoria = get_object_or_404(Vistoria, id=vistoria_id)

    if request.method == 'POST':
        vistoria.delete()
        messages.success(request, 'Vistoria excluída com sucesso.')
        return redirect('vistorias:listar_vistorias')

    return render(request, 'vistorias/confirmar_exclusao.html', {'vistoria': vistoria})


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
            gravidade = request.POST.get(f'gravidade_{parametro.id}')  # <-- NOVO
            obs = request.POST.get(f'observacao_{parametro.id}', '')

            if situacao:
                AvaliacaoParametro.objects.create(
                    vistoria_equipamento=vistoria_equip,
                    parametro=parametro,
                    situacao=situacao,
                    gravidade=gravidade if situacao == 'danificado' else None,
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
        'gravidade_choices': AvaliacaoParametro.GRAVIDADE_CHOICES,  # <-- NOVO
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

# Gerar Relatório
from itertools import islice

def agrupar_em(lista, tamanho):
    """Divide uma lista em sublistas com tamanho máximo `tamanho`."""
    return [lista[i:i + tamanho] for i in range(0, len(lista), tamanho)]

def gerar_relatorio_vistoria(request, pk):
    vistoria = get_object_or_404(Vistoria, pk=pk)

    # Pegando os equipamentos relacionados corretamente
    equipamentos = list(vistoria.equipamentos_vistoriados.select_related(
        'equipamento', 'equipamento__categoria'
    ).prefetch_related('avaliacoes', 'avaliacoes__parametro'))

    # Agrupar os equipamentos em blocos de até 15
    grupos_equipamentos = agrupar_em(equipamentos, 15)

    return render(request, 'vistorias/relatorio_vistoria.html', {
        'vistoria': vistoria,
        'grupos_equipamentos': grupos_equipamentos,
    })
