Feature: Login
  Shoppers sign in before they can browse products.

  Background:
    Given I am on the login page

  Scenario: A registered shopper logs in
    When I log in as "standard_user" with password "secret_sauce"
    Then I see the product inventory

  Scenario Outline: An invalid login is rejected with a reason
    When I log in as "<username>" with password "<password>"
    Then I see the login error "<error>"
    And I am still on the login page

    Examples:
      | username        | password       | error                |
      | standard_user   | wrong_password | do not match         |
      |                 | secret_sauce   | Username is required |
      | standard_user   |                | Password is required |

  Scenario: A locked-out shopper can't log in, even with the right password
    When I log in as "locked_out_user" with password "secret_sauce"
    Then I see the login error "Epic sadface: Sorry, this user has been locked out."
    And I am still on the login page
