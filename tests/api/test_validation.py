"""How the booking API handles bad input and missing records.

Restful-booker has no published validation rules, so these tests expect only
what any REST API should do: reject a client's mistake with a 4xx status
instead of crashing or saving bad data. Where it doesn't, the test is a strict
expected failure with the bug as its reason, so the suite stays green and a
fix shows up as an unexpected pass that fails the build.
"""

import pytest
import requests

# Fields the API needs to create a booking (additionalneeds is optional)
REQUIRED_FIELDS = ["firstname", "lastname", "totalprice", "depositpaid", "bookingdates"]


def known_bug(reason):
    # Only a wrong status code counts as the bug; a timeout or crash still fails the test
    return pytest.mark.xfail(reason=reason, raises=AssertionError, strict=True)


@pytest.fixture
def create_booking(base_url, json_headers, authed):
    """POST a booking payload, and delete anything the API saved once the test ends."""
    created = []

    def create(payload):
        response = requests.post(f"{base_url}/booking", json=payload, headers=json_headers, timeout=15)
        if response.status_code == 200:
            created.append(response.json()["bookingid"])
        return response

    yield create
    for booking_id in created:
        authed.request("DELETE", f"{base_url}/booking/{booking_id}")


# --- Bad input the API rejects correctly


def test_malformed_json_is_rejected(base_url, json_headers):
    response = requests.post(f"{base_url}/booking", data="{not json", headers=json_headers, timeout=15)
    assert response.status_code == 400


def test_unsupported_response_format_is_rejected(base_url, booking_payload):
    # The API only speaks JSON and XML; anything else gets 418 "I'm a Teapot"
    headers = {"Content-Type": "application/json", "Accept": "text/plain"}
    response = requests.post(f"{base_url}/booking", json=booking_payload, headers=headers, timeout=15)
    assert response.status_code == 418


def test_non_numeric_booking_id_is_not_found(base_url, json_headers):
    response = requests.get(f"{base_url}/booking/abc", headers=json_headers, timeout=15)
    assert response.status_code == 404


def test_optional_field_can_be_left_out(create_booking, booking_payload):
    payload = {k: v for k, v in booking_payload.items() if k != "additionalneeds"}
    response = create_booking(payload)

    assert response.status_code == 200
    assert "additionalneeds" not in response.json()["booking"]


def test_health_check_responds(base_url):
    # Restful-booker's health check answers 201 Created rather than the usual 200
    assert requests.get(f"{base_url}/ping", timeout=15).status_code == 201


# --- Bad input the API mishandles (known bugs)


@known_bug("Restful-booker returns 500 Internal Server Error instead of 400 when a required field is missing")
@pytest.mark.parametrize("field", REQUIRED_FIELDS)
def test_missing_required_field_is_rejected(create_booking, booking_payload, field):
    payload = {k: v for k, v in booking_payload.items() if k != field}
    assert create_booking(payload).status_code == 400


@known_bug("Restful-booker returns 500 Internal Server Error instead of 400 for an empty body")
def test_empty_body_is_rejected(create_booking):
    assert create_booking({}).status_code == 400


@known_bug("Restful-booker accepts a non-numeric totalprice and saves it as null")
def test_non_numeric_price_is_rejected(create_booking, booking_payload):
    assert create_booking({**booking_payload, "totalprice": "abc"}).status_code == 400


@known_bug("Restful-booker accepts a checkout date before the checkin date")
def test_checkout_before_checkin_is_rejected(create_booking, booking_payload):
    dates = {"checkin": "2026-11-05", "checkout": "2026-11-01"}
    assert create_booking({**booking_payload, "bookingdates": dates}).status_code == 400


@known_bug("Restful-booker accepts a checkin value that isn't a date")
def test_invalid_date_is_rejected(create_booking, booking_payload):
    dates = {"checkin": "not-a-date", "checkout": "2026-11-05"}
    assert create_booking({**booking_payload, "bookingdates": dates}).status_code == 400


@known_bug("Restful-booker returns 405 Method Not Allowed instead of 404 for a booking that doesn't exist")
@pytest.mark.parametrize("method", ["PUT", "DELETE"])
def test_changing_a_missing_booking_is_not_found(base_url, authed, booking_payload, method):
    response = authed.request(method, f"{base_url}/booking/99999999", json=booking_payload)
    assert response.status_code == 404
