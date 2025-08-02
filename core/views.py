from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'core/home.html')

def destinos(request):
    return render(request, 'core/destinos.html')

def galeria(request):
    return render(request, 'core/galeria.html')

def sobre(request):
    return render(request, 'core/sobre.html')