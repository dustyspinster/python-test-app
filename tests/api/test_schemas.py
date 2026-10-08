"""Offline checks that the schemas reject bad data, so a passing API test means something."""

import pytest

from tests.api.schemas import BOOKING, BOOKING_IDS, assert_matches_schema

VALID_BOOKING = {
    "firstname": "Test",
    "lastname": "User",
    "totalprice": 150,
    "depositpaid": True,
    "bookingdates": {"checkin": "2026-11-01", "checkout": "2026-11-05"},
    "additionalneeds": "Breakfast",
}


def test_valid_booking_passes():
    assert_matches_schema(VALID_BOOKING, BOOKING)


def test_additionalneeds_is_optional():
    booking = {k: v for k, v in VALID_BOOKING.items() if k != "additionalneeds"}
    assert_matches_schema(booking, BOOKING)


@pytest.mark.parametrize(
    "change, expected_problem",
    [
        ({"lastname": None}, "lastname: None is not of type 'string'"),
        ({"totalprice": "150"}, "totalprice: '150' is not of type 'integer'"),
        ({"depositpaid": "yes"}, "depositpaid: 'yes' is not of type 'boolean'"),
        ({"bookingdates": {"checkin": "2026-13-45", "checkout": "2026-11-05"}}, "is not a 'date'"),
        ({"bookingdates": {"checkin": "2026-11-01"}}, "'checkout' is a required property"),
        ({"surprise": 1}, "Additional properties are not allowed ('surprise' was unexpected)"),
    ],
)
def test_invalid_booking_fails(change, expected_problem):
    with pytest.raises(AssertionError, match="does not match schema") as failure:
        assert_matches_schema({**VALID_BOOKING, **change}, BOOKING)
    assert expected_problem in str(failure.value)


def test_missing_required_field_fails():
    booking = {k: v for k, v in VALID_BOOKING.items() if k != "firstname"}
    with pytest.raises(AssertionError, match="'firstname' is a required property"):
        assert_matches_schema(booking, BOOKING)


def test_every_problem_is_reported():
    with pytest.raises(AssertionError) as failure:
        assert_matches_schema({**VALID_BOOKING, "totalprice": "150", "depositpaid": "yes"}, BOOKING)
    assert "totalprice" in str(failure.value)
    assert "depositpaid" in str(failure.value)


def test_booking_ids_reject_non_integer_ids():
    with pytest.raises(AssertionError, match="'abc' is not of type 'integer'"):
        assert_matches_schema([{"bookingid": 1}, {"bookingid": "abc"}], BOOKING_IDS)
