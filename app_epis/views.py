from django.shortcuts import render

# Create your views here.
def lista(request):
    return render(request, "app_epis/pages/list.html")
