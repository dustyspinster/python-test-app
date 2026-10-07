import pytest
from selenium.webdriver.support.ui import WebDriverWait

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage

BACKPACK = "sauce-labs-backpack"
CHECKOUT_URL = "https://www.saucedemo.com/checkout-step-one.html"


def add_backpack(driver):
    inventory = InventoryPage(driver)
    inventory.add_to_cart(BACKPACK)
    WebDriverWait(driver, 10).until(lambda d: inventory.cart_count() == 1)
    return inventory


@pytest.fixture
def cart_with_item(logged_in_driver):
    # Full click-through path, used by the end-to-end test
    inventory = add_backpack(logged_in_driver)
    inventory.open_cart()
    CartPage(logged_in_driver).checkout()
    return logged_in_driver


@pytest.fixture
def checkout_form(logged_in_driver):
    # Opens the form directly, used by the validation tests
    add_backpack(logged_in_driver)
    logged_in_driver.get(CHECKOUT_URL)
    return logged_in_driver


def test_complete_checkout(cart_with_item):
    checkout = CheckoutPage(cart_with_item)
    checkout.fill_information("Test", "User", "97201")
    checkout.finish()

    assert "Thank you for your order" in checkout.confirmation_text()


@pytest.mark.parametrize(
    "first, last, postal, expected_error",
    [
        ("", "User", "97201", "First Name is required"),
        ("Test", "", "97201", "Last Name is required"),
        ("Test", "User", "", "Postal Code is required"),
    ],
)
def test_checkout_requires_all_fields(checkout_form, first, last, postal, expected_error):
    checkout = CheckoutPage(checkout_form)
    checkout.fill_information(first, last, postal)

    assert expected_error in checkout.error_message()