Feature: Accessibility
Shoppers can use keyboard navigation, and pages pass an automated WCAG 2.2 scan

  Scenario: Keyboard users can log in
    Given I am on the "login" page
    Then the username, password and Login button can each receive keyboard focus
    And they are selected in that order when tabbing
    And pressing Enter submits the login form

  @known-bug
  Scenario: Keyboard users can see when the Login button has focus
    Given I am on the "login" page
    Then the Login button looks different when it has keyboard focus

  @known-bug
  Scenario: Keyboard users can access the shopping cart page
    Given I am on the "products" page
    Then the shopping cart button can receive keyboard focus

  Scenario Outline: Every page will pass an automated WCAG 2.2 Scan
    Given I am on the "<page>" page
    Then the page has no WCAG 2.2 AA violations

    Examples:
      | page                 |
      | login                |
      | products             |
      | product details      |
      | cart                 |
      | checkout information |
      | checkout overview    |
      | checkout complete    |
