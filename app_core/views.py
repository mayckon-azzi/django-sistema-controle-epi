from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect

# Create your views here.
def home(request):
    return render(request, "app_core/pages/home.html")

def testar_mensagens(request):
    messages.success(request, "Operação realizada com sucesso.")
    messages.info(request, "Informação de exemplo.")
    messages.warning(request, "Aviso de exemplo.")
    messages.error(request, "Erro de exemplo.")
    return redirect("app_core:home")
