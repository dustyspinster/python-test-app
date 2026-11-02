"""The API suite's circuit breaker, run against fake responses and a fake clock.

No requests reach Restful-booker here: each "request" returns the response the step
names, or raises the error a real outage would, so every state can be forced on demand.
"""

import pytest
import requests
from pytest_bdd import given, parsers, scenarios, then, when

from tests.api.circuit_breaker import CircuitBreaker, CircuitOpenError

scenarios("features/circuit_breaker.feature")

# The fake clock fixture, clock, is in conftest.py


@pytest.fixture
def sent():
    # How many requests actually went out, as opposed to being stopped by the breaker
    return []


def fake_send(sent: list, response: str):
    def send() -> requests.Response:
        sent.append(response)
        if response == "connection refused":
            raise requests.ConnectionError("Connection refused")
        if response == "timed out":
            raise requests.Timeout("Timed out")
        fake = requests.Response()
        fake.status_code = int(response)
        return fake

    return send


def send_request(breaker: CircuitBreaker, sent: list, response: str) -> None:
    # A failure the service caused is the expected outcome here, not an error in the test
    try:
        breaker.call(fake_send(sent, response))
    except (requests.ConnectionError, requests.Timeout):
        pass


@given(
    parsers.parse("the breaker trips after {threshold:d} failures in a row and waits {cooldown:d} seconds"),
    target_fixture="breaker",
)
def breaker(clock, threshold, cooldown):
    return CircuitBreaker(threshold, cooldown, clock=clock.time)


@when(
    parsers.re(
        r'I send (?P<count>\d+) requests? that results? in a "(?P<response>[^"]+)" response(?: in a row)?'
    )
)
def send_requests(breaker, sent, count, response):
    for _ in range(int(count)):
        before = len(sent)
        send_request(breaker, sent, response)
        assert len(sent) == before + 1, "The breaker stopped a request this step expected to send"


@when("I send 1 request that is successful")
def send_successful_request(breaker, sent):
    send_requests(breaker, sent, 1, "200")


@when(parsers.re(r"I wait (?P<seconds>\d+)(?: more)? seconds?"))
def wait(clock, seconds):
    clock.sleep(int(seconds))


@then("the next request is sent")
def next_request_sent(breaker, sent):
    before = len(sent)
    breaker.call(fake_send(sent, "200"))
    assert len(sent) == before + 1


@then("the next request fails without being sent")
def next_request_blocked(breaker, sent):
    before = len(sent)
    with pytest.raises(CircuitOpenError):
        breaker.call(fake_send(sent, "200"))
    assert len(sent) == before, "The request was sent anyway"
