Feature: Shopping cart
  Shoppers collect products in a cart before checking out.

  Background:
    Given I am logged in

  Scenario: Adding a product updates the cart badge
    When I add "Sauce Labs Backpack" to my cart
    Then my cart badge shows 1

  Scenario: Adding two products
    When I add "Sauce Labs Backpack" to my cart
    And I add "Sauce Labs Bike Light" to my cart
    Then my cart badge shows 2

  Scenario: Removing the only product empties the cart
    Given I have added "Sauce Labs Backpack" to my cart
    When I remove "Sauce Labs Backpack" from my cart
    Then my cart badge shows 0

  Scenario: The cart page lists added products
    Given I have added "Sauce Labs Backpack" to my cart
    When I open my cart
    Then my cart lists "Sauce Labs Backpack"

  Scenario: Continue Shopping keeps the cart
    Given I have added "Sauce Labs Backpack" to my cart
    When I open my cart
    And I continue shopping
    Then I see the product inventory
    And my cart badge shows 1

  Scenario: The cart is saved after logging out and back in
    Given I have added "Sauce Labs Backpack" to my cart
    When I log out
    And I log back in as standard_user
    Then my cart badge shows 1

  @known-bug
  Scenario: The app state is reset and fully empties the cart
    Given I have added "Sauce Labs Backpack" to my cart
    When I click reset the app state
    Then my cart badge shows 0
    And the button under "Sauce Labs Backpack" shows Add to cart
