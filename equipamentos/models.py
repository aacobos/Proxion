from django.db import models
from clientes.models import Cliente
from usuarios.models import Usuario


# Parâmetros que podem ser avaliados nos equipamentos
class ParametroEquipamento(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    

    avaliacao_ajuda = models.TextField(
        blank=True,
        verbose_name="Como avaliar",
        help_text="Descreva como o analista deve avaliar este parâmetro."
    )

    def __str__(self):
        return self.nome


# Categoria de Equipamento: ex: Coletor de Dados, Nobreak, Rádio, etc.
class CategoriaEquipamento(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    
    # Parâmetros padrão para todos os equipamentos dessa categoria
    parametros = models.ManyToManyField(ParametroEquipamento, blank=True)

    def __str__(self):
        return self.nome


# Equipamento individual
class Equipamento(models.Model):
    SITUACAO_CHOICES = (
        ('em_contrato', 'Em contrato'),
        ('sem_contrato', 'Sem contrato'),
    )

    STATUS_CHOICES = (
        ('em_producao', 'Em Produção'),
        ('disponivel', 'Disponível'),
        ('em_manutencao', 'Em Manutenção'),
        ('danificado', 'Danificado'),
        ('indisponivel', 'Indisponível'),
    )

    nome = models.CharField(max_length=255)
    etiqueta = models.CharField(max_length=100, blank=True)
    numero_serie = models.CharField(max_length=100, unique=True)
    codigo_referencia = models.CharField(max_length=100, blank=True)

    categoria = models.ForeignKey(CategoriaEquipamento, on_delete=models.SET_NULL, null=True, blank=True)
    fabricante = models.CharField(max_length=100, blank=True)
    marca = models.CharField(max_length=100, blank=True)
    modelo = models.CharField(max_length=100, blank=True)

    situacao = models.CharField(max_length=20, choices=SITUACAO_CHOICES, default='em_contrato')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponivel')

    data_compra = models.DateField(null=True, blank=True)
    data_garantia = models.DateField(null=True, blank=True)
    custo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    descricao = models.TextField(blank=True)
    fornecedores = models.CharField(max_length=255, blank=True)
    utilizado_por = models.CharField(max_length=255, blank=True)
    tags = models.CharField(max_length=255, blank=True)

    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)

    cadastrado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipamentos_cadastrados')
    cadastrado_em = models.DateTimeField(auto_now_add=True)
    alterado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipamentos_alterados')
    alterado_em = models.DateTimeField(auto_now=True)

    # Parâmetros específicos aplicados ao equipamento (podem ser herdados da categoria ou personalizados)
    parametros_personalizados = models.ManyToManyField(ParametroEquipamento, blank=True)

    def __str__(self):
        return f"{self.nome} - {self.numero_serie}"


