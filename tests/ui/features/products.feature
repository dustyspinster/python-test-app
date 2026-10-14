Feature: Products sorting
  Shoppers can click a dropdown to sort how products are listed

  Background:
    Given I am logged in as standard_user

  Scenario Outline: Sorting products
    When I sort products by "<sort>"
    Then the products are sorted by <field>, <direction>
    And the first product is "<first>"

    Examples:
      | sort                | field | direction   | first                             |
      | Name (Z to A)       | name  | Z to A      | Test.allTheThings() T-Shirt (Red) |
      | Price (low to high) | price | low to high | Sauce Labs Onesie                 |
      | Price (high to low) | price | high to low | Sauce Labs Fleece Jacket          |

  Scenario: Switching back to name order, A to Z
    Given I have sorted products by "Name (Z to A)"
    When I sort products by "Name (A to Z)"
    Then the products are sorted by name, A to Z
    And the first product is "Sauce Labs Backpack"
