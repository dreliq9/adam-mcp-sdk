"""Tests for adam_greet escape-hatch tool."""
from adam_mcp_py import Status, is_passthrough
from adam_greet.mcp.escape_tools import compose_raw_greeting


def test_compose_raw_greeting_returns_template_verbatim():
    r = compose_raw_greeting({"template": "Greetings, traveler."})
    assert r.status == Status.OK
    assert r.value == "Greetings, traveler."


def test_compose_raw_greeting_is_marked_passthrough():
    assert is_passthrough(compose_raw_greeting)


def test_compose_raw_greeting_includes_raw_field():
    r = compose_raw_greeting({"template": "X"})
    assert r.raw == {"template": "X"}
