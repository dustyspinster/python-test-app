from pytest_bdd import given, parsers, scenarios, then, when

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage

scenarios("features/checkout.feature")


@given("I am on the checkout information page")
def checkout_information_page(browser):
    # Open the form directly; the full click-through path is covered by the purchase scenario
    browser.get(CheckoutPage.URL)


@when("I start checkout")
def start_checkout(browser):
    CartPage(browser).checkout()


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


@then(parsers.parse('I see the checkout error "{error}"'))
def checkout_error(browser, error):
    assert error in CheckoutPage(browser).error_message()
