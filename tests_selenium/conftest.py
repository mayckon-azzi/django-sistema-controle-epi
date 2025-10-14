import os
import uuid
import tempfile
import shutil
import pytest
from dataclasses import dataclass
from django.contrib.auth.models import Permission, Group
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from app_colaboradores.models import Colaborador
from tests_selenium.pages.login_page import LoginPage

@pytest.fixture
def driver():
    opts = Options()
    if os.getenv("HEADLESS", "0") == "1":
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--remote-debugging-port=0")

    user_data_dir = tempfile.mkdtemp(prefix=f"chrome-prof-{uuid.uuid4().hex[:8]}-")
    opts.add_argument(f"--user-data-dir={user_data_dir}")

    d = webdriver.Chrome(options=opts)
    d.set_window_size(1366, 900)
    try:
        yield d
    finally:
        try:
            d.quit()
        finally:
            shutil.rmtree(user_data_dir, ignore_errors=True)


def _salt(n: int = 6) -> str:
    return uuid.uuid4().hex[:n]


@dataclass(frozen=True, slots=True)
class TestUser:
    user: object          
    username: str
    email: str
    password: str
    nome: str
    matricula: str


@pytest.fixture
def user_with_perms(db, django_user_model):
    """
    Uso:
        u = user_with_perms(
            perms=["app_colaboradores.view_colaborador"],
            groups=["Colaborador"],
            nome="Maria da Silva",         
            matricula="C123"               
        )
    Retorna: TestUser (com .user, .username, .email, .password, .nome, .matricula)
    """
    def _make(
        perms=None,
        groups=None,
        is_staff: bool = False,
        is_superuser: bool = False,
        prefix: str = "user",
        nome: str | None = None,
        matricula: str | None = None,
        email_domain: str = "teste.com",
        
    ) -> TestUser:
        s = _salt()
        username = f"{prefix}_{s}"
        email = f"{username}@{email_domain}"
        password = f"Senha@{s}"

        user = django_user_model.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=is_staff,
            is_superuser=is_superuser,
        )

        if groups:
            for gname in groups:
                g, _ = Group.objects.get_or_create(name=gname)
                user.groups.add(g)
        if perms:
            for label_codename in perms:
                app_label, codename = label_codename.split(".", 1)
                perm = Permission.objects.get(
                    content_type__app_label=app_label,
                    codename=codename
                )
                user.user_permissions.add(perm)
        user.save()

        _nome = nome or f"User{s}"
        _matricula = matricula or f"C{s.upper()}"

        colab, _ = Colaborador.objects.get_or_create(
            user=user,
            defaults={
                "nome": _nome,
                "matricula": _matricula,
                "email": email,
            },
        )
        
        updated = False
        if colab.nome != _nome:
            colab.nome = _nome; updated = True
        if colab.matricula != _matricula:
            colab.matricula = _matricula; updated = True
        if colab.email != email:
            colab.email = email; updated = True
        if updated:
            colab.save(update_fields=["nome", "matricula", "email"])

        return TestUser(
            user=user,
            username=username,
            email=email,
            password=password,
            nome=colab.nome,
            matricula=colab.matricula,
        )

    return _make

@pytest.fixture
def auth_driver(driver, user_with_perms):
    """
    Devolve o driver JÁ LOGADO com um usuário que tem permissões básicas.
    Ajuste a lista de perms/grupos conforme sua necessidade por default.
    """
    u = user_with_perms(perms=[
        "app_colaboradores.view_colaborador",
        "app_epis.view_tipoepi",      
        "app_entregas.view_entrega",  
    ], groups=["Colaborador"])

    LoginPage(driver).ensure_logged_in(u.username, u.password)
    return driver, u  
