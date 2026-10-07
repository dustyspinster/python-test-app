from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.interactions import click


class InventoryPage:
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")
    CART_LINK = (By.CLASS_NAME, "shopping_cart_link")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def add_to_cart(self, product_id):
        # The button turns into a Remove button once the item is in the cart
        locator = (By.ID, f"add-to-cart-{product_id}")
        click(self.driver, locator, EC.presence_of_element_located((By.ID, f"remove-{product_id}")))

    def remove_from_cart(self, product_id):
        locator = (By.ID, f"remove-{product_id}")
        click(self.driver, locator, EC.presence_of_element_located((By.ID, f"add-to-cart-{product_id}")))

    def cart_count(self):
        # The badge disappears when the cart is empty, so use find_elements
        badges = self.driver.find_elements(*self.CART_BADGE)
        return int(badges[0].text) if badges else 0

    def open_cart(self):
        click(self.driver, self.CART_LINK, EC.url_contains("cart.html"))
