from django import forms
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'
        widgets = {
            'perfil': forms.Select(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'placeholder': '000.000.000-00'}),
        }