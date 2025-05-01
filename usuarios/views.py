from django.shortcuts import render, get_object_or_404, redirect
from .models import Usuario
from .forms import UsuarioForm

# A ideia é exibir uma tabela com os usuários cadastrados no sistema
def listar_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/listar_usuarios.html', {'usuarios': usuarios})


def cadastrar_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('usuarios:listar_usuarios')
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/cadastrar_usuario.html', {'form': form})


def editar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('usuarios:listar_usuarios')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'usuarios/editar_usuario.html', {'form': form, 'usuario': usuario})


def excluir_usuario(request, pk):
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, pk=pk)
        usuario.delete()
    return redirect('usuarios:listar_usuarios')


def detalhes_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    return render(request, 'usuarios/detalhes_usuario.html', {'usuario': usuario})