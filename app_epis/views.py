from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from .models import EPI, CategoriaEPI

def lista(request):
    q = request.GET.get("q", "").strip()
    categoria_id = request.GET.get("categoria", "")

    qs = EPI.objects.select_related("categoria").all()
    if q:
        qs = qs.filter(Q(nome__icontains=q) | Q(codigo__icontains=q) | Q(categoria__nome__icontains=q))
    if categoria_id:
        qs = qs.filter(categoria_id=categoria_id)

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "epis": page_obj.object_list,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "q": q,
        "categoria_id": categoria_id,
        "categorias": CategoriaEPI.objects.all(),
    }
    return render(request, "app_epis/pages/list.html", context)
