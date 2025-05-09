import random
import string
from django.shortcuts import render, get_object_or_404, redirect
from .models import Usuario
from .forms import UsuarioForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q

# ==== Login =====
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Garante que o usuário tenha um objeto Usuario
            try:
                user.usuario
            except Usuario.DoesNotExist:
                Usuario.objects.create(user=user)

            return redirect('usuarios:listar_usuarios')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'usuarios/login.html')


# ===== Cadastrar usuário =====
# Restringindo o acesso à view de cadastro apenas para administradores
def eh_admin(user):
    return user.is_authenticated and (user.is_superuser or (hasattr(user, 'usuario') and user.usuario.perfil == 'admin'))

# Gerar senha aleatória para o usuário
def gerar_senha_aleatoria(tamanho=8):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(tamanho))

@user_passes_test(eh_admin)
def cadastrar_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            # Gera senha aleatória
            senha_gerada = gerar_senha_aleatoria()

            # Cria o usuário do Django
            usuario_django = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=senha_gerada
            )

            # Cria o perfil extendido
            usuario = form.save(commit=False)
            usuario.user = usuario_django
            usuario.save()

            # Mensagem de sucesso
            messages.success(request, f'Usuário criado com sucesso! A senha gerada foi: {senha_gerada}')
            return redirect('usuarios:listar_usuarios')
    else:
        form = UsuarioForm()

    return render(request, 'usuarios/cadastrar_usuario.html', {'form': form})


# ===== Listar usuários =====
def listar_usuarios(request):
    busca = request.GET.get('busca', '')
    ordenar_por = request.GET.get('ordenar_por', 'nome_completo')

    usuarios = Usuario.objects.all()

    if busca:
        usuarios = usuarios.filter(
            Q(nome_completo__icontains=busca) |
            Q(cpf__icontains=busca) |
            Q(email__icontains=busca)
        )

    if ordenar_por in ['nome_completo', 'cpf', 'email', 'perfil']:
        usuarios = usuarios.order_by(ordenar_por)

    return render(request, 'usuarios/listar_usuarios.html', {
        'usuarios': usuarios,
        'busca': busca,
        'ordenar_por': ordenar_por,
    })


# ===== Editar usuário =====
@user_passes_test(eh_admin)
def editar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES, instance=usuario)

        if form.is_valid():
            usuario = form.save()

            nova_senha = request.POST.get('nova_senha')
            if nova_senha:
                usuario.user.set_password(nova_senha)
                usuario.user.save()
                messages.success(request, f'Usuário atualizado com nova senha: {nova_senha}')
            else:
                messages.success(request, 'Usuário atualizado com sucesso.')

            return redirect('usuarios:listar_usuarios')
        else:
            print(form.errors)  # DEBUG TEMPORÁRIO
    else:
        form = UsuarioForm(instance=usuario)

    return render(request, 'usuarios/editar_usuario.html', {'form': form, 'usuario': usuario})


# ===== Excluir usuário =====
def excluir_usuario(request, pk):
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, pk=pk)
        usuario.delete()
    return redirect('usuarios:listar_usuarios')


# ===== Detalhes usuário =====
def detalhes_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    return render(request, 'usuarios/detalhes_usuario.html', {'usuario': usuario})