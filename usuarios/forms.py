# usuarios/forms.py
from django import forms
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        label='Nome de usuário',
        help_text='Será usado para login.'
    )

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

    def __init__(self, *args, **kwargs):
        # Espera-se que o User esteja associado ao instance
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {})
        if instance and instance.user:
            initial['username'] = instance.user.username
            kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        usuario = super().save(commit=False)
        username = self.cleaned_data.get('username')
        if usuario.user:
            usuario.user.username = username
            usuario.user.save()
        if commit:
            usuario.save()
        return usuario
