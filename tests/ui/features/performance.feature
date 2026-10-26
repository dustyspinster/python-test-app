Feature: Web store performance

  Scenario Outline: Add to cart function reacts in a timely manner
    Given I am logged in as <username>
    When I add "Sauce Labs Backpack" to my cart
    Then my cart badge shows 1 within 3 seconds

    Examples:
      | username                |
      | standard_user           |
      | performance_glitch_user |

  Scenario Outline: A user can log in and see products in a timely manner
    Given I am on the login page
    When I log in as "<username>" with password "<password>"
    Then I see the product inventory within 3 seconds

    Examples:
      | username        | password       |
      | standard_user   | secret_sauce   |
      | visual_user     | secret_sauce   |

    @known-bug
    Examples:
      | username                  | password       |
      | performance_glitch_user   | secret_sauce   |

  Scenario Outline: A user can return to the Products page in a timely manner
    Given I am logged in as <username>
    And I am on the "Sauce Labs Backpack" details page
    When I click "Back to products"
    Then I am taken back to the Products page within 3 seconds

    Examples:
      | username        |
      | standard_user   |
      | visual_user     |

    @known-bug
    Examples:
      | username                  |
      | performance_glitch_user   |

  Scenario Outline: A user can sort products on the Products page in a timely manner
    Given I am logged in as <username>
    When I sort products by "Price (low to high)"
    Then the products are sorted by price, low to high, within 3 seconds

    Examples:
      | username        |
      | standard_user   |

    @known-bug
    Examples:
      | username                  |
      | performance_glitch_user   |
