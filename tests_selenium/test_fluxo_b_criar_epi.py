import time

import pytest
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app_epis.models import CategoriaEPI


@pytest.mark.django_db(transaction=True)
def test_fluxo_criar_epi(driver, user_with_perms, live_server, set_input, choose_option):
    """
    Fluxo: login -> abrir /epis/novo/ -> criar EPI -> ver na lista.
    """
    admin = user_with_perms(
        perms=[
            "app_epis.add_epi",
            "app_epis.view_epi",
            "app_colaboradores.view_colaborador",
        ]
    )

    login_url = live_server.url + reverse("app_colaboradores:entrar")

    driver.maximize_window()
    driver.get(login_url)
    time.sleep(2)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))
    driver.find_element(By.NAME, "username").send_keys(admin.username)
    time.sleep(1)
    driver.find_element(By.NAME, "password").send_keys(admin.plain_password)
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(2)

    cat, _ = CategoriaEPI.objects.get_or_create(nome="Luvas")
    cat_value = str(cat.pk)

    criar_epi_url = live_server.url + reverse("app_epis:criar")
    driver.get(criar_epi_url)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "codigo")))

    codigo = f"LUV-{int(time.time())}"
    set_input((By.NAME, "codigo"), codigo)
    time.sleep(1)

    set_input((By.NAME, "nome"), "Luvas antiderrapante")
    time.sleep(1)

    choose_option((By.NAME, "categoria"), value=cat_value)
    time.sleep(1)

    set_input((By.NAME, "tamanho"), "M")
    time.sleep(1)

    set_input((By.NAME, "estoque"), "5")
    time.sleep(1)

    set_input((By.NAME, "estoque_minimo"), "1")
    time.sleep(1)

    driver.find_element(By.ID, "btn-salvar-epi").click()
    time.sleep(1)

    lista_url = live_server.url + reverse("app_epis:lista")
    driver.get(lista_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(5)

    html = driver.page_source.lower()
    assert "luva antiderrapante" in html or codigo.lower() in html
