from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC

from pages.interactions import Condition, Locator, click
from pages.login_page import LoginPage


class Menu:
    """The side menu behind the button at the top left of every page once logged in."""

    OPEN_BUTTON = (By.ID, "react-burger-menu-btn")
    LOGOUT = (By.ID, "logout_sidebar_link")
    RESET = (By.ID, "reset_sidebar_link")
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver

    def _choose(self, link: Locator, done: Condition) -> None:
        # The menu slides open, so wait for the link to be visible before clicking it
        click(self.driver, self.OPEN_BUTTON, EC.visibility_of_element_located(link))
        click(self.driver, link, done)

    def log_out(self) -> None:
        self._choose(self.LOGOUT, EC.presence_of_element_located(LoginPage.LOGIN_BUTTON))

    def reset_app_state(self) -> None:
        # Resetting clears the cart, so wait for the cart badge to disappear
        self._choose(self.RESET, EC.invisibility_of_element_located(self.CART_BADGE))
