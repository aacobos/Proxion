from django.db import models
from django.utils import timezone

# Create your models here.
from django.db import models
from django.utils import timezone

class Cliente(models.Model):
    nome_fantasia = models.CharField(max_length=255)
    razao_social = models.CharField(max_length=255, blank=True)
    cnpj = models.CharField(max_length=18, unique=True)
    
    email = models.EmailField(blank=True)
    endereco = models.CharField(max_length=255)

    # Sigla do cliente
    sigla = models.CharField(max_length=50, blank=True, verbose_name='Sigla do Cliente')
    unidade = models.CharField(max_length=100, blank=True)
    sub_local = models.CharField(max_length=100, blank=True, verbose_name='Sub-local')

    # Nome do responsável pela empresa
    responsavel = models.CharField(max_length=255, blank=True)

    # Logo da empresa
    logo = models.ImageField(upload_to='clientes/logos/', null=True, blank=True)

    # Dados do contrato
    numero_contrato = models.CharField(max_length=100, blank=True)
    data_inicio_contrato = models.DateField(null=True, blank=True)
    data_vencimento_contrato = models.DateField(null=True, blank=True)

    # Data de cadastro do cliente no sistema
    data_cadastro = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return self.nome_fantasia
