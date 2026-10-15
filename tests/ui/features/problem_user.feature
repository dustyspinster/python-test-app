Feature: Problem User
  This user experiences bugs when using the store features

  Background:
    Given I am logged in as problem_user

  @known-bug
  Scenario: A shopper can enter their last name at checkout
    Given I have added "Sauce Labs Onesie" to my cart
    And I am on the checkout information page
    When I enter first name "Problem", last name "User" and postal code "97201"
    Then I reach the order overview

  @known-bug
  Scenario: A shopper can see photos of the products in the products page
    Then I see that every product has a unique image
    And each image is not a 404 placeholder

  @known-bug
  Scenario: A shopper can change the sorting method of products
    When I sort products by "Price (high to low)"
    Then the first product is "Sauce Labs Fleece Jacket"

  @known-bug
  Scenario Outline: A shopper can add a product to the cart
    When I add "<product>" to my cart
    Then my cart badge shows 1

    Examples:
      | product                           |
      | Sauce Labs Bolt T-Shirt           |
      | Sauce Labs Fleece Jacket          |
      | Test.allTheThings() T-Shirt (Red) |

  @known-bug
  Scenario: A shopper removes an item from the cart from the products page
    Given I have clicked add to cart on "Sauce Labs Onesie"
    When I click Remove on "Sauce Labs Onesie"
    Then my cart badge shows 0

  @known-bug
  Scenario Outline: A shopper clicks on a product to open the product description
    When I click on "<product>"
    Then I am directed to the "<product>" product description

    Examples:
      | product                           |
      | Sauce Labs Backpack               |
      | Sauce Labs Bolt T-Shirt           |
      | Sauce Labs Onesie                 |
      | Sauce Labs Bike Light             |
      | Sauce Labs Fleece Jacket          |
      | Test.allTheThings() T-Shirt (Red) |
