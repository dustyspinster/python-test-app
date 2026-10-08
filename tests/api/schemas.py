"""JSON schemas for Restful-booker responses, and a helper that validates against them.

The schemas are strict on purpose: every documented field is required with an exact
type, dates must be real ISO dates, and unexpected extra fields fail validation, so an
API change shows up as a test failure rather than passing silently.
"""

from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

BOOKING_DATES = {
    "type": "object",
    "properties": {
        "checkin": {"type": "string", "format": "date"},
        "checkout": {"type": "string", "format": "date"},
    },
    "required": ["checkin", "checkout"],
    "additionalProperties": False,
}

# GET /booking/{id}, PUT and PATCH responses
BOOKING = {
    "type": "object",
    "properties": {
        "firstname": {"type": "string", "minLength": 1},
        "lastname": {"type": "string", "minLength": 1},
        "totalprice": {"type": "integer", "minimum": 0},
        "depositpaid": {"type": "boolean"},
        "bookingdates": BOOKING_DATES,
        # Optional in the API: bookings can be created without it
        "additionalneeds": {"type": "string"},
    },
    "required": ["firstname", "lastname", "totalprice", "depositpaid", "bookingdates"],
    "additionalProperties": False,
}

# POST /booking response
CREATED_BOOKING = {
    "type": "object",
    "properties": {
        "bookingid": {"type": "integer", "minimum": 1},
        "booking": BOOKING,
    },
    "required": ["bookingid", "booking"],
    "additionalProperties": False,
}

# GET /booking response, with or without search filters
BOOKING_IDS = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {"bookingid": {"type": "integer", "minimum": 1}},
        "required": ["bookingid"],
        "additionalProperties": False,
    },
}

# POST /auth with valid credentials
AUTH_TOKEN = {
    "type": "object",
    "properties": {"token": {"type": "string", "minLength": 1}},
    "required": ["token"],
    "additionalProperties": False,
}

# POST /auth with bad credentials (the API still returns 200)
AUTH_FAILURE = {
    "type": "object",
    "properties": {"reason": {"type": "string", "minLength": 1}},
    "required": ["reason"],
    "additionalProperties": False,
}


def assert_matches_schema(data: Any, schema: dict[str, Any]) -> None:
    """Fail with every schema violation listed, each with its path in the response."""
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    if errors:
        problems = "\n".join(f"  {'/'.join(map(str, e.path)) or '(root)'}: {e.message}" for e in errors)
        raise AssertionError(f"Response does not match schema:\n{problems}")
