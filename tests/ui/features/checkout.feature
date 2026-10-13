Feature: Checkout
  Shoppers enter their details and confirm the order to buy what's in their cart.

  Background:
    Given I am logged in
    And I have added "Sauce Labs Backpack" to my cart

  Scenario: A shopper completes a purchase
    When I open my cart
    And I start checkout
    And I enter first name "Test", last name "User" and postal code "97201"
    And I finish my order
    Then I see the order confirmation "Thank you for your order"

  Scenario Outline: Checkout requires every field
    Given I am on the checkout information page
    When I enter first name "<first>", last name "<last>" and postal code "<postal>"
    Then I see the checkout error "<error>"

    Examples:
      | first | last | postal | error                   |
      |       | User | 97201  | First Name is required  |
      | Test  |      | 97201  | Last Name is required   |
      | Test  | User |        | Postal Code is required |

  Scenario: Cancelling checkout keeps the cart
    When I open my cart
    And I start checkout
    And I enter first name "Test", last name "User" and postal code "97201"
    And I cancel my order
    Then I am taken back to the Products page
    And my cart badge shows 1

  # Swag Labs shows this cart's item total unrounded; see Known issues in the README
  @known-bug
  Scenario: Checkout totals the cart with tax
    Given I have also added these products to my cart
      | product                  |
      | Sauce Labs Bike Light    |
      | Sauce Labs Bolt T-Shirt  |
      | Sauce Labs Fleece Jacket |
    When I open my cart
    And I start checkout
    And I enter first name "Test", last name "User" and postal code "97201"
    # $29.99 + $9.99 + $15.99 + $49.99 = $105.96, and 8% tax is $8.4768, shown as $8.48
    Then the item total is "$105.96"
    And the tax is "$8.48"
    And the order total is "$114.44"
