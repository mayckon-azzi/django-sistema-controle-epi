from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class RegisterPage:
    HOME_URL = "http://localhost:8000/"
    LOGIN_URL = "http://localhost:8000/colaboradores/login/"
    REGISTER_URL = "http://localhost:8000/colaboradores/registrar/"

    USER = (By.ID, "id_username")
    EMAIL = (By.ID, "id_email")
    NOME = (By.ID, "id_nome")
    MATRICULA = (By.ID, "id_matricula")
    PASS1 = (By.ID, "id_password1")
    PASS2 = (By.ID, "id_password2")

    SUBMIT = (By.CSS_SELECTOR, "button[type='submit'],input[type='submit']")

    def __init__(self, driver, timeout=10):
        self.d = driver
        self.w = WebDriverWait(driver, timeout)

    def open_home(self):
        self.d.get(self.HOME_URL)

    def click_entrar(self):
        try:
            self.w.until(EC.element_to_be_clickable((By.LINK_TEXT, "Entrar"))).click()
        except Exception:
            self.d.get(self.LOGIN_URL)

    def click_criar_conta(self):
        for locator in [
            (By.LINK_TEXT, "Criar conta"),
            (By.PARTIAL_LINK_TEXT, "Criar"),
            (By.PARTIAL_LINK_TEXT, "Registrar"),
        ]:
            try:
                self.w.until(EC.element_to_be_clickable(locator)).click()
                return
            except Exception:
                pass
        self.d.get(self.REGISTER_URL)

    def fill_form(self, username, email, nome, matricula, senha):
        self.w.until(EC.visibility_of_element_located(self.USER)).send_keys(username)
        self.d.find_element(*self.EMAIL).send_keys(email)
        self.d.find_element(*self.NOME).send_keys(nome)
        self.d.find_element(*self.MATRICULA).send_keys(matricula)
        self.d.find_element(*self.PASS1).send_keys(senha)
        self.d.find_element(*self.PASS2).send_keys(senha)

    def submit(self):
        self.d.find_element(*self.SUBMIT).click()
