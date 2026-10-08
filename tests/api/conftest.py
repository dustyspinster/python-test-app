import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
JSON_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


@pytest.fixture
def base_url():
    return BASE_URL


@pytest.fixture
def json_headers():
    return JSON_HEADERS


@pytest.fixture
def auth_token():
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": "admin", "password": "password123"},
        headers=JSON_HEADERS,
        timeout=15,
    )
    assert response.status_code == 200
    return response.json()["token"]


@pytest.fixture
def auth_headers(auth_token):
    return {**JSON_HEADERS, "Cookie": f"token={auth_token}"}


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
def new_booking(base_url, booking_payload, json_headers, auth_headers):
    response = requests.post(f"{base_url}/booking", json=booking_payload, headers=json_headers, timeout=15)
    assert response.status_code == 200
    booking_id = response.json()["bookingid"]
    yield booking_id
    # Cleanup so tests don't leave data behind
    requests.delete(f"{base_url}/booking/{booking_id}", headers=auth_headers, timeout=15)
