import time
import uuid

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .pages.register_page import RegisterPage


def test_fluxo_criar_conta(driver):
    """
    Fluxo: home -> Entrar -> Criar conta -> preencher -> Cadastrar
    Valida: redireciona para login com mensagem de sucesso.
    """
    salt = uuid.uuid4().hex[:6]
    username = f"user_{salt}"
    email = f"{username}@teste.com"
    nome = "Usuário de Teste"
    matricula = f"C{salt.upper()}"
    senha = "Senha@12345"

    page = RegisterPage(driver)
    page.open_home()
    time.sleep(2)
    page.click_entrar()
    time.sleep(2)
    page.click_criar_conta()
    time.sleep(2)
    assert "registrar" in driver.current_url or "register" in driver.current_url
    page.fill_form(username, email, nome, matricula, senha)
    time.sleep(3)
    page.submit()
    time.sleep(2)
    WebDriverWait(driver, 10).until(EC.url_contains("/colaboradores/login/"))
    assert "/colaboradores/login/" in driver.current_url

    page_text = driver.page_source
    assert "Cadastro realizado com sucesso" in page_text or "Faça login para continuar" in page_text

    driver.save_screenshot(f"evidencia_registro_{salt}.png")
