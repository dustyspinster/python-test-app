"""Client-side rate limiting, so the API tests don't send requests faster than a set limit."""

import time
from collections.abc import Callable


class RateLimiter:
    """A token bucket: up to `burst` requests can go at once, refilling at `rate` per second.

    A request that finds no capacity left waits until there is some, instead of failing.
    The clock and sleep are passed in so tests can use a fake clock instead of waiting for real.
    """

    def __init__(
        self,
        rate: float,
        burst: int,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.rate = rate
        self.burst = burst
        self._clock = clock
        self._sleep = sleep
        # Starts full, so the first burst goes through straight away
        self._tokens = float(burst)
        self._updated = clock()

    def _refill(self) -> None:
        now = self._clock()
        self._tokens = min(self.burst, self._tokens + (now - self._updated) * self.rate)
        self._updated = now

    def acquire(self) -> float:
        """Wait until a request is allowed, then use up one slot. Returns the seconds waited."""
        self._refill()
        waited = 0.0
        if self._tokens < 1:
            waited = (1 - self._tokens) / self.rate
            self._sleep(waited)
            self._refill()
        self._tokens -= 1
        return waited
