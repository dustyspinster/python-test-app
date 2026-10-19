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


def pytest_bdd_apply_tag(tag, function):
    """Turn a @known-bug tag into a strict expected failure.

    The scenario still runs, and is reported as expected to fail instead of failing the build.
    Only a failed assertion counts as the known bug; any other error still fails the test.
    strict=True makes an unexpected pass fail, so the tag gets removed once the bug is fixed.
    """
    if tag != "known-bug":
        return None
    reason = "Known Swag Labs bug; see Known issues in the README"
    pytest.mark.xfail(reason=reason, raises=AssertionError, strict=True)(function)
    return True


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
