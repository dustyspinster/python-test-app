Feature: Circuit Breaker
  If the API service is down, stop sending requests so tests fail quickly

  Background:
    Given the breaker trips after 3 failures in a row and waits 30 seconds

  Scenario Outline: Rejected requests don't trip the breaker
    When I send 3 requests that result in a "<response>" response in a row
    Then the next request is sent

    Examples: The service is up but rejects the request
      | response |
      | 400      |
      | 403      |
      | 404      |
      | 405      |
      | 418      |
      # Restful-booker returns 500 for bad input
      | 500      |

  Scenario Outline: Three requests while the service is down will trip the breaker
    When I send 3 requests that result in a "<response>" response in a row
    Then the next request fails without being sent

    Examples: The service is down
      | response           |
      | connection refused |
      | timed out          |
      | 502                |
      | 503                |
      | 504                |

  Scenario: After two failed requests, one successful request resets the count
    When I send 2 requests that result in a "503" response in a row
    And I send 1 request that is successful
    And I send 2 requests that result in a "503" response in a row
    Then the next request is sent

  Scenario: After the 30-second cooldown, the next request is sent
    When I send 3 requests that result in a "503" response in a row
    And I wait 29 seconds
    Then the next request fails without being sent
    When I wait 1 more second
    Then the next request is sent

  Scenario: After a cooldown, a successful trial request closes the breaker
    When I send 3 requests that result in a "503" response in a row
    And I wait 30 seconds
    And I send 1 request that is successful
    And I send 2 requests that result in a "503" response in a row
    Then the next request is sent

  Scenario: After a cooldown, a failed trial request opens the breaker again
    When I send 3 requests that result in a "503" response in a row
    And I wait 30 seconds
    And I send 1 request that results in a "503" response
    Then the next request fails without being sent
    When I wait 29 seconds
    Then the next request fails without being sent
    When I wait 1 more second
    Then the next request is sent
