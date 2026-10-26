import pytest
from pytest_bdd import parsers, scenarios, then

from pages import timing
from pages.inventory_page import InventoryPage

scenarios("features/performance.feature")


@pytest.fixture(autouse=True)
def record_user_actions(driver):
    # Before the first page loads, so every action in the scenario is timed from when the page got it
    timing.record_user_actions(driver)


@then(parsers.parse("my cart badge shows {count:d} within {limit:g} seconds"))
def cart_badge_within(browser, count, limit):
    elapsed = timing.seconds_until(browser, lambda d: InventoryPage(d).cart_count() == count)
    assert elapsed <= limit, f"The cart badge showed {count} after {elapsed:.2f} s; the limit is {limit} s"


@then(parsers.parse("I see the product inventory within {limit:g} seconds"))
def inventory_within(browser, limit):
    elapsed = timing.seconds_until(browser, lambda d: d.find_elements(*InventoryPage.ITEM_NAMES))
    assert elapsed <= limit, f"The products appeared after {elapsed:.2f} s; the limit is {limit} s"


# Defined here so it takes priority over the shared "sorted by {field}, {direction}" step, which
# would otherwise also match these lines
@then(
    parsers.re(
        r"the products are sorted by (?P<field>name|price), "
        r"(?P<direction>A to Z|Z to A|low to high|high to low),? within (?P<limit>[\d.]+) seconds"
    )
)
def sorted_within(browser, field, direction, limit):
    page = InventoryPage(browser)

    def is_sorted(_) -> bool:
        values = page.product_names() if field == "name" else page.product_prices()
        return bool(values) and values == sorted(values, reverse=direction in ("Z to A", "high to low"))

    elapsed = timing.seconds_until(browser, is_sorted)
    assert elapsed <= float(limit), f"The products were sorted after {elapsed:.2f} s; the limit is {limit} s"


@then(parsers.parse("I am taken back to the Products page within {limit:g} seconds"))
def back_on_products_within(browser, limit):
    elapsed = timing.seconds_until(browser, lambda d: d.find_elements(*InventoryPage.ITEM_NAMES))
    assert elapsed <= limit, f"The Products page showed after {elapsed:.2f} s; the limit is {limit} s"
