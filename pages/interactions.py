"""Click and type helpers that confirm each action took effect.

Headless Chrome intermittently stops delivering real input to the page: the
click or keystroke is accepted by ChromeDriver but no event ever reaches the
DOM, and it stays that way for the rest of the page. Triggering the same action
from inside the page with JavaScript still works, so each helper tries real
input first and falls back to JavaScript only when nothing happened.
"""
import logging

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

log = logging.getLogger(__name__)

# React tracks input values itself, so set the value through the native setter
# and fire an input event, or React keeps its old state
SET_VALUE_JS = """
const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
setter.call(arguments[0], arguments[1]);
arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
"""


def _happened(driver, done, timeout):
    try:
        WebDriverWait(
            driver, timeout, ignored_exceptions=(NoSuchElementException, StaleElementReferenceException)
        ).until(done)
        return True
    except Exception:
        return False


def click(driver, locator, done, timeout=10, settle=4):
    """Click the element, then wait until done(driver) is truthy."""
    WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator)).click()
    if _happened(driver, done, settle):
        return

    elements = driver.find_elements(*locator)
    if not elements:
        # The element went away, so the click did land and the page is just slow
        if _happened(driver, done, timeout):
            return
        raise AssertionError(f"Clicking {locator} had no visible effect")

    log.warning("Chrome dropped the click on %s; clicking via JavaScript", locator)
    driver.execute_script("arguments[0].click();", elements[0])
    if not _happened(driver, done, settle):
        raise AssertionError(f"Clicking {locator} had no effect, even via JavaScript")


def type_text(driver, locator, text, timeout=10, settle=2):
    """Replace the field's contents with text and confirm the field kept it."""

    def has_text(d):
        return d.find_element(*locator).get_attribute("value") == text

    field = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))
    field.clear()
    field.send_keys(text)
    if _happened(driver, has_text, settle):
        return

    log.warning("Chrome dropped typing into %s; setting the value via JavaScript", locator)
    driver.execute_script(SET_VALUE_JS, driver.find_element(*locator), text)
    if not _happened(driver, has_text, settle):
        raise AssertionError(f"Field {locator} did not keep {text!r}, even via JavaScript")
