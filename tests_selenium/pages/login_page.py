from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

class LoginPage:
    URL = f"{BASE_URL}/accounts/login/"

    USER = (By.ID, "id_username")
    PASS = (By.ID, "id_password")
    SUBMIT = (By.CSS_SELECTOR, "button[type='submit']")
    LOGOUT_LINK = (By.PARTIAL_LINK_TEXT, "Sair")  # ajuste se o seu template usar outro texto

    def __init__(self, driver, timeout=10):
        self.d = driver
        self.w = WebDriverWait(driver, timeout)

    def open(self):
        self.d.get(self.URL)

    def login(self, username, password):
        self.open()
        self.w.until(EC.visibility_of_element_located(self.USER)).send_keys(username)
        self.d.find_element(*self.PASS).send_keys(password)
        self.d.find_element(*self.SUBMIT).click()

    def ensure_logged_in(self, username, password):
        """Faz login somente se necessário."""
        self.open()
        page = self.d.page_source.lower()
        if "logout" in page or "sair" in page:
            return
        self.login(username, password)
