import pytest

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage

BACKPACK = "sauce-labs-backpack"


@pytest.fixture
def cart_with_item(logged_in_driver):
    inventory = InventoryPage(logged_in_driver)
    inventory.add_to_cart(BACKPACK)
    inventory.open_cart()
    CartPage(logged_in_driver).checkout()
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
def test_checkout_requires_all_fields(cart_with_item, first, last, postal, expected_error):
    checkout = CheckoutPage(cart_with_item)
    checkout.fill_information(first, last, postal)

    assert expected_error in checkout.error_message()