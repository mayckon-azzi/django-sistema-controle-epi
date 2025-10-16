# tests_selenium/test_fluxo_almoxarife_atender_solicitacao.py
import time
import uuid

import pytest
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app_colaboradores.models import Colaborador
from app_entregas.models import Entrega
from app_epis.models import EPI, CategoriaEPI


@pytest.mark.django_db(transaction=True)
def test_almoxarife_aprova_e_atende_solicitacao(
    driver, live_server, user_with_perms, set_input, choose_option
):
    salt = uuid.uuid4().hex[:6]

    almox = user_with_perms(
        perms=[
            "app_entregas.view_solicitacao",
            "app_entregas.change_solicitacao",
            "app_entregas.add_entrega",
            "app_entregas.view_entrega",
        ],
        groups=["almoxarife", "Almoxarife"],
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

    solicitante = Colaborador.objects.create(
        nome=f"Bruno {salt}",
        email=f"bruno_{salt}@empresa.com",
        matricula=f"B{salt.upper()}",
        ativo=True,
    )

    url_login = live_server.url + reverse("app_colaboradores:entrar")
    url_gerenciar = live_server.url + reverse("app_entregas:solicitacoes_gerenciar")

    driver.maximize_window()
    driver.get(url_login)
    time.sleep(1)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))
    set_input((By.NAME, "username"), almox.username)
    time.sleep(1)
    set_input((By.NAME, "password"), almox.plain_password)
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(1)

    driver.get(url_gerenciar)
    time.sleep(1)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(1)

    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "btn-aprovar-solicitacao-epi-enviada"))
    ).click()
    time.sleep(1)

    try:
        alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
        alert.accept()
        time.sleep(1)
    except Exception:
        pass

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "status")))
    time.sleep(1)
    choose_option((By.NAME, "status"), text="Aprovada")
    time.sleep(1)
    driver.find_element(By.XPATH, "//button[contains(., 'Filtrar')]").click()
    time.sleep(1)

    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "btn-atender-solicitacao-epi-enviada"))
    ).click()
    time.sleep(1)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//button[contains(., 'Confirmar') and contains(., 'Entrega')]")
        )
    )
    time.sleep(1)
    driver.find_element(
        By.XPATH, "//button[contains(., 'Confirmar') and contains(., 'Entrega')]"
    ).click()
    time.sleep(1)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(1)

    assert Entrega.objects.filter(colaborador=solicitante, epi=epi, quantidade=1).exists()
    time.sleep(2)
