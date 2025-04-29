from django.contrib import admin
from .models import Vistoria, VistoriaEquipamento, AvaliacaoParametro
from equipamentos.models import Equipamento, ParametroEquipamento


class AvaliacaoParametroInline(admin.TabularInline):
    model = AvaliacaoParametro
    extra = 0
    autocomplete_fields = ['parametro']
    fields = ('parametro', 'situacao', 'observacoes')
    show_change_link = False


class VistoriaEquipamentoInline(admin.StackedInline):
    model = VistoriaEquipamento
    extra = 0
    autocomplete_fields = ['equipamento']
    fields = ('equipamento', 'status_final', 'observacoes')
    show_change_link = True

    # Avaliação dos parâmetros será feita na página do VistoriaEquipamento
    def get_inline_instances(self, request, obj=None):
        return []


@admin.register(VistoriaEquipamento)
class VistoriaEquipamentoAdmin(admin.ModelAdmin):
    list_display = ('equipamento', 'vistoria', 'status_final', 'vistoriado_em')
    list_filter = ('status_final', 'vistoria__cliente')
    search_fields = ('equipamento__nome', 'vistoria__cliente__nome_fantasia')
    autocomplete_fields = ['vistoria', 'equipamento']
    inlines = [AvaliacaoParametroInline]
    readonly_fields = ('vistoriado_em',)


@admin.register(Vistoria)
class VistoriaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'unidade', 'sublocal', 'data', 'status')
    list_filter = ('cliente', 'unidade', 'status')
    search_fields = ('cliente__nome_fantasia', 'unidade', 'sublocal')
    autocomplete_fields = ['cliente', 'realizada_por']
    readonly_fields = ('criado_em', 'atualizado_em')
    inlines = [VistoriaEquipamentoInline]

    fieldsets = (
        ('Local da Vistoria', {
            'fields': ('cliente', 'unidade', 'sublocal')
        }),
        ('Detalhes', {
            'fields': ('horario_inicio', 'horario_fim', 'status', 'realizada_por')
        }),
        ('Observações Gerais', {
            'fields': ('observacoes_gerais',)
        }),
        ('Auditoria', {
            'fields': ('criado_em', 'atualizado_em')
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # Se for uma nova vistoria (não está editando)
        if not change:
            equipamentos = Equipamento.objects.filter(cliente=obj.cliente)
            for equipamento in equipamentos:
                VistoriaEquipamento.objects.create(
                    vistoria=obj,
                    equipamento=equipamento,
                    status_final='disponivel'  # você pode ajustar esse valor padrão
                )


@admin.register(AvaliacaoParametro)
class AvaliacaoParametroAdmin(admin.ModelAdmin):
    list_display = ('parametro', 'vistoria_equipamento', 'situacao')
    list_filter = ('situacao', 'parametro__gravidade')
    search_fields = ('parametro__nome', 'vistoria_equipamento__equipamento__nome')
    autocomplete_fields = ['parametro', 'vistoria_equipamento']
