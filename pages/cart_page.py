from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class CartPage:
    ITEM_NAMES = (By.CLASS_NAME, "inventory_item_name")
    CHECKOUT_BUTTON = (By.ID, "checkout")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def item_names(self):
        self.wait.until(EC.presence_of_element_located(self.ITEM_NAMES))
        return [el.text for el in self.driver.find_elements(*self.ITEM_NAMES)]

    def checkout(self):
        # Click, then confirm the page moved on. Retry if the click was ignored.
        for _ in range(3):
            self.wait.until(EC.element_to_be_clickable(self.CHECKOUT_BUTTON)).click()
            try:
                WebDriverWait(self.driver, 4).until(EC.url_contains("checkout-step-one"))
                return
            except TimeoutException:
                continue
        raise AssertionError("Clicking Checkout never opened checkout-step-one")