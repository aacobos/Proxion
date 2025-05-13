from django.db import models
from django.core.exceptions import ValidationError
from clientes.models import Cliente
from equipamentos.models import Equipamento, ParametroEquipamento
from usuarios.models import Usuario
from django.utils.timezone import now


class Vistoria(models.Model):
    STATUS_CHOICES = (
        ('em_andamento', 'Em andamento'),
        ('finalizada', 'Finalizada'),
    )

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    unidade = models.CharField(max_length=100)
    sublocal = models.CharField(max_length=100, blank=True)

    data = models.DateField(auto_now_add=True)
    horario_inicio = models.TimeField(null=False, blank=False, default=now)
    horario_fim = models.TimeField(null=True, blank=True)

    observacoes_gerais = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='em_andamento')

    realizada_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data', '-criado_em']

    def clean(self):
        if self.horario_fim and self.horario_inicio and self.horario_fim <= self.horario_inicio:
            raise ValidationError("O horário de fim deve ser posterior ao horário de início.")

    def __str__(self):
        return f"Vistoria - {self.cliente.nome_fantasia} - {self.data}"


class VistoriaEquipamento(models.Model):
    vistoria = models.ForeignKey(
        Vistoria, on_delete=models.CASCADE, related_name='equipamentos_vistoriados'
    )
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE)

    vistoriado_em = models.DateTimeField(auto_now_add=True)

    status_final = models.CharField(
        max_length=20, choices=Equipamento.STATUS_CHOICES
    )

    observacoes = models.TextField(blank=True)

    class Meta:
        # Removemos o unique_together!
        ordering = ['-vistoriado_em']

    def __str__(self):
        return f"{self.equipamento.nome} - {self.vistoria}"


class AvaliacaoParametro(models.Model):
    vistoria_equipamento = models.ForeignKey(
        VistoriaEquipamento, on_delete=models.CASCADE, related_name='avaliacoes'
    )
    parametro = models.ForeignKey(ParametroEquipamento, on_delete=models.CASCADE)

    SITUACAO_CHOICES = (
        ('ok', 'OK'),
        ('danificado', 'Danificado'),
    )

    GRAVIDADE_CHOICES = (
        ('leve', 'Leve'),
        ('medio', 'Médio'),
        ('grave', 'Grave'),
    )

    situacao = models.CharField(max_length=20, choices=SITUACAO_CHOICES)
    gravidade = models.CharField(
        max_length=10,
        choices=GRAVIDADE_CHOICES,
        blank=True,
        null=True,
        help_text="Gravidade do problema, se danificado"
    )
    observacoes = models.TextField(blank=True)

    class Meta:
        unique_together = ('vistoria_equipamento', 'parametro')

    def clean(self):
        if self.situacao == 'danificado' and not self.gravidade:
            raise ValidationError("Gravidade é obrigatória para itens danificados.")

    def __str__(self):
        return f"{self.parametro.nome} - {self.get_situacao_display()}"
