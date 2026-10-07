from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.interactions import click, type_text


class LoginPage:
    URL = "https://www.saucedemo.com"

    USERNAME = (By.ID, "user-name")
    PASSWORD = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR = (By.CSS_SELECTOR, "[data-test='error']")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def open(self):
        self.driver.get(self.URL)

    def login(self, username, password):
        type_text(self.driver, self.USERNAME, username)
        type_text(self.driver, self.PASSWORD, password)
        # Login either opens the inventory or shows an error
        click(
            self.driver,
            self.LOGIN_BUTTON,
            lambda d: "inventory" in d.current_url or d.find_elements(*self.ERROR),
        )

    def error_message(self):
        return self.wait.until(EC.visibility_of_element_located(self.ERROR)).text
