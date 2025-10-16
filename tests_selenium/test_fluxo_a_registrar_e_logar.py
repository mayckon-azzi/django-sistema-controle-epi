# tests_selenium/test_registrar_e_logar.py
import time

import pytest
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@pytest.mark.django_db(transaction=True)
def test_fluxo_criar_conta_e_fazer_login(driver, live_server, set_input, registration_data):
    user = registration_data

    url_register = live_server.url + reverse("app_colaboradores:registrar")
    url_epis_lista = live_server.url + reverse("app_epis:lista")

    driver.maximize_window()
    driver.get(url_register)
    time.sleep(0.5)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))

    set_input((By.NAME, "username"), user["username"])
    time.sleep(0.5)
    set_input((By.NAME, "email"), user["email"])
    time.sleep(1)
    set_input((By.NAME, "nome"), user["nome"])
    time.sleep(1)
    set_input((By.NAME, "matricula"), user["matricula"])
    time.sleep(1)

    senha_campos = driver.find_elements(By.NAME, "password")
    if senha_campos:
        set_input((By.NAME, "password"), user["senha"])
    else:
        set_input((By.NAME, "password1"), user["senha"])
        time.sleep(1)
        set_input((By.NAME, "password2"), user["senha"])
    time.sleep(1)

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(1)

    WebDriverWait(driver, 10).until(EC.url_contains("/colaboradores/login/"))
    time.sleep(1)
    assert "/colaboradores/login/" in driver.current_url

    html = driver.page_source.lower()
    assert "cadastro realizado" in html or "faça login" in html or "sucesso" in html
    time.sleep(1)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))
    set_input((By.NAME, "username"), user["username"])
    time.sleep(1)
    set_input((By.NAME, "password"), user["senha"])
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(1)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(1)

    driver.get(url_epis_lista)
    time.sleep(1)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(1)

    html = driver.page_source.lower()
    assert "epi" in html or "epis" in html or "catálogo" in html
    time.sleep(2)
