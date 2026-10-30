"""The API suite's rate limiter, run against a fake clock.

No requests reach Restful-booker here: "sending" a request means passing it through
the limiter, and the fake clock moves forward only when a step waits or the limiter
makes a request wait, so the timings are exact and these tests run instantly.
"""

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.api.rate_limiter import RateLimiter

scenarios("features/rate_limiter.feature")


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def time(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += seconds


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def waits():
    # Seconds each request in the latest batch waited, in the order they were sent
    return []


@given(
    parsers.parse("the limit is {rate:d} requests per second with bursts up to {burst:d}"),
    target_fixture="limiter",
)
def limiter(clock, rate, burst):
    return RateLimiter(rate, burst, clock=clock.time, sleep=clock.sleep)


@given(parsers.parse("I have sent {count:d} requests at once"))
@when(parsers.parse("I send {count:d} requests at once"))
@when(parsers.parse("I send {count:d} more requests at once"))
def send_at_once(limiter, waits, count):
    waits[:] = [limiter.acquire() for _ in range(count)]


@when(parsers.parse("I send {per_second:d} requests per second for {seconds:d} seconds"))
def send_steadily(limiter, clock, waits, per_second, seconds):
    waits.clear()
    for i in range(per_second * seconds):
        # Evenly spaced; a request the limiter held back pushes the rest later, as it would for real
        clock.now = max(clock.now, i / per_second)
        waits.append(limiter.acquire())


NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "ten": 10}


@when(parsers.re(r"I wait for (?P<word>\w+) seconds?"))
def wait_seconds(clock, word):
    assert word in NUMBER_WORDS, f"No number for {word!r}; add it to NUMBER_WORDS"
    clock.sleep(NUMBER_WORDS[word])


@then("no request waits before it is sent")
def no_request_waits(waits):
    assert waits and not any(waits), f"Seconds each request waited: {waits}"


@then(parsers.parse("the first {count:d} requests are sent without waiting"))
@then(parsers.parse("none of the first {count:d} requests wait"))
def first_requests_dont_wait(waits, count):
    assert len(waits) >= count and not any(waits[:count]), f"Seconds each request waited: {waits}"


@then(parsers.re(r"(?:the|an) (?P<number>\d+)(?:st|nd|rd|th) request waits before it is sent"))
def request_waits(limiter, waits, number):
    waited = waits[int(number) - 1]
    # Exactly one slot's worth: at 10 per second, a slot frees up every 0.1 seconds
    assert waited == pytest.approx(1 / limiter.rate), f"Request {number} waited {waited} seconds"
