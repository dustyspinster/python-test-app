import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.login_page import LoginPage


def test_valid_login(driver):
    page = LoginPage(driver)
    page.open()
    page.login("standard_user", "secret_sauce")

    WebDriverWait(driver, 10).until(EC.url_contains("inventory"))
    assert "inventory" in driver.current_url


@pytest.mark.parametrize(
    "username, password, expected_error",
    [
        ("standard_user", "wrong_password", "do not match"),
        ("locked_out_user", "secret_sauce", "locked out"),
        ("", "secret_sauce", "Username is required"),
        ("standard_user", "", "Password is required"),
    ],
)
def test_invalid_login(driver, username, password, expected_error):
    page = LoginPage(driver)
    page.open()
    page.login(username, password)

    assert expected_error in page.error_message()
    assert "inventory" not in driver.current_url
