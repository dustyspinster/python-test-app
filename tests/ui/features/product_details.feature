Feature: Product details
A user can browse to a specific product page to learn details of a store item

  Background:
    Given I am logged in

  Scenario Outline: The price and name of a product are the same on the details page and products page
    Given I am on the "products" page
    Then the price of "<product>" is <price>
    When I click on "<product>"
    Then the details page shows the name "<product>"
    And the details page shows the price <price>

    Examples:
      | product                           | price  |
      | Sauce Labs Backpack               | $29.99 |
      | Sauce Labs Bike Light             | $9.99  |
      | Sauce Labs Bolt T-Shirt           | $15.99 |
      | Sauce Labs Fleece Jacket          | $49.99 |
      | Sauce Labs Onesie                 | $7.99  |
      | Test.allTheThings() T-Shirt (Red) | $15.99 |

  Scenario Outline: Adding a product to the cart from the details page
    Given I am on the "products" page
    When I click on "<product>"
    And I click Add to cart
    Then the details page button shows "Remove"
    And my cart badge shows 1

    Examples:
      | product                           |
      | Sauce Labs Backpack               |
      | Sauce Labs Bike Light             |
      | Sauce Labs Bolt T-Shirt           |
      | Sauce Labs Fleece Jacket          |
      | Sauce Labs Onesie                 |
      | Test.allTheThings() T-Shirt (Red) |
