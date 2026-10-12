import requests
from pytest_bdd import given, parsers, scenarios, then, when

from tests.api.schemas import BOOKING, CREATED_BOOKING, assert_matches_schema

scenarios("features/bookings.feature")


@given("a booking exists", target_fixture="booking_id")
def booking_exists(new_booking):
    return new_booking


@when("a guest creates a booking", target_fixture="response")
def guest_creates_booking(base_url, booking_payload, json_headers):
    return requests.post(f"{base_url}/booking", json=booking_payload, headers=json_headers, timeout=15)


@when(
    parsers.parse('an admin replaces the booking with first name "{name}"'),
    target_fixture="response",
)
def admin_replaces_booking(base_url, booking_id, booking_payload, authed, name):
    return authed.request(
        "PUT", f"{base_url}/booking/{booking_id}", json={**booking_payload, "firstname": name}
    )


@when(parsers.parse('an admin sets "{field}" to "{value}"'), target_fixture="response")
def admin_patches_booking(base_url, booking_id, authed, field, value):
    return authed.request("PATCH", f"{base_url}/booking/{booking_id}", json={field: value})


@when("an admin deletes the booking", target_fixture="response")
def admin_deletes_booking(base_url, booking_id, authed):
    return authed.request("DELETE", f"{base_url}/booking/{booking_id}")


@when(parsers.parse("a guest tries to {action} the booking without logging in"), target_fixture="response")
def guest_changes_booking(base_url, booking_id, booking_payload, json_headers, action):
    method = {"update": "PUT", "delete": "DELETE"}[action]
    return requests.request(
        method, f"{base_url}/booking/{booking_id}", json=booking_payload, headers=json_headers, timeout=15
    )


@then(parsers.parse("the response status is {status:d}"))
def response_status(response, status):
    assert response.status_code == status


@then("the response is a valid new booking")
def valid_new_booking(response, booking_payload):
    assert_matches_schema(response.json(), CREATED_BOOKING)
    assert response.json()["booking"] == booking_payload


@then("the booking can be retrieved with the same details")
def booking_retrievable(response, base_url, booking_payload, json_headers):
    booking_id = response.json()["bookingid"]
    fetched = requests.get(f"{base_url}/booking/{booking_id}", headers=json_headers, timeout=15)

    assert fetched.status_code == 200
    assert_matches_schema(fetched.json(), BOOKING)
    assert fetched.json() == booking_payload


@then(parsers.parse('the booking matches the original except "{field}" is "{value}"'))
def only_field_changed(response, booking_payload, field, value):
    assert_matches_schema(response.json(), BOOKING)
    assert response.json() == {**booking_payload, field: value}


@then("the booking can no longer be found")
def booking_gone(base_url, booking_id, json_headers):
    response = requests.get(f"{base_url}/booking/{booking_id}", headers=json_headers, timeout=15)
    assert response.status_code == 404
