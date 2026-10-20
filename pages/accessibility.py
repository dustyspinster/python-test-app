"""Accessibility checks that don't depend on simulated key presses.

Headless Chrome intermittently drops real input, keyboard included (see
interactions.py), so keyboard support is checked through what the page
exposes instead: whether an element can take focus, the order focus moves
in, and whether focus changes how an element looks.
"""

import logging

from axe_selenium_python import Axe
from selenium.webdriver.remote.webdriver import WebDriver

log = logging.getLogger(__name__)

# The WCAG 2.0, 2.1 and 2.2 Level A and AA rules, the standard behind Section 508
WCAG_AA_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]

# Properties a browser or site typically changes to show focus
FOCUS_STYLE_PROPERTIES = ["outlineStyle", "outlineColor", "boxShadow", "borderColor", "backgroundColor"]


def wcag_violations(driver: WebDriver) -> list[dict]:
    """Run axe-core with the WCAG A and AA rules and return its violations.

    Items axe can't decide on its own, such as some color contrast, are logged
    as warnings for a person to review rather than failing the test.
    """
    axe = Axe(driver)
    axe.inject()
    results = axe.run(options={"runOnly": {"type": "tag", "values": WCAG_AA_TAGS}})
    for item in results["incomplete"]:
        log.warning("Needs manual review: %s (%d elements)", item["help"], len(item["nodes"]))
    return results["violations"]


def describe(violations: list[dict]) -> str:
    return "; ".join(
        f"{v['id']} ({v['impact']}, {len(v['nodes'])} elements): {v['help']}" for v in violations
    )


def can_take_focus(driver: WebDriver, css: str) -> bool:
    return driver.execute_script(
        "const e = document.querySelector(arguments[0]); e.focus(); return document.activeElement === e;",
        css,
    )


def tab_order(driver: WebDriver) -> list[str] | None:
    """IDs of the visible elements Tab moves through, in order.

    With no positive tabindex anywhere, Tab follows document order, so this is
    the order a keyboard user experiences. Returns None if a positive tabindex
    overrides that order.
    """
    return driver.execute_script(
        """
        if ([...document.querySelectorAll('[tabindex]')].some(e => e.tabIndex > 0)) return null;
        return [...document.querySelectorAll('a[href], button, input, select, textarea, [tabindex]')]
          .filter(e => e.tabIndex >= 0 && e.offsetParent !== null)
          .map(e => e.id || e.tagName.toLowerCase());
        """
    )


def submits_on_enter(driver: WebDriver, field_ids: list[str], button_id: str) -> bool:
    # Browsers submit a form when Enter is pressed in one of its fields, if the form has a submit button
    return driver.execute_script(
        """
        const button = document.getElementById(arguments[1]);
        const form = button.closest('form');
        return !!form && button.type === 'submit'
          && arguments[0].every(id => document.getElementById(id).closest('form') === form);
        """,
        field_ids,
        button_id,
    )


def focus_style_change(driver: WebDriver, element_id: str) -> tuple[bool, list[str]]:
    """Focus the element and return (whether it's in its keyboard-focus state, the styles that changed)."""
    return driver.execute_script(
        """
        const e = document.getElementById(arguments[0]);
        const props = arguments[1];
        const look = () => { const s = getComputedStyle(e); return props.map(p => s[p]); };
        if (document.activeElement) document.activeElement.blur();
        const before = look();
        e.focus();
        const after = look();
        return [e.matches(':focus-visible'), props.filter((p, i) => before[i] !== after[i])];
        """,
        element_id,
        FOCUS_STYLE_PROPERTIES,
    )
