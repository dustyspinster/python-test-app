from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.interactions import click


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
        click(self.driver, self.CHECKOUT_BUTTON, EC.url_contains("checkout-step-one"))
