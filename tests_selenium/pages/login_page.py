from selenium.webdriver.common.by import By


class LoginPage:
    URL = "http://localhost:8000/accounts/login/"
    USER = (By.ID, "id_username")
    PASS = (By.ID, "id_password")
    SUBMIT = (By.CSS_SELECTOR, "button[type='submit']")

    def __init__(self, driver):
        self.driver = driver

    def open(self):
        self.driver.get(self.URL)

    def login(self, username, password):
        self.driver.find_element(*self.USER).send_keys(username)
        self.driver.find_element(*self.PASS).send_keys(password)
        self.driver.find_element(*self.SUBMIT).click()
