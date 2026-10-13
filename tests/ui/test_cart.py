from pytest_bdd import parsers, scenarios, then, when

from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage, product_id

scenarios("features/cart.feature")


@when(parsers.parse('I remove "{product}" from my cart'))
def remove_product(browser, product):
    InventoryPage(browser).remove_from_cart(product_id(product))


@then(parsers.parse('my cart lists "{product}"'))
def cart_lists(browser, product):
    assert product in CartPage(browser).item_names()
