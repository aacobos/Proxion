from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import CategoriaEquipamento, Equipamento, ParametroEquipamento

@admin.register(CategoriaEquipamento)
class CategoriaEquipamentoAdmin(admin.ModelAdmin):
    list_display = ['nome']
    filter_horizontal = ['parametros']  # Isso mostra o campo de seleção de parâmetros corretamente

@admin.register(ParametroEquipamento)
class ParametroEquipamentoAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']

@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'numero_serie', 'categoria', 'situacao', 'status', 'cliente']
    readonly_fields = ['parametros_herdados_da_categoria']
    search_fields = ['nome']

    # Oculta o campo parametros_personalizados do formulário
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if 'parametros_personalizados' in fields:
            fields.remove('parametros_personalizados')
        return fields

    # Só mostra os parâmetros herdados da categoria, em formato legível
    def parametros_herdados_da_categoria(self, obj):
        if obj.categoria:
            return ", ".join([str(p) for p in obj.categoria.parametros.all()])
        return "Nenhum parâmetro definido na categoria."
    parametros_herdados_da_categoria.short_description = "Parâmetros para a vistoria"

    def save_model(self, request, obj, form, change):
        categoria_antiga = None
        if change:
            equipamento_anterior = Equipamento.objects.get(pk=obj.pk)
            categoria_antiga = equipamento_anterior.categoria

        super().save_model(request, obj, form, change)

        # Se for novo ou se a categoria tiver mudado, atualiza os parâmetros personalizados
        if obj.categoria and (not change or obj.categoria != categoria_antiga):
            parametros_da_categoria = obj.categoria.parametros.all()
            obj.parametros_personalizados.set(parametros_da_categoria)



