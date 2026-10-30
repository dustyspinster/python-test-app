Feature: Rate Limiter
  Requests sent faster than the limit wait until they're allowed

  Background:
    Given the limit is 10 requests per second with bursts up to 20

  Scenario: Requests sent at 10 per second don't wait
    When I send 10 requests per second for 5 seconds
    Then no request waits before it is sent

  Scenario: A request beyond a burst of 20 waits
    When I send 21 requests at once
    Then the first 20 requests are sent without waiting
    And the 21st request waits before it is sent

  Scenario: After a burst, a one-second pause lets 10 more requests through
    Given I have sent 20 requests at once
    When I wait for one second
    And I send 11 more requests at once
    Then none of the first 10 requests wait
    And an 11th request waits before it is sent

  Scenario: A long pause doesn't allow a burst bigger than 20
    Given I have sent 20 requests at once
    When I wait for five seconds
    And I send 21 more requests at once
    Then the first 20 requests are sent without waiting
    And the 21st request waits before it is sent
