from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.interactions import click, type_text


class CheckoutPage:
    FIRST_NAME = (By.ID, "first-name")
    LAST_NAME = (By.ID, "last-name")
    POSTAL_CODE = (By.ID, "postal-code")
    CONTINUE_BUTTON = (By.ID, "continue")
    FINISH_BUTTON = (By.ID, "finish")
    ERROR = (By.CSS_SELECTOR, "[data-test='error']")
    CONFIRMATION = (By.CLASS_NAME, "complete-header")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def fill_information(self, first, last, postal):
        type_text(self.driver, self.FIRST_NAME, first)
        type_text(self.driver, self.LAST_NAME, last)
        type_text(self.driver, self.POSTAL_CODE, postal)
        # Continue either moves on to step two or shows a validation error
        click(
            self.driver,
            self.CONTINUE_BUTTON,
            lambda d: "checkout-step-two" in d.current_url or d.find_elements(*self.ERROR),
        )

    def finish(self):
        click(self.driver, self.FINISH_BUTTON, EC.url_contains("checkout-complete"))

    def error_message(self):
        return self.wait.until(EC.visibility_of_element_located(self.ERROR)).text

    def confirmation_text(self):
        return self.wait.until(EC.visibility_of_element_located(self.CONFIRMATION)).text
