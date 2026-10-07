from selenium.webdriver.common.by import By


class InventoryPage:
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")
    CART_LINK = (By.CLASS_NAME, "shopping_cart_link")

    def __init__(self, driver):
        self.driver = driver

    def add_to_cart(self, product_id):
        self.driver.find_element(By.ID, f"add-to-cart-{product_id}").click()

    def remove_from_cart(self, product_id):
        self.driver.find_element(By.ID, f"remove-{product_id}").click()

    def cart_count(self):
        # The badge disappears when the cart is empty, so use find_elements
        badges = self.driver.find_elements(*self.CART_BADGE)
        return int(badges[0].text) if badges else 0

    def open_cart(self):
        self.driver.find_element(*self.CART_LINK).click()