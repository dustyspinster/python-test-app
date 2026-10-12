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
