"""Step definitions shared by more than one UI feature file."""

import pytest
from pytest_bdd import given, parsers, then, when
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.inventory_page import InventoryPage, product_id


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


@given(parsers.parse('I have added "{product}" to my cart'))
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
