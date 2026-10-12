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
