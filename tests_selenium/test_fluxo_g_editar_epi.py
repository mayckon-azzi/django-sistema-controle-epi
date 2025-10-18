import time
import uuid

import pytest
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC  
from selenium.webdriver.support.ui import WebDriverWait
from app_epis.models import EPI, CategoriaEPI



@pytest.mark.django_db(transaction=True)
def test_editar_epi(driver,live_server,user_with_perms,set_input,choose_option):
  
  salt = uuid.uuid4().hex[:6]
  
  almox = user_with_perms(
    perms=[
      "app_epis.view_epi",
      "app_epis.change_epi",
      ],
    groups=["almoxarife","Almoxarife"], 
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
  
  url_login = live_server.url + reverse("app_colaboradores:entrar")
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



  lista_url = live_server.url + reverse("app_epis:lista")
  driver.get(lista_url)

 # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "Catálogo de EPIs")))
  time.sleep(1)

  driver.find_element(By.ID, "btn-editar-epi").click()
  editar_url = live_server.url + reverse("app_epis:editar", args=[epi.pk])
  driver.get(editar_url)
  
  codigo = f"LUV-{int(time.time())}"
  cat_value = str(cat.pk)
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

