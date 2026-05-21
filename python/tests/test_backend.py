"""Tests for adam_mcp_py.BackendProtocol — implements §2.6."""

from adam_mcp_py import BackendProtocol, detect_backend


class LocalBackend:
    mode_tag = "[LOCAL]"
    available = True

    def call(self, payload: dict) -> dict:
        return {"echo": payload}


class WebBackend:
    mode_tag = "[WEB]"
    available = False

    def call(self, payload: dict) -> dict:
        return {"web_echo": payload}


def test_backend_protocol_runtime_check():
    local = LocalBackend()
    assert isinstance(local, BackendProtocol)


def test_detect_backend_returns_first_available():
    backends = [WebBackend(), LocalBackend()]
    selected = detect_backend(backends)
    assert isinstance(selected, LocalBackend)


def test_detect_backend_returns_none_if_none_available():
    class Down:
        mode_tag = "[DOWN]"
        available = False

        def call(self, payload):
            return {}

    selected = detect_backend([Down()])
    assert selected is None
