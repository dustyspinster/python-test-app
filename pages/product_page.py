from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class ProductPage:
    """A single product's details page, reached by clicking its name on the products page."""

    # Shows "ITEM NOT FOUND" when the page's product ID doesn't exist
    NAME = (By.CSS_SELECTOR, "[data-test='inventory-item-name']")

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def name(self) -> str:
        return self.wait.until(EC.visibility_of_element_located(self.NAME)).text
