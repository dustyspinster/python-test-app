import time

import pytest
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL = "https://www.saucedemo.com/checkout-step-one.html"
FIRST = (By.ID, "first-name")

SET_VALUE_JS = """
const el = arguments[0];
const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
setter.call(el, arguments[1]);
el.dispatchEvent(new Event('input', { bubbles: true }));
"""


def fresh_field(driver):
    driver.get(URL)
    return WebDriverWait(driver, 10).until(EC.element_to_be_clickable(FIRST))


def current_value(driver):
    time.sleep(1)
    return driver.find_element(*FIRST).get_attribute("value")


def test_diagnose_typing(logged_in_driver):
    d = logged_in_driver
    results = {}

    el = fresh_field(d)
    el.send_keys("Test")
    results["1 send_keys only"] = current_value(d)

    el = fresh_field(d)
    el.click()
    el.send_keys("Test")
    results["2 click then send_keys"] = current_value(d)

    el = fresh_field(d)
    ActionChains(d).move_to_element(el).click().send_keys("Test").perform()
    results["3 action chains"] = current_value(d)

    el = fresh_field(d)
    d.execute_script(SET_VALUE_JS, el, "Test")
    results["4 javascript setter"] = current_value(d)

    results["field html"] = fresh_field(d).get_attribute("outerHTML")
    results["url"] = d.current_url

    pytest.fail(f"DIAGNOSTIC RESULTS (a value of 'Test' means typing worked): {results}")