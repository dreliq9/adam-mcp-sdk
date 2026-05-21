"""Tests for adam_greet.mcp.greeting_tools."""

from adam_mcp_py import Status
from adam_greet.mcp.greeting_tools import compose_greeting, compose_personalized_greeting


def test_compose_greeting_ok():
    r = compose_greeting({"name": "Adam", "formality": 5})
    assert r.status == Status.OK
    assert "Adam" in r.value
    assert r.mode_tag == "[LOCAL]"


def test_compose_greeting_validates_input():
    r = compose_greeting({"name": "", "formality": 5})
    assert r.status == Status.FAIL
    assert r.hint is not None


def test_compose_personalized_greeting_uses_history():
    r = compose_personalized_greeting({"name": "Adam"})
    assert r.status == Status.OK
    assert "Adam" in r.value
