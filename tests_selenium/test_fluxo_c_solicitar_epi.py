# tests_selenium/test_fluxo_solicitar_epi.py
import time
import uuid

import pytest
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app_colaboradores.models import Colaborador
from app_epis.models import EPI, CategoriaEPI


@pytest.mark.django_db(transaction=True)
def test_fluxo_solicitar_epi(driver, live_server, user_with_perms, set_input, choose_option):
    salt = uuid.uuid4().hex[:6]
    admin = user_with_perms(
        perms=[
            "app_entregas.add_solicitacao",
            "app_entregas.view_solicitacao",
        ],
        groups=["colaborador"],
    )

    Colaborador.objects.create(
        user=admin,
        nome=f"User {salt}",
        email=f"user_{salt}@teste.com",
        matricula=f"M{salt.upper()}",
        ativo=True,
    )

    cat, _ = CategoriaEPI.objects.get_or_create(nome="Capacetes")
    epi = EPI.objects.create(
        codigo=f"CAP-{salt.upper()}",
        nome="Capacete de Segurança",
        categoria=cat,
        tamanho="U",
        ativo=True,
        estoque=10,
        estoque_minimo=1,
    )

    login_url = live_server.url + reverse("app_colaboradores:entrar")
    criar_solic_url = live_server.url + reverse("app_entregas:criar_solicitacao")
    minhas_solic_url = live_server.url + reverse("app_entregas:minhas_solicitacoes")

    driver.maximize_window()
    driver.get(login_url)
    time.sleep(1)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))
    set_input((By.NAME, "username"), admin.username)
    time.sleep(1)
    set_input((By.NAME, "password"), admin.plain_password)
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(1)

    driver.get(criar_solic_url)
    time.sleep(1)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "epi")))
    choose_option((By.NAME, "epi"), value=str(epi.pk))
    time.sleep(1)
    set_input((By.NAME, "quantidade"), "1")
    time.sleep(1)
    driver.find_element(By.ID, "btn-confirmar-solicitacao-epi").click()
    time.sleep(1)

    driver.get(minhas_solic_url)
    time.sleep(1)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(1)

    html = driver.page_source.lower()
    assert "solicita" in html
    assert "capacete de segurança" in html
    time.sleep(2)
