import time

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .pages.register_page import RegisterPage
from .pages.login_page import LoginPage


def test_fluxo_criar_conta_e_fazer_login(driver, user_with_perms):
    """
    Fluxo: home -> Entrar -> Criar conta -> preencher -> Cadastrar
    Valida: redireciona para login com mensagem de sucesso.
    """
    
    u = user_with_perms(perms=["app_colaboradores.view_colaborador"])
    
    page = RegisterPage(driver)
    page.open_home()
    time.sleep(1)
    
    page.click_entrar()
    time.sleep(1)
    
    page.click_criar_conta()
    time.sleep(1)
    
    assert "registrar" in driver.current_url or "register" in driver.current_url
    page.fill_form(u.username, u.email, u.nome, u.matricula, u.password)
    time.sleep(1)
    
    page.submit()
    time.sleep(1)
    
    WebDriverWait(driver, 10).until(EC.url_contains("/colaboradores/login/"))
    assert "/colaboradores/login/" in driver.current_url

    page_text = driver.page_source
    assert "Cadastro realizado com sucesso" in page_text or "Faça login para continuar" in page_text
    
    page = LoginPage(driver)
    time.sleep(1)
    page.login(u.username, u.password)
    time.sleep(1)
    driver.get("http://localhost:8000/epis/")
    assert "Catálogo de EPIs" in driver.page_source
    
    time.sleep(2)
