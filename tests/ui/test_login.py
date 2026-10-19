from pytest_bdd import given, parsers, scenarios, then, when

from pages.login_page import LoginPage

scenarios("features/login.feature")


@given("I am on the login page", target_fixture="browser")
def login_page(driver):
    LoginPage(driver).open()
    return driver


# [^"]* rather than {}, so an Examples cell can be empty
@when(parsers.re(r'I log in as "(?P<username>[^"]*)" with password "(?P<password>[^"]*)"'))
def log_in(browser, username, password):
    LoginPage(browser).login(username, password)


@then("I am still on the login page")
def still_on_login(browser):
    assert "inventory" not in browser.current_url
