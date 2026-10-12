Feature: Booking lifecycle
  Guests create bookings; only a logged-in admin can change or cancel them.

  Scenario: A guest creates a booking
    When a guest creates a booking
    Then the response status is 200
    And the response is a valid new booking
    And the booking can be retrieved with the same details

  Scenario: An admin replaces a booking
    Given a booking exists
    When an admin replaces the booking with first name "Updated"
    Then the response status is 200
    And the booking matches the original except "firstname" is "Updated"

  Scenario Outline: A partial update changes only the given field
    Given a booking exists
    When an admin sets "<field>" to "<value>"
    Then the response status is 200
    And the booking matches the original except "<field>" is "<value>"

    Examples:
      | field           | value   |
      | firstname       | Patched |
      | lastname        | Changed |
      | additionalneeds | Dinner  |

  Scenario: An admin cancels a booking
    Given a booking exists
    When an admin deletes the booking
    Then the response status is 201
    And the booking can no longer be found

  Scenario Outline: Changing a booking requires logging in
    Given a booking exists
    When a guest tries to <action> the booking without logging in
    Then the response status is 403

    Examples:
      | action |
      | update |
      | delete |
