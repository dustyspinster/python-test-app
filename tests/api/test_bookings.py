import requests

from tests.api.schemas import (
    AUTH_FAILURE,
    AUTH_TOKEN,
    BOOKING_IDS,
    assert_matches_schema,
)


def test_list_bookings(base_url, new_booking, json_headers):
    response = requests.get(f"{base_url}/booking", headers=json_headers, timeout=15)

    assert response.status_code == 200
    assert_matches_schema(response.json(), BOOKING_IDS)
    assert {"bookingid": new_booking} in response.json()


def test_search_bookings_by_name(base_url, new_booking, booking_payload, json_headers):
    names = {"firstname": booking_payload["firstname"], "lastname": booking_payload["lastname"]}
    response = requests.get(f"{base_url}/booking", params=names, headers=json_headers, timeout=15)

    assert response.status_code == 200
    assert_matches_schema(response.json(), BOOKING_IDS)
    assert {"bookingid": new_booking} in response.json()


def test_get_nonexistent_booking(base_url, json_headers):
    response = requests.get(f"{base_url}/booking/99999999", headers=json_headers, timeout=15)
    assert response.status_code == 404


def test_auth_returns_token(base_url, json_headers):
    response = requests.post(
        f"{base_url}/auth",
        json={"username": "admin", "password": "password123"},
        headers=json_headers,
        timeout=15,
    )
    assert response.status_code == 200
    assert_matches_schema(response.json(), AUTH_TOKEN)


def test_auth_with_bad_credentials_returns_no_token(base_url, json_headers):
    response = requests.post(
        f"{base_url}/auth",
        json={"username": "admin", "password": "wrong"},
        headers=json_headers,
        timeout=15,
    )
    # This API returns 200 even for bad credentials, with a "reason" field instead of a token
    assert_matches_schema(response.json(), AUTH_FAILURE)
    assert response.json()["reason"] == "Bad credentials"


def test_rejected_token_is_refreshed_once(base_url, new_booking, booking_payload, authed, caplog):
    # Simulate a token wiped by Restful-booker's periodic reset
    authed.token = "expired"
    response = authed.request("PATCH", f"{base_url}/booking/{new_booking}", json={"firstname": "Retried"})

    assert response.status_code == 200
    assert response.json() == {**booking_payload, "firstname": "Retried"}
    assert "returned 403; logging in again" in caplog.text
