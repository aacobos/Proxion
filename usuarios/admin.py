from django.contrib import admin
from .models import Usuario
from django.utils.safestring import mark_safe

# Registro do modelo Usuario no admin
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    # Campos a serem exibidos na listagem
    list_display = ('nome_completo', 'cpf', 'email', 'telefone', 'perfil', 'data_cadastro', 'foto_thumbnail', 'assinatura_thumbnail')

    # Função para exibir a miniatura da foto
    def foto_thumbnail(self, obj):
        if obj.foto:
            return mark_safe(f'<img src="{obj.foto.url}" style="max-height: 50px;"/>')
        return "Sem Foto"
    
    # Função para exibir a miniatura da assinatura
    def assinatura_thumbnail(self, obj):
        if obj.assinatura:
            return mark_safe(f'<img src="{obj.assinatura.url}" style="max-height: 50px;"/>')
        return "Sem Assinatura"

    # Definindo um título amigável para as miniaturas
    foto_thumbnail.short_description = 'Foto'
    assinatura_thumbnail.short_description = 'Assinatura'

     # Customizar o formulário de detalhes para mostrar as miniaturas
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:  # Quando um objeto (usuário) já foi carregado, exibe as miniaturas
            form.base_fields['foto'].widget.attrs['readonly'] = True
            form.base_fields['assinatura'].widget.attrs['readonly'] = True
            form.base_fields['foto'].help_text = mark_safe(f'<img src="{obj.foto.url}" style="max-height: 100px;"/>' if obj.foto else "Sem Foto")
            form.base_fields['assinatura'].help_text = mark_safe(f'<img src="{obj.assinatura.url}" style="max-height: 100px;"/>' if obj.assinatura else "Sem Assinatura")
        return form
