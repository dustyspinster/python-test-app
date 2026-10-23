"""Click and type helpers that confirm each action took effect.

Headless Chrome intermittently stops delivering real input to the page: the
click or keystroke is accepted by ChromeDriver but no event ever reaches the
DOM, and it stays that way for the rest of the page. Triggering the same action
from inside the page with JavaScript still works, so each helper tries real
input first and falls back to JavaScript only when nothing happened.

Reported upstream as https://issues.chromium.org/issues/571158512
"""

import logging
from collections.abc import Callable

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

log = logging.getLogger(__name__)

# A Selenium locator such as (By.ID, "checkout")
Locator = tuple[str, str]
# Anything WebDriverWait can wait on: returns a truthy value once the condition holds
Condition = Callable[[WebDriver], object]

# React tracks input values itself, so set the value through the native setter
# and fire an input event, or React keeps its old state
SET_VALUE_JS = """
const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
setter.call(arguments[0], arguments[1]);
arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
"""

# Same idea for a <select>: pick the option through the native setter, then
# fire the change event React listens for
SELECT_OPTION_JS = """
const select = arguments[0];
const option = Array.from(select.options).find((o) => o.text === arguments[1]);
const setter = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value').set;
setter.call(select, option.value);
select.dispatchEvent(new Event('change', { bubbles: true }));
"""


# Once Chrome starts dropping input on a page it keeps dropping it, so after one confirmed drop
# the rest of that page's actions go straight to JavaScript instead of waiting out real input.
# The flag lives in the page, so a new page load clears it and real input is tried again.
INPUT_DROPPED_JS = "return window.__inputDropped === true;"
MARK_INPUT_DROPPED_JS = "window.__inputDropped = arguments[0];"


def _input_dropped(driver: WebDriver) -> bool:
    return bool(driver.execute_script(INPUT_DROPPED_JS))


def _fallback(driver: WebDriver, action: Callable[[], None], confirmed: Callable[[], bool]) -> bool:
    """Do the action via JavaScript, keeping the page marked as dropping input only if it worked.

    Marked first: if the action loads a new page, the old page's flag goes with it.
    """
    driver.execute_script(MARK_INPUT_DROPPED_JS, True)
    action()
    if confirmed():
        return True
    # JavaScript failed too, so the app ignored the action; that's not Chrome dropping input
    driver.execute_script(MARK_INPUT_DROPPED_JS, False)
    return False


def _happened(driver: WebDriver, done: Condition, timeout: float) -> bool:
    try:
        WebDriverWait(
            driver, timeout, ignored_exceptions=(NoSuchElementException, StaleElementReferenceException)
        ).until(done)
        return True
    except TimeoutException:
        return False


def click(
    driver: WebDriver, locator: Locator, done: Condition, timeout: float = 10, settle: float = 4
) -> None:
    """Click the element, then wait until done(driver) is truthy."""
    element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))
    if _input_dropped(driver):
        log.warning("Chrome is dropping input on this page; clicking %s via JavaScript", locator)
    else:
        element.click()
        if _happened(driver, done, settle):
            return

        elements = driver.find_elements(*locator)
        if not elements:
            # The element went away, so the click did land and the page is just slow
            if _happened(driver, done, timeout):
                return
            raise AssertionError(f"Clicking {locator} had no visible effect")

        # Usually Chrome's input bug, but an app that ignores the input looks the same until the fallback
        log.warning(
            "Clicking %s had no effect (Chrome may have dropped it); clicking via JavaScript", locator
        )
        element = elements[0]

    def js_click() -> None:
        driver.execute_script("arguments[0].click();", element)

    if not _fallback(driver, js_click, lambda: _happened(driver, done, settle)):
        raise AssertionError(f"Clicking {locator} had no effect, even via JavaScript")


def type_text(driver: WebDriver, locator: Locator, text: str, timeout: float = 10, settle: float = 2) -> None:
    """Replace the field's contents with text and confirm the field kept it."""

    def has_text(d: WebDriver) -> bool:
        return d.find_element(*locator).get_attribute("value") == text

    field = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))
    if _input_dropped(driver):
        log.warning("Chrome is dropping input on this page; setting %s via JavaScript", locator)
    else:
        field.clear()
        field.send_keys(text)
        if _happened(driver, has_text, settle):
            return

        log.warning(
            "Typing into %s had no effect (Chrome may have dropped it); setting it via JavaScript", locator
        )

    def js_type() -> None:
        driver.execute_script(SET_VALUE_JS, driver.find_element(*locator), text)

    if not _fallback(driver, js_type, lambda: _happened(driver, has_text, settle)):
        raise AssertionError(f"Field {locator} did not keep {text!r}, even via JavaScript")


def choose_option(
    driver: WebDriver, locator: Locator, text: str, timeout: float = 10, settle: float = 2
) -> None:
    """Choose the option with this visible text in a dropdown, and confirm it was chosen."""

    def chosen(d: WebDriver) -> bool:
        return Select(d.find_element(*locator)).first_selected_option.text == text

    menu = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))
    if _input_dropped(driver):
        log.warning("Chrome is dropping input on this page; choosing %r in %s via JavaScript", text, locator)
    else:
        Select(menu).select_by_visible_text(text)
        if _happened(driver, chosen, settle):
            return

        log.warning(
            "Choosing %r in %s had no effect (Chrome may have dropped it); choosing via JavaScript",
            text,
            locator,
        )

    def js_choose() -> None:
        driver.execute_script(SELECT_OPTION_JS, driver.find_element(*locator), text)

    if not _fallback(driver, js_choose, lambda: _happened(driver, chosen, settle)):
        raise AssertionError(f"Dropdown {locator} did not keep {text!r}, even via JavaScript")
