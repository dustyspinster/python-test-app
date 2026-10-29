from pytest_bdd import parsers, scenarios, then

# Opening a product, adding it from its details page and checking its buttons are shared steps,
# in conftest.py
from pages.inventory_page import InventoryPage
from pages.product_page import ProductPage

scenarios("features/product_details.feature")


@then(parsers.parse('the price of "{product}" is {price}'))
def list_price(browser, product, price):
    assert InventoryPage(browser).product_price(product) == price


@then(parsers.parse('the details page shows the name "{product}"'))
def details_name(browser, product):
    assert ProductPage(browser).name() == product


@then(parsers.parse("the details page shows the price {price}"))
def details_price(browser, price):
    assert ProductPage(browser).price() == price
