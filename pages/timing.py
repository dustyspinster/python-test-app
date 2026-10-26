"""Response-time measurements taken with the browser's own clock.

The clock starts when the page receives a user action (a click, typing or a
dropdown change), not when the test sends it. If Chrome drops the real input
and interactions.py falls back to JavaScript after waiting, only the JavaScript
action reaches the page, so that wait doesn't count against the site.
"""

from collections.abc import Callable

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

# Runs in every page before the site's own scripts. sessionStorage keeps the time across page loads
RECORD_ACTIONS_JS = """
for (const type of ['click', 'input', 'change', 'submit']) {
  addEventListener(type, (e) => {
    const at = String(performance.timeOrigin + e.timeStamp);
    try { sessionStorage.setItem('__lastActionAt', at); } catch (_) {}
  }, true);
}
"""

SECONDS_SINCE_ACTION_JS = """
const at = Number(sessionStorage.getItem('__lastActionAt'));
return at ? (performance.timeOrigin + performance.now() - at) / 1000 : null;
"""


def record_user_actions(driver: WebDriver) -> None:
    """Start recording when the page receives user actions, on every page from now on (Chrome only)."""
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": RECORD_ACTIONS_JS})


def seconds_until(driver: WebDriver, condition: Callable[[WebDriver], object], timeout: float = 30) -> float:
    """Wait for the condition, then return the seconds since the page received the last user action.

    Accurate to about a tenth of a second when the condition is still pending, but the step before
    may already have waited for it, polling every half second, so allow that much margin in limits.
    """
    try:
        WebDriverWait(driver, timeout, poll_frequency=0.05).until(condition)
    except TimeoutException:
        # An assertion, so a @known-bug scenario that never finishes still counts as the known bug
        raise AssertionError(f"Still waiting after {timeout} seconds") from None
    elapsed = driver.execute_script(SECONDS_SINCE_ACTION_JS)
    assert elapsed is not None, "The page never received a user action to time from"
    return elapsed
