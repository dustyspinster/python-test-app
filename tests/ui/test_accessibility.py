import pytest
from pytest_bdd import given, parsers, scenarios, then
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages import accessibility
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage

scenarios("features/accessibility.feature")

LOGIN_CONTROLS = ["user-name", "password", "login-button"]
# The cart link is an <a> with no href, which is why browsers skip it when tabbing.
# It has no ID, and it's announced to screen readers as a button labelled "Cart".
CART_LINK = "[data-test='shopping-cart-link']"


@given(parsers.parse('I am on the "{page}" page'), target_fixture="browser")
def on_page(driver, page):
    """Reach the page the way a shopper would, from logging in onward."""
    login = LoginPage(driver)
    login.open()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(LoginPage.LOGIN_BUTTON))
    if page == "login":
        return driver

    login.login("standard_user", "secret_sauce")
    WebDriverWait(driver, 10).until(EC.url_contains("inventory"))
    inventory = InventoryPage(driver)
    if page == "products":
        return driver
    if page == "product details":
        inventory.open_product("Sauce Labs Backpack")
        return driver

    inventory.add_to_cart("sauce-labs-backpack")
    inventory.open_cart()
    if page == "cart":
        return driver
    CartPage(driver).checkout()
    if page == "checkout information":
        return driver
    checkout = CheckoutPage(driver)
    checkout.fill_information("Test", "User", "97201")
    if page == "checkout overview":
        return driver
    checkout.finish()
    if page == "checkout complete":
        return driver
    raise ValueError(f"No route to the {page!r} page")


@then("the page has no WCAG 2.2 AA violations")
def no_wcag_violations(browser):
    violations = accessibility.wcag_violations(browser)
    assert not violations, accessibility.describe(violations)


@then("the username, password and Login button can each receive keyboard focus")
def login_controls_focusable(browser):
    unfocusable = [i for i in LOGIN_CONTROLS if not accessibility.can_take_focus(browser, f"#{i}")]
    assert not unfocusable, f"Can't receive keyboard focus: {unfocusable}"


@then("they are selected in that order when tabbing")
def login_tab_order(browser):
    order = accessibility.tab_order(browser)
    assert order is not None, "A positive tabindex overrides the natural tab order"
    assert [i for i in order if i in LOGIN_CONTROLS] == LOGIN_CONTROLS, f"Tab order: {order}"


@then("pressing Enter submits the login form")
def enter_submits_login(browser):
    assert accessibility.submits_on_enter(browser, ["user-name", "password"], "login-button")


@then("the Login button looks different when it has keyboard focus")
def login_button_focus_visible(browser):
    keyboard_focus, changed = accessibility.focus_style_change(browser, "login-button")
    if not keyboard_focus:
        # Without the keyboard-focus state there's nothing to judge, so this must not count as the known bug
        pytest.fail("Couldn't put the Login button in its keyboard-focus state")
    assert changed, "The Login button looks identical with and without keyboard focus"


@then("the shopping cart button can receive keyboard focus")
def cart_link_focusable(browser):
    assert accessibility.can_take_focus(browser, CART_LINK), "The cart link can't receive keyboard focus"
