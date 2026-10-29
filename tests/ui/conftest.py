"""Step definitions shared by more than one UI feature file."""

import pytest
from pytest_bdd import given, parsers, then, when
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage, product_id
from pages.login_page import LoginPage
from pages.menu import Menu
from pages.product_page import ProductPage

KNOWN_BUG = pytest.mark.xfail(
    reason="Known Swag Labs bug; see Known issues in the README", raises=AssertionError, strict=True
)


def pytest_bdd_apply_tag(tag, function):
    """Turn a @known-bug tag into a strict expected failure.

    The scenario still runs, and is reported as expected to fail instead of failing the build.
    Only a failed assertion counts as the known bug; any other error still fails the test.
    strict=True makes an unexpected pass fail, so the tag gets removed once the bug is fixed.
    """
    if tag != "known-bug":
        return None
    KNOWN_BUG(function)
    return True


def pytest_configure(config):
    config.addinivalue_line("markers", "known-bug: a known Swag Labs bug; runs as a strict expected failure")


def pytest_collection_modifyitems(items):
    # A tag on an Examples table reaches only its own rows, as a plain mark that skips the hook above
    for item in items:
        if item.get_closest_marker("known-bug") and not item.get_closest_marker("xfail"):
            item.add_marker(KNOWN_BUG)


@given("I am on the login page", target_fixture="browser")
def login_page(driver):
    LoginPage(driver).open()
    return driver


# [^"]* rather than {}, so an Examples cell can be empty
@when(parsers.re(r'I log in as "(?P<username>[^"]*)" with password "(?P<password>[^"]*)"'))
def log_in(browser, username, password):
    LoginPage(browser).login(username, password)


@given(parsers.parse('I am on the "{product}" details page'))
@when(parsers.parse('I click on "{product}"'))
def open_product(browser, product):
    InventoryPage(browser).open_product(product)


@given(parsers.parse('I am on the "{page}" page'))
def on_page(browser, page):
    # Logging in lands on the products page, the only page these scenarios start from
    assert page == "products", f"No route to the {page!r} page"
    WebDriverWait(browser, 10).until(EC.url_contains("inventory"))


@when("I click Add to cart")
def click_add_to_cart(browser):
    ProductPage(browser).add_to_cart()


@then(parsers.parse('the details page button shows "{label}"'))
def details_button_label(browser, label):
    assert ProductPage(browser).cart_button_text() == label


@when(parsers.parse('I click "{label}"'))
def click_details_button(browser, label):
    page = ProductPage(browser)
    buttons = {
        "Add to cart": page.add_to_cart,
        "Remove": page.remove_from_cart,
        "Back to products": page.back_to_products,
    }
    assert label in buttons, f"No details page button labelled {label!r}"
    buttons[label]()


@given("I am logged in", target_fixture="browser")
def logged_in(logged_in_driver):
    return logged_in_driver


@given(parsers.parse("I am logged in as {username}"), target_fixture="browser")
@when(parsers.parse("I log back in as {username}"), target_fixture="browser")
def logged_in_as(driver, username):
    # All Swag Labs test users share this password
    page = LoginPage(driver)
    page.open()
    page.login(username, "secret_sauce")
    WebDriverWait(driver, 10).until(EC.url_contains("inventory"))
    return driver


@given(parsers.parse('I have added "{product}" to my cart'))
@given(parsers.parse('I have clicked add to cart on "{product}"'))
@when(parsers.parse('I add "{product}" to my cart'))
def add_product(browser, product):
    inventory = InventoryPage(browser)
    expected = inventory.cart_count() + 1
    inventory.add_to_cart(product_id(product))
    # The badge can lag behind the button; wait for it so a following page load sees the item
    WebDriverWait(browser, 10).until(lambda _: inventory.cart_count() == expected)


@given("I have also added these products to my cart")
def add_products(browser, datatable):
    # The data table's first row is its header
    for (product,) in datatable[1:]:
        add_product(browser, product)


@when("I open my cart")
def open_cart(browser):
    InventoryPage(browser).open_cart()


@then("I see the product inventory")
@then("I am taken back to the Products page")
def on_inventory(browser):
    WebDriverWait(browser, 10).until(EC.url_contains("inventory"))


@then(parsers.parse("my cart badge shows {count:d}"))
def cart_badge(browser, count):
    assert InventoryPage(browser).cart_count() == count


@given("I am on the checkout information page")
def checkout_information_page(browser):
    # Open the form directly; the full click-through path is covered by the purchase scenario
    browser.get(CheckoutPage.URL)


# [^"]* rather than {}, so an Examples cell can be empty
@when(
    parsers.re(
        r'I enter first name "(?P<first>[^"]*)", last name "(?P<last>[^"]*)"'
        r' and postal code "(?P<postal>[^"]*)"'
    )
)
def enter_details(browser, first, last, postal):
    CheckoutPage(browser).fill_information(first, last, postal)


@when("I finish my order")
def finish_order(browser):
    CheckoutPage(browser).finish()


@then(parsers.parse('I see the order confirmation "{text}"'))
def order_confirmation(browser, text):
    assert text in CheckoutPage(browser).confirmation_text()


@when(parsers.parse('I remove "{product}" from my cart'))
@when(parsers.parse('I click Remove on "{product}"'))
def remove_product(browser, product):
    InventoryPage(browser).remove_from_cart(product_id(product))


# Which way each direction in the feature file runs
DESCENDING = {"A to Z": False, "Z to A": True, "low to high": False, "high to low": True}


@given(parsers.parse('I have sorted products by "{sort}"'))
@when(parsers.parse('I sort products by "{sort}"'))
def sort_products(browser, sort):
    InventoryPage(browser).sort_by(sort)


@then(parsers.parse("the products are sorted by {field}, {direction}"))
def products_sorted(browser, field, direction):
    page = InventoryPage(browser)
    values = page.product_names() if field == "name" else page.product_prices()
    # Python checks the order independently of the site's own sorting code
    assert values == sorted(values, reverse=DESCENDING[direction])


@then(parsers.parse('the first product is "{name}"'))
def first_product(browser, name):
    # Also guards against an empty list, which would count as sorted
    names = InventoryPage(browser).product_names()
    assert names and names[0] == name


@then(parsers.parse('I see the login error "{error}"'))
def login_error(browser, error):
    assert error in LoginPage(browser).error_message()


@given("I have logged out")
@when("I log out")
def log_out(browser):
    Menu(browser).log_out()


@then("I see the login page")
def on_login_page(browser):
    # The login form is showing and the shopper isn't on any logged-in page
    assert browser.find_elements(*LoginPage.LOGIN_BUTTON)
    assert "inventory" not in browser.current_url


@when("I open the products page directly")
def open_products_page_directly(browser):
    browser.get(InventoryPage.URL)


@when("I continue shopping")
def continue_shopping(browser):
    CartPage(browser).continue_shopping()


@when("I reset the app state")
@when("I click reset the app state")
def reset_app_state(browser):
    Menu(browser).reset_app_state()


@then(parsers.parse('the button under "{product}" shows {label}'))
def cart_button_label(browser, product, label):
    assert InventoryPage(browser).cart_button_text(product_id(product)) == label
