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

from collections import Counter

from django.db.models import Q

def listar_vistorias(request):
    termo = request.GET.get('q', '').strip()

    vistorias = Vistoria.objects.annotate(
        qtd_equipamentos=Count('equipamentos_vistoriados')  # já vistoriados
    ).order_by('-data', '-criado_em')

    if termo:
        vistorias = vistorias.filter(
            Q(cliente__nome_fantasia__icontains=termo) |
            Q(status__icontains=termo) |
            Q(unidade__icontains=termo) |
            Q(sublocal__icontains=termo) |
            Q(realizada_por__nome_completo__icontains=termo)
        )

    # Novo passo: contar equipamentos cadastrados por cliente
    vistoria_com_dados = []
    for vistoria in vistorias:
        total_cadastrados = Equipamento.objects.filter(cliente=vistoria.cliente).count()
        vistoria.qtd_cadastrados = total_cadastrados
        vistoria_com_dados.append(vistoria)

    return render(request, 'vistorias/listar_vistorias.html', {
        'vistorias': vistoria_com_dados,
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
    termo_busca = request.GET.get("q", "").strip().lower()

    equipamentos_base = Equipamento.objects.filter(cliente=vistoria.cliente)

    equipamentos_data = []

    for equipamento in equipamentos_base:
        vistoria_equipamento = VistoriaEquipamento.objects.filter(
            vistoria=vistoria, equipamento=equipamento
        ).first()

        data_ultima_vistoria = (
            VistoriaEquipamento.objects.filter(equipamento=equipamento)
            .order_by('-id').values_list('vistoria__data', flat=True).first()
        )

        status_avaliado = 'avaliado' if vistoria_equipamento else 'pendente'

        equipamentos_data.append({
            'id': equipamento.id,
            'nome': equipamento.nome,
            'numero_serie': equipamento.numero_serie,
            'avaliado': vistoria_equipamento is not None,
            'status_avaliado': status_avaliado,
            'data_ultima_vistoria': data_ultima_vistoria,
        })

    # Filtro por nome, número de série ou status de avaliação
    if termo_busca:
        equipamentos_data = [
            e for e in equipamentos_data
            if termo_busca in (e['nome'] or '').lower()
            or termo_busca in (e['numero_serie'] or '').lower()
            or termo_busca in e['status_avaliado']
        ]

    return render(request, 'vistorias/equipamentos_para_vistoria.html', {
        'vistoria': vistoria,
        'equipamentos': equipamentos_data,
        'termo_busca': termo_busca,
    })

    # Filtro de busca no nome, número de série ou status de avaliação
    if termo_busca:
        equipamentos_data = [
            e for e in equipamentos_data
            if termo_busca in (e['nome'] or '').lower()
            or termo_busca in (e.get('numero_serie') or '').lower()
            or termo_busca in e['status_avaliado']
        ]

    return render(request, 'vistorias/equipamentos_para_vistoria.html', {
        'vistoria': vistoria,
        'equipamentos': equipamentos_data,
        'termo_busca': termo_busca,
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


from django.shortcuts import render, get_object_or_404
from collections import Counter
from .models import Vistoria, VistoriaEquipamento, AvaliacaoParametro

from collections import Counter
from django.db.models import Q

def detalhes_vistoria(request, vistoria_id):
    vistoria = get_object_or_404(Vistoria, id=vistoria_id)

    termo_busca = request.GET.get('q', '')

    equipamentos = vistoria.equipamentos_vistoriados.select_related(
        'equipamento__categoria'
    ).prefetch_related('avaliacoes', 'avaliacoes__parametro')

    # Filtro por nome, categoria, número de série ou status
    if termo_busca:
        equipamentos = equipamentos.filter(
            Q(equipamento__nome__icontains=termo_busca) |
            Q(equipamento__categoria__nome__icontains=termo_busca) |
            Q(equipamento__numero_serie__icontains=termo_busca) |
            Q(status_final__icontains=termo_busca)
        )

    # Ordenação por nome do equipamento
    equipamentos = sorted(equipamentos, key=lambda x: x.equipamento.nome.lower())

    # Contadores para gráfico geral
    status_counter = Counter()
    gravidade_counter = Counter()

    # Contador para parâmetros danificados gravemente
    parametros_graves_counter = Counter()

    for eq in equipamentos:
        status = eq.status_final
        if status == 'danificado':
            for av in eq.avaliacoes.all():
                if av.situacao == 'danificado':
                    if av.gravidade:
                        gravidade_counter[av.gravidade] += 1
                        if av.gravidade == 'grave':
                            parametros_graves_counter[av.parametro.nome] += 1
        else:
            status_counter[status] += 1

    # Dados do gráfico de pizza (visão geral)
    grafico_labels = [
        'Em Produção', 'Disponível', 'Em Manutenção',
        'Danificado - Leve', 'Danificado - Médio', 'Danificado - Grave',
    ]
    grafico_dados = [
        status_counter.get('em_producao', 0),
        status_counter.get('disponivel', 0),
        status_counter.get('em_manutencao', 0),
        gravidade_counter.get('leve', 0),
        gravidade_counter.get('medio', 0),
        gravidade_counter.get('grave', 0),
    ]

    # Preparar dados para gráfico de barras (10 parâmetros graves principais)
    parametros_graves_ordenados = parametros_graves_counter.most_common(10)
    parametros_graves_labels = [p[0] for p in parametros_graves_ordenados]
    parametros_graves_dados = [p[1] for p in parametros_graves_ordenados]

    return render(request, 'vistorias/detalhes_vistoria.html', {
        'vistoria': vistoria,
        'equipamentos': equipamentos,
        'grafico_labels': grafico_labels,
        'grafico_dados': grafico_dados,
        'termo_busca': termo_busca,
        'parametros_graves_labels': parametros_graves_labels,
        'parametros_graves_dados': parametros_graves_dados,
    })

# Gerar Relatório
from itertools import islice

def agrupar_em(lista, tamanho):
    """Divide uma lista em sublistas com tamanho máximo `tamanho`."""
    return [lista[i:i + tamanho] for i in range(0, len(lista), tamanho)]

def gerar_relatorio_vistoria(request, pk):
    vistoria = get_object_or_404(Vistoria, pk=pk)

    equipamentos = list(vistoria.equipamentos_vistoriados.select_related(
        'equipamento', 'equipamento__categoria'
    ).prefetch_related('avaliacoes', 'avaliacoes__parametro'))

    # Gráficos
    status_counter = Counter()
    gravidade_counter = Counter()
    parametros_graves_counter = Counter()

    for eq in equipamentos:
        status = eq.status_final
        if status == 'danificado':
            for av in eq.avaliacoes.all():
                if av.situacao == 'danificado' and av.gravidade:
                    gravidade_counter[av.gravidade] += 1
                    if av.gravidade == 'grave':
                        parametros_graves_counter[av.parametro.nome] += 1
        else:
            status_counter[status] += 1

    grafico_labels = [
        'Em Produção', 'Disponível', 'Em Manutenção',
        'Danificado - Leve', 'Danificado - Médio', 'Danificado - Grave',
    ]
    grafico_dados = [
        status_counter.get('em_producao', 0),
        status_counter.get('disponivel', 0),
        status_counter.get('em_manutencao', 0),
        gravidade_counter.get('leve', 0),
        gravidade_counter.get('medio', 0),
        gravidade_counter.get('grave', 0),
    ]

    parametros_graves_ordenados = parametros_graves_counter.most_common(10)
    parametros_graves_labels = [p[0] for p in parametros_graves_ordenados]
    parametros_graves_dados = [p[1] for p in parametros_graves_ordenados]

    analista = vistoria.realizada_por  # objeto Usuario

    return render(request, 'vistorias/relatorio_vistoria.html', {
        'vistoria': vistoria,
        'equipamentos': equipamentos,
        'grafico_labels': grafico_labels,
        'grafico_dados': grafico_dados,
        'parametros_graves_labels': parametros_graves_labels,
        'parametros_graves_dados': parametros_graves_dados,
        'analista_nome': analista.nome_completo if analista else '',
        'analista_assinatura': analista.assinatura.url if analista and analista.assinatura else '',
    })

