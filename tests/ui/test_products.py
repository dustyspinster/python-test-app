from pytest_bdd import parsers, scenarios, then, when

from pages.inventory_page import InventoryPage

scenarios("features/products.feature")

# Which way each direction in the feature file runs
DESCENDING = {"A to Z": False, "Z to A": True, "low to high": False, "high to low": True}


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
