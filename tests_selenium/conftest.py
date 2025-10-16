# test_selenium/conftest.py
import os
import shutil
import sys
import tempfile
import uuid

import pytest
from django.contrib.auth.models import Group, Permission
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select as SeleniumSelect
from selenium.webdriver.support.ui import WebDriverWait

CTRL_KEY = Keys.COMMAND if sys.platform == "darwin" else Keys.CONTROL

# -----------------------------
# Selenium WebDriver (session)
# -----------------------------


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
    d.set_window_size(1200, 900)
    try:
        yield d
    finally:
        try:
            d.quit()
        finally:
            shutil.rmtree(user_data_dir, ignore_errors=True)


# -----------------------------
# Função para gerar parte de um Hashcode
# -----------------------------


def _salt(n: int = 6) -> str:
    return uuid.uuid4().hex[:n]


# -----------------------------
# Dados para registro de usuário
# -----------------------------


@pytest.fixture
def registration_data():
    """
    Gera dados únicos para registro de usuários.
    Retorna dict com username, email, senha, nome, matricula.
    """
    s = _salt()
    username = f"user_{s}"
    email = f"{username}@teste.com"
    nome = f"Usuário {s}"
    matricula = f"M{s.upper()}"
    senha = f"Senha@{s}"
    return {
        "username": username,
        "email": email,
        "nome": nome,
        "matricula": matricula,
        "senha": senha,
    }


# -----------------------------
# Usuário com permissões
# -----------------------------


@pytest.fixture
def user_with_perms(db, django_user_model):
    """
    Cria usuário e aplica permissões/grupos.
    Retorna um objeto User com atributo extra `plain_password` para uso no Selenium.

    Uso:
        u = user_with_perms(perms=["app_epis.add_epi", "app_epis.view_epi"])
    """

    def _make(perms=None, groups=None, is_staff=False, is_superuser=False, prefix="user"):
        s = _salt()
        username = f"{prefix}_{s}"
        email = f"{username}@teste.com"
        plain_password = f"Senha@{s}"

        user = django_user_model.objects.create_user(
            username=username,
            email=email,
            password=plain_password,
            is_staff=is_staff,
            is_superuser=is_superuser,
        )

        if perms:
            for label_codename in perms:
                app_label, codename = label_codename.split(".")
                perm = Permission.objects.filter(
                    content_type__app_label=app_label, codename=codename
                ).first()
                if not perm:
                    raise RuntimeError(f"Permissão não encontrada: {label_codename}")
                user.user_permissions.add(perm)

        if groups:
            for gname in groups:
                grp, _ = Group.objects.get_or_create(name=gname)
                user.groups.add(grp)

        user.save()

        user.plain_password = plain_password
        return user

    return _make


# -----------------------------
# Apagar dados nos input
# -----------------------------


@pytest.fixture
def set_input(driver):
    """
    Helper p/ inputs: espera ficar clicável, limpa e digita.
    Uso:
        set_input((By.NAME, "estoque"), "5")
    """

    def _set(by, value, timeout=10, js_fallback=True, fire_events=True):
        el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(by))
        el.click()

        el.send_keys(CTRL_KEY, "a")
        el.send_keys(Keys.DELETE)

        if js_fallback and el.get_attribute("value"):
            driver.execute_script(
                "arguments[0].value='';"
                "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));",
                el,
            )

        el.send_keys(str(value))

        if fire_events:
            driver.execute_script(
                "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));",
                el,
            )
        return el

    return _set


# -----------------------------
# Select correto no formulário
# -----------------------------


@pytest.fixture
def choose_option(driver):
    def _choose(by, *, text=None, value=None, index=None, timeout=10):
        el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(by))
        sel = SeleniumSelect(el)

        if text is not None:
            for opt in sel.options:
                if opt.text.strip() == text:
                    opt.click()
                    break
            else:
                raise AssertionError(f'Texto exato "{text}" não encontrado.')
        elif value is not None:
            sel.select_by_value(value)
        elif index is not None:
            sel.select_by_index(index)
        else:
            raise ValueError("Informe text, value ou index.")
        return el

    return _choose
