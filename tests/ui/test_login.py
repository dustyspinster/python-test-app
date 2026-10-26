from pytest_bdd import scenarios, then

scenarios("features/login.feature")


@then("I am still on the login page")
def still_on_login(browser):
    assert "inventory" not in browser.current_url
