from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


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

    def _values(self):
        return tuple(
            self.driver.find_element(*locator).get_attribute("value")
            for locator in (self.FIRST_NAME, self.LAST_NAME, self.POSTAL_CODE)
        )

    def fill_information(self, first, last, postal):
        wanted = (first, last, postal)
        locators = (self.FIRST_NAME, self.LAST_NAME, self.POSTAL_CODE)

        # Type everything, then confirm the fields kept the text. Retry if the page wiped it.
        for _ in range(3):
            try:
                for locator, text in zip(locators, wanted):
                    field = self.wait.until(EC.element_to_be_clickable(locator))
                    field.clear()
                    field.send_keys(text)
                if self._values() == wanted:
                    break
            except (StaleElementReferenceException, NoSuchElementException):
                continue
        else:
            raise AssertionError("Checkout fields did not keep the typed values")

        self._click_continue()

    def _click_continue(self):
        # Click, then confirm something happened (next page or an error). Retry if ignored.
        for _ in range(3):
            self.wait.until(EC.element_to_be_clickable(self.CONTINUE_BUTTON)).click()
            try:
                WebDriverWait(self.driver, 3).until(
                    lambda d: "checkout-step-two" in d.current_url
                    or d.find_elements(*self.ERROR)
                )
                return
            except TimeoutException:
                continue

    def finish(self):
        self.wait.until(EC.element_to_be_clickable(self.FINISH_BUTTON)).click()

    def error_message(self):
        return self.wait.until(EC.visibility_of_element_located(self.ERROR)).text

    def confirmation_text(self):
        return self.wait.until(EC.visibility_of_element_located(self.CONFIRMATION)).text