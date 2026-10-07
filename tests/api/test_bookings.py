import requests


def test_create_booking(base_url, booking_payload, json_headers):
    response = requests.post(
        f"{base_url}/booking", json=booking_payload, headers=json_headers, timeout=15
    )
    body = response.json()

    assert response.status_code == 200
    assert isinstance(body["bookingid"], int)
    assert body["booking"]["firstname"] == booking_payload["firstname"]
    assert body["booking"]["totalprice"] == booking_payload["totalprice"]
    assert body["booking"]["bookingdates"] == booking_payload["bookingdates"]


def test_get_booking(base_url, new_booking, booking_payload, json_headers):
    response = requests.get(f"{base_url}/booking/{new_booking}", headers=json_headers, timeout=15)
    body = response.json()

    assert response.status_code == 200
    assert body["firstname"] == booking_payload["firstname"]
    assert body["lastname"] == booking_payload["lastname"]
    assert isinstance(body["depositpaid"], bool)


def test_update_booking(base_url, new_booking, booking_payload, auth_headers):
    updated = {**booking_payload, "firstname": "Updated"}
    response = requests.put(
        f"{base_url}/booking/{new_booking}", json=updated, headers=auth_headers, timeout=15
    )

    assert response.status_code == 200
    assert response.json()["firstname"] == "Updated"


def test_delete_booking(base_url, new_booking, auth_headers, json_headers):
    response = requests.delete(f"{base_url}/booking/{new_booking}", headers=auth_headers, timeout=15)
    assert response.status_code == 201

    follow_up = requests.get(f"{base_url}/booking/{new_booking}", headers=json_headers, timeout=15)
    assert follow_up.status_code == 404


def test_get_nonexistent_booking(base_url, json_headers):
    response = requests.get(f"{base_url}/booking/99999999", headers=json_headers, timeout=15)
    assert response.status_code == 404


def test_update_without_auth_is_forbidden(base_url, new_booking, booking_payload, json_headers):
    response = requests.put(
        f"{base_url}/booking/{new_booking}", json=booking_payload, headers=json_headers, timeout=15
    )
    assert response.status_code == 403


def test_delete_without_auth_is_forbidden(base_url, new_booking, json_headers):
    response = requests.delete(f"{base_url}/booking/{new_booking}", headers=json_headers, timeout=15)
    assert response.status_code == 403


def test_auth_returns_token(base_url, json_headers):
    response = requests.post(
        f"{base_url}/auth",
        json={"username": "admin", "password": "password123"},
        headers=json_headers,
        timeout=15,
    )
    assert response.status_code == 200
    assert response.json()["token"]


def test_auth_with_bad_credentials_returns_no_token(base_url, json_headers):
    response = requests.post(
        f"{base_url}/auth",
        json={"username": "admin", "password": "wrong"},
        headers=json_headers,
        timeout=15,
    )
    # This API returns 200 even for bad credentials, with a "reason" field instead of a token
    assert "token" not in response.json()
    assert response.json().get("reason") == "Bad credentials"