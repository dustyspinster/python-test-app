"""problem_user is a Swag Labs test account with deliberate bugs.

Each scenario describes the correct behavior and is tagged @known-bug, so it
runs as a strict expected failure (see conftest.py).
"""

from pytest_bdd import parsers, scenarios, then, when
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.inventory_page import InventoryPage
from pages.product_page import ProductPage

scenarios("features/problem_user.feature")

# The image Swag Labs shows when a product's real image is missing
PLACEHOLDER_IMAGE = "sl-404"


@then("I reach the order overview")
def order_overview(browser):
    WebDriverWait(browser, 10).until(EC.url_contains("checkout-step-two"))


@then("I see that every product has a unique image")
def unique_images(browser):
    images = InventoryPage(browser).product_image_files()
    # Checking for an empty list too, since no images would also count as "no duplicates"
    assert images and len(set(images)) == len(images), f"Duplicate product images: {images}"


@then("each image is not a 404 placeholder")
def no_placeholder_images(browser):
    images = InventoryPage(browser).product_image_files()
    assert images and not [i for i in images if PLACEHOLDER_IMAGE in i], f"Placeholder images: {images}"


@when(parsers.parse('I click on "{product}"'))
def open_product_page(browser, product):
    InventoryPage(browser).open_product(product)


@then(parsers.parse('I am directed to the "{product}" product description'))
def on_product_page(browser, product):
    assert ProductPage(browser).name() == product
