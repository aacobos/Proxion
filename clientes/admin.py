from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Cliente

# Register your models here.
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    # Campos exibidos na listagem
    list_display = (
        'nome_fantasia', 'razao_social', 'cnpj', 'responsavel', 'email',
        'numero_contrato', 'data_inicio_contrato',
        'data_vencimento_contrato', 'data_cadastro', 'logo_thumbnail'
    )
    search_fields = ('nome_fantasia', 'razao_social', 'cnpj', 'responsavel', 'numero_contrato')
    list_filter = ('data_inicio_contrato', 'data_vencimento_contrato')

    # Miniatura do logo
    def logo_thumbnail(self, obj):
        if obj.logo:
            return mark_safe(f'<img src="{obj.logo.url}" style="max-height: 50px;"/>')
        return "Sem Logo"

    logo_thumbnail.short_description = 'Logo'

    # Customizar o formulário para mostrar a miniatura
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['logo'].widget.attrs['readonly'] = True
            form.base_fields['logo'].help_text = mark_safe(
                f'<img src="{obj.logo.url}" style="max-height: 100px;"/>' if obj.logo else "Sem Logo"
            )
        return form