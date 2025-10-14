import time

from .pages.login_page import LoginPage


def test_login_e_lista_colaboradores(driver):

    page = LoginPage(driver)
    page.open()
    time.sleep(2)
    page.login("admin", "admin123")
    time.sleep(2)
    driver.get("http://localhost:8000/colaboradores/")
    assert "Colaboradores" in driver.page_source
