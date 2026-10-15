from pytest_bdd import parsers, scenarios, then, when

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage

scenarios("features/checkout.feature")


@when("I start checkout")
def start_checkout(browser):
    CartPage(browser).checkout()


@when("I cancel my order")
def cancel_order(browser):
    CheckoutPage(browser).cancel()


@when("I finish my order")
def finish_order(browser):
    CheckoutPage(browser).finish()


@then(parsers.parse('I see the order confirmation "{text}"'))
def order_confirmation(browser, text):
    assert text in CheckoutPage(browser).confirmation_text()


@then(parsers.parse('I see the checkout error "{error}"'))
def checkout_error(browser, error):
    assert error in CheckoutPage(browser).error_message()


@then(parsers.parse('the item total is "{amount}"'))
def item_total(browser, amount):
    assert CheckoutPage(browser).item_total() == amount


@then(parsers.parse('the tax is "{amount}"'))
def tax(browser, amount):
    assert CheckoutPage(browser).tax() == amount


@then(parsers.parse('the order total is "{amount}"'))
def order_total(browser, amount):
    assert CheckoutPage(browser).total() == amount
