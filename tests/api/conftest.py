import logging
from collections.abc import Iterator
from typing import Any

import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
JSON_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

log = logging.getLogger(__name__)


def get_token() -> str:
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": "admin", "password": "password123"},
        headers=JSON_HEADERS,
        timeout=15,
    )
    assert response.status_code == 200
    return response.json()["token"]


class AuthedClient:
    """Sends requests with a login token, logging in again once if the token is rejected.

    Restful-booker resets itself every 10 minutes, which also invalidates login tokens.
    A test whose token was issued just before a reset gets 403 Forbidden afterwards, so
    a 403 triggers one retry with a fresh token. A real permissions bug fails again on
    the retry, so it still fails the test.
    """

    def __init__(self) -> None:
        self.token = get_token()

    def _send(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        headers = {**JSON_HEADERS, "Cookie": f"token={self.token}"}
        return requests.request(method, url, headers=headers, timeout=15, **kwargs)

    def request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        response = self._send(method, url, **kwargs)
        if response.status_code == 403:
            log.warning("%s %s returned 403; logging in again and retrying once", method, url)
            self.token = get_token()
            response = self._send(method, url, **kwargs)
        return response


@pytest.fixture
def base_url():
    return BASE_URL


@pytest.fixture
def json_headers():
    return JSON_HEADERS


@pytest.fixture
def authed():
    return AuthedClient()


@pytest.fixture
def booking_payload():
    return {
        "firstname": "Test",
        "lastname": "User",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-11-01", "checkout": "2026-11-05"},
        "additionalneeds": "Breakfast",
    }


@pytest.fixture
def new_booking(base_url, booking_payload, json_headers, authed) -> Iterator[int]:
    response = requests.post(f"{base_url}/booking", json=booking_payload, headers=json_headers, timeout=15)
    assert response.status_code == 200
    booking_id = response.json()["bookingid"]
    yield booking_id
    # Cleanup so tests don't leave data behind
    authed.request("DELETE", f"{base_url}/booking/{booking_id}")
