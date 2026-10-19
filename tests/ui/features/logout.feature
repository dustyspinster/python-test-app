Feature: Logout
  Shoppers can log out of their account

  Background:
    Given I am logged in as standard_user

  Scenario: A registered shopper logs out
    When I log out
    Then I see the login page

  Scenario: The products page can't be opened after logging out
    Given I have logged out
    When I open the products page directly
    Then I see the login error "You can only access '/inventory.html' when you are logged in."
