from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.interactions import click, type_text


class CheckoutPage:
    URL = "https://www.saucedemo.com/checkout-step-one.html"
    OVERVIEW_URL = "https://www.saucedemo.com/checkout-step-two.html"

    FIRST_NAME = (By.ID, "first-name")
    LAST_NAME = (By.ID, "last-name")
    POSTAL_CODE = (By.ID, "postal-code")
    CONTINUE_BUTTON = (By.ID, "continue")
    FINISH_BUTTON = (By.ID, "finish")
    CANCEL_BUTTON = (By.ID, "cancel")
    ERROR = (By.CSS_SELECTOR, "[data-test='error']")
    CONFIRMATION = (By.CLASS_NAME, "complete-header")
    # The order overview's summary lines, such as "Item total: $39.98"
    ITEM_TOTAL = (By.CSS_SELECTOR, "[data-test='subtotal-label']")
    TAX = (By.CSS_SELECTOR, "[data-test='tax-label']")
    TOTAL = (By.CSS_SELECTOR, "[data-test='total-label']")

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def fill_information(self, first: str, last: str, postal: str) -> None:
        type_text(self.driver, self.FIRST_NAME, first)
        type_text(self.driver, self.LAST_NAME, last)
        type_text(self.driver, self.POSTAL_CODE, postal)
        # Continue either moves on to step two or shows a validation error
        click(
            self.driver,
            self.CONTINUE_BUTTON,
            lambda d: "checkout-step-two" in d.current_url or d.find_elements(*self.ERROR),
        )

    def enter_last_name(self, last: str) -> None:
        # Raises AssertionError if the field doesn't keep the text, even when set via JavaScript
        type_text(self.driver, self.LAST_NAME, last)

    def last_name(self) -> str:
        return self.driver.find_element(*self.LAST_NAME).get_attribute("value")

    def finish(self) -> None:
        click(self.driver, self.FINISH_BUTTON, EC.url_contains("checkout-complete"))

    def cancel(self) -> None:
        # Cancel on the order overview returns to the products page, keeping the cart
        click(self.driver, self.CANCEL_BUTTON, EC.url_contains("inventory"))

    def error_message(self) -> str:
        return self.wait.until(EC.visibility_of_element_located(self.ERROR)).text

    def confirmation_text(self) -> str:
        return self.wait.until(EC.visibility_of_element_located(self.CONFIRMATION)).text

    def _amount(self, locator: tuple[str, str]) -> str:
        # "Item total: $39.98" -> "$39.98"
        return self.wait.until(EC.visibility_of_element_located(locator)).text.rsplit(" ", 1)[-1]

    def item_total(self) -> str:
        return self._amount(self.ITEM_TOTAL)

    def tax(self) -> str:
        return self._amount(self.TAX)

    def total(self) -> str:
        return self._amount(self.TOTAL)
