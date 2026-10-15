from pytest_bdd import parsers, scenarios, then

from pages.cart_page import CartPage

scenarios("features/cart.feature")


@then(parsers.parse('my cart lists "{product}"'))
def cart_lists(browser, product):
    assert product in CartPage(browser).item_names()
