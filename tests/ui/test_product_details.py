from pytest_bdd import given, parsers, scenarios, then, when
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.inventory_page import InventoryPage
from pages.product_page import ProductPage

scenarios("features/product_details.feature")


@given(parsers.parse('I am on the "{page}" page'))
def on_page(browser, page):
    # Logging in lands on the products page, the only page these scenarios start from
    assert page == "products", f"No route to the {page!r} page"
    WebDriverWait(browser, 10).until(EC.url_contains("inventory"))


@then(parsers.parse('the price of "{product}" is {price}'))
def list_price(browser, product, price):
    assert InventoryPage(browser).product_price(product) == price


@when(parsers.parse('I click on "{product}"'))
def click_product(browser, product):
    InventoryPage(browser).open_product(product)


@when("I click Add to cart")
def click_add_to_cart(browser):
    ProductPage(browser).add_to_cart()


@then(parsers.parse('the details page button shows "{label}"'))
def details_button_label(browser, label):
    assert ProductPage(browser).cart_button_text() == label


@then(parsers.parse('the details page shows the name "{product}"'))
def details_name(browser, product):
    assert ProductPage(browser).name() == product


@then(parsers.parse("the details page shows the price {price}"))
def details_price(browser, price):
    assert ProductPage(browser).price() == price
