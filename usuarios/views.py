from django.shortcuts import render, redirect
from .forms import UsuarioForm
from django.http import HttpResponse
from .models import Usuario

# Create your views here.
def usuario(request):
    return HttpResponse("<h1>Página do Usuário</h1>")

def registrar_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('usuarios:lista_usuarios')  # ou qualquer página que desejar
    else:
        form = UsuarioForm()

    return render(request, 'usuarios/registrar_usuario.html', {'form': form})

def lista_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios})