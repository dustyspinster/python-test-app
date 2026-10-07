from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage

BACKPACK = "sauce-labs-backpack"
BIKE_LIGHT = "sauce-labs-bike-light"


def test_add_item_updates_cart_badge(logged_in_driver):
    inventory = InventoryPage(logged_in_driver)
    inventory.add_to_cart(BACKPACK)

    assert inventory.cart_count() == 1


def test_add_two_items(logged_in_driver):
    inventory = InventoryPage(logged_in_driver)
    inventory.add_to_cart(BACKPACK)
    inventory.add_to_cart(BIKE_LIGHT)

    assert inventory.cart_count() == 2


def test_remove_item_empties_cart(logged_in_driver):
    inventory = InventoryPage(logged_in_driver)
    inventory.add_to_cart(BACKPACK)
    inventory.remove_from_cart(BACKPACK)

    assert inventory.cart_count() == 0


def test_cart_page_shows_added_item(logged_in_driver):
    inventory = InventoryPage(logged_in_driver)
    inventory.add_to_cart(BACKPACK)
    inventory.open_cart()

    assert "Sauce Labs Backpack" in CartPage(logged_in_driver).item_names()