import os
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.login_page import LoginPage

SCREENSHOT_DIR = Path("screenshots")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture
def driver(request):
    options = webdriver.ChromeOptions()
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    headless = bool(os.getenv("HEADLESS"))
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    if not headless:
        driver.maximize_window()
    yield driver

    failed = any(
        getattr(request.node, name, None) is not None and getattr(request.node, name).failed
        for name in ("rep_setup", "rep_call")
    )
    if failed:
        SCREENSHOT_DIR.mkdir(exist_ok=True)
        safe_name = "".join(c if c.isalnum() else "_" for c in request.node.name)
        driver.save_screenshot(str(SCREENSHOT_DIR / f"{safe_name}.png"))
        (SCREENSHOT_DIR / f"{safe_name}.txt").write_text(
            f"URL: {driver.current_url}\nTitle: {driver.title}\n"
        )
        try:
            lines = [f"{e['level']}: {e['message']}" for e in driver.get_log("browser")]
            (SCREENSHOT_DIR / f"{safe_name}.log").write_text("\n".join(lines) or "(no console messages)")
        except Exception as exc:
            (SCREENSHOT_DIR / f"{safe_name}.log").write_text(f"Could not read console log: {exc}")
        (SCREENSHOT_DIR / f"{safe_name}.html").write_text(driver.page_source, encoding="utf-8")
    driver.quit()


@pytest.fixture
def logged_in_driver(driver):
    page = LoginPage(driver)
    page.open()
    page.login("standard_user", "secret_sauce")
    WebDriverWait(driver, 10).until(EC.url_contains("inventory"))
    return driver
