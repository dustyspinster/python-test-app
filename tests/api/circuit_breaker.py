"""A circuit breaker, so the API tests fail fast while Restful-booker is down."""

import time
from collections.abc import Callable

import requests

# Responses that mean the service itself is down. Other errors, such as 400 or 404, mean it's up
# and answering. Restful-booker also returns 500 for a booking with missing fields, so 500 is left out
OUTAGE_STATUSES = {502, 503, 504}


class CircuitOpenError(Exception):
    """Raised instead of sending a request while the breaker is open."""


class CircuitBreaker:
    """Stops sending requests after `threshold` failures in a row, for `cooldown` seconds.

    After the cooldown, one trial request is sent: if it succeeds the breaker closes and
    counting starts over; if it fails the breaker opens for another full cooldown.
    The clock is passed in so tests can use a fake clock instead of waiting for real.
    """

    def __init__(self, threshold: int, cooldown: float, clock: Callable[[], float] = time.monotonic) -> None:
        self.threshold = threshold
        self.cooldown = cooldown
        self._clock = clock
        self._failures = 0
        self._opened_at: float | None = None

    def call(self, send: Callable[[], requests.Response], description: str = "request") -> requests.Response:
        """Send the request unless the breaker is open, and count whether the service failed it."""
        if self._opened_at is not None:
            remaining = self._opened_at + self.cooldown - self._clock()
            if remaining > 0:
                raise CircuitOpenError(
                    f"Not sending {description}: the service failed {self._failures} requests in a row, "
                    f"so the circuit breaker is open for another {remaining:.0f} s"
                )
            # Cooldown over: this request is the trial, and its result decides what happens next

        try:
            response = send()
        except (requests.ConnectionError, requests.Timeout):
            self._failed()
            raise
        if response.status_code in OUTAGE_STATUSES:
            self._failed()
        else:
            self._failures = 0
            self._opened_at = None
        return response

    def _failed(self) -> None:
        self._failures += 1
        # Only a success resets the count, so a failed trial is still over the threshold and reopens it
        if self._failures >= self.threshold:
            self._opened_at = self._clock()
