from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.interactions import click


class CartPage:
    # Only the cart (and checkout overview) render this list; the inventory page doesn't
    CART_LIST = (By.CLASS_NAME, "cart_list")
    # The inventory page uses the same class for its item names, so only search inside CART_LIST
    ITEM_NAMES = (By.CLASS_NAME, "inventory_item_name")
    CHECKOUT_BUTTON = (By.ID, "checkout")

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def item_names(self) -> list[str]:
        cart = self.wait.until(EC.presence_of_element_located(self.CART_LIST))
        return [el.text for el in cart.find_elements(*self.ITEM_NAMES)]

    def checkout(self) -> None:
        click(self.driver, self.CHECKOUT_BUTTON, EC.url_contains("checkout-step-one"))
