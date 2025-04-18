from django import forms
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'nome_completo',
            'cpf',
            'email',
            'telefone',
            'foto',
            'assinatura',
            'perfil',
        ]
        widgets = {
            'perfil': forms.Select(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'placeholder': '000.000.000-00'}),
        }