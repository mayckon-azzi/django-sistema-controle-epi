# tests_selenium/test_register_then_login.py
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests_selenium.pages.register_page import RegisterPage
from tests_selenium.pages.login_page import LoginPage
import os

BASE = os.getenv("BASE_URL", "http://localhost:8000")

def test_fluxo_criar_conta_e_fazer_login(driver, user_with_perms):
    u = user_with_perms(perms=["app_colaboradores.view_colaborador"])

    LoginPage(driver).login(u.username, u.password)
    WebDriverWait(driver, 10).until(EC.url_contains("/"))  

    driver.get(f"{BASE}/colaboradores/")
    assert "Colaboradores" in driver.page_source
