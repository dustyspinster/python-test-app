from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.interactions import click


class ProductPage:
    """A single product's details page, reached by clicking its name on the products page."""

    # Shows "ITEM NOT FOUND" when the page's product ID doesn't exist
    NAME = (By.CSS_SELECTOR, "[data-test='inventory-item-name']")
    PRICE = (By.CSS_SELECTOR, "[data-test='inventory-item-price']")
    # Unlike the products page, these IDs don't include the product name
    ADD_TO_CART = (By.ID, "add-to-cart")
    REMOVE = (By.ID, "remove")

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def name(self) -> str:
        return self.wait.until(EC.visibility_of_element_located(self.NAME)).text

    def price(self) -> str:
        # As displayed, such as "$29.99"
        return self.wait.until(EC.visibility_of_element_located(self.PRICE)).text

    def add_to_cart(self) -> None:
        # The button turns into a Remove button once the item is in the cart
        click(self.driver, self.ADD_TO_CART, EC.presence_of_element_located(self.REMOVE))

    def cart_button_text(self) -> str:
        buttons = self.driver.find_elements(*self.ADD_TO_CART) or self.driver.find_elements(*self.REMOVE)
        return buttons[0].text if buttons else ""
