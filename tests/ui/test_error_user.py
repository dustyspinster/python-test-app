"""error_user is a Swag Labs test account whose buttons and fields fail in some places.

Each scenario describes the correct behavior. Those that hit a bug are tagged
@known-bug, so they run as strict expected failures (see conftest.py).
"""

import contextlib

from pytest_bdd import given, parsers, scenarios, then, when

from pages.checkout_page import CheckoutPage

scenarios("features/error_user.feature")


@given("I am on the checkout overview page")
def checkout_overview_page(browser):
    # Open the overview directly, so a bug on the information page can't stop the scenario early
    browser.get(CheckoutPage.OVERVIEW_URL)


@when(parsers.parse('I enter last name "{last}"'))
def enter_last_name(browser, last):
    # Typing checks that the field kept the text; leave reporting that to the Then step
    with contextlib.suppress(AssertionError):
        CheckoutPage(browser).enter_last_name(last)


@then(parsers.parse('the last name field shows "{last}"'))
def last_name_shows(browser, last):
    assert CheckoutPage(browser).last_name() == last
