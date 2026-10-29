Feature: Error User

  Background:
    Given I am logged in as error_user

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
      | Sauce Labs Onesie                 |

    @known-bug
    Examples:
      | product                           |
      | Sauce Labs Bolt T-Shirt           |
      | Sauce Labs Fleece Jacket          |
      | Test.allTheThings() T-Shirt (Red) |

  @known-bug
  Scenario: A shopper enters their first and last name into checkout
    Given I am on the checkout information page
    When I enter last name "User"
    Then the last name field shows "User"

  @known-bug
  Scenario: A shopper can click Finish to complete order
    Given I have added "Sauce Labs Backpack" to my cart
    And I am on the checkout overview page
    When I finish my order
    Then I see the order confirmation "Thank you for your order"

  