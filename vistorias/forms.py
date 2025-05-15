from django import forms
from .models import Vistoria, VistoriaEquipamento

class VistoriaEquipamentoForm(forms.ModelForm):
    class Meta:
        model = VistoriaEquipamento
        fields = ['status_final']

class VistoriaForm(forms.ModelForm):
    class Meta:
        model = Vistoria
        fields = ['cliente', 'unidade']