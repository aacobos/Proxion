from django import forms
from .models import Equipamento, ParametroEquipamento

class EquipamentoForm(forms.ModelForm):
    class Meta:
        model = Equipamento
        fields = [
            'nome', 'etiqueta', 'numero_serie', 'codigo_referencia',
            'categoria', 'fabricante', 'marca', 'modelo',
            'situacao', 'status', 'data_compra', 'data_garantia',
            'custo', 'descricao', 'fornecedores', 'utilizado_por',
            'tags', 'cliente', 'parametros_personalizados'
        ]
        widgets = {
            'data_compra': forms.DateInput(attrs={'type': 'date'}),
            'data_garantia': forms.DateInput(attrs={'type': 'date'}),
            'descricao': forms.Textarea(attrs={'rows': 3}),
            'parametros_personalizados': forms.CheckboxSelectMultiple(),
        }

class ParametroEquipamentoForm(forms.ModelForm):
    class Meta:
        model = ParametroEquipamento
        fields = ['nome', 'avaliacao_ajuda']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avaliacao_ajuda'].widget.attrs.update({
            'placeholder': "Descreva como o analista deve avaliar este parâmetro."
        })
