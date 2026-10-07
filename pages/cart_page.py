from selenium.webdriver.common.by import By


class CartPage:
    ITEM_NAMES = (By.CLASS_NAME, "inventory_item_name")
    CHECKOUT_BUTTON = (By.ID, "checkout")

    def __init__(self, driver):
        self.driver = driver

    def item_names(self):
        return [el.text for el in self.driver.find_elements(*self.ITEM_NAMES)]

    def checkout(self):
        self.driver.find_element(*self.CHECKOUT_BUTTON).click()