import pytest
from selenium import webdriver

from pages.login_page import LoginPage


@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()


@pytest.fixture
def logged_in_driver(driver):
    page = LoginPage(driver)
    page.open()
    page.login("standard_user", "secret_sauce")
    return driver