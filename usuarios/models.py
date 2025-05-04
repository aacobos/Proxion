# usuarios/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='usuario', null=True, blank=True)

    PERFIS = (
        ('admin', 'Administrador'),
        ('analista', 'Analista'),
    )

    nome_completo = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14, unique=True)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    foto = models.ImageField(upload_to='usuarios/fotos/', null=True, blank=True)
    assinatura = models.ImageField(upload_to='usuarios/assinaturas/', null=True, blank=True)
    perfil = models.CharField(max_length=10, choices=PERFIS, default='analista')

    data_cadastro = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return self.nome_completo
