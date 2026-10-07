import os

import pytest
from selenium import webdriver

from pages.login_page import LoginPage


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
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
    driver.quit()


@pytest.fixture
def logged_in_driver(driver):
    page = LoginPage(driver)
    page.open()
    page.login("standard_user", "secret_sauce")
    return driver