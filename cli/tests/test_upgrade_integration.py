"""End-to-end integration test for `adam-mcp upgrade`."""
from pathlib import Path
import shutil


def test_full_upgrade_flow_on_stale_fixture(tmp_path: Path, monkeypatch):
    """Copy adam-greet, set its pin to a stale version, run upgrade, verify Result shape.

    This mocks `uv sync` because we don't want test runs to mutate the real venv.
    """
    from adam_mcp_cli.cmd_upgrade import upgrade
    from adam_mcp_cli import cmd_upgrade as cu

    # Copy the reference MCP into tmp_path/mcp
    repo_root = Path(__file__).resolve().parents[2]
    src = repo_root / "reference-mcp" / "adam-greet"
    dst = tmp_path / "adam-greet-fixture"
    shutil.copytree(src, dst)

    # Edit pyproject.toml to set a stale pin
    pyproj = dst / "pyproject.toml"
    text = pyproj.read_text()
    # Replace whatever the current pin is with ==0.0.1 (definitely stale)
    import re
    new_text = re.sub(r"adam-mcp-py\s*[=<>!]*\s*[\d.]+", "adam-mcp-py==0.0.1", text)
    pyproj.write_text(new_text)

    # Mock uv sync so the test doesn't actually run it
    class FakeRun:
        returncode = 0
        stdout = ""
        stderr = ""

    monkeypatch.setattr(cu.subprocess, "run", lambda *a, **kw: FakeRun())
    # Force fetch_latest_version to return a known target
    monkeypatch.setattr(cu, "fetch_latest_version", lambda: "0.2.0")

    report = upgrade(dst, target=None, dry_run=False)

    # Pin updated
    final_pyproj = pyproj.read_text()
    assert "adam-mcp-py==0.2.0" in final_pyproj, final_pyproj
    assert "adam-mcp-py==0.0.1" not in final_pyproj

    # Result envelope shape
    for key in ["status", "value", "hint", "mode_tag", "raw", "metrics", "diagnostics"]:
        assert key in report, f"Missing key: {key}"

    # mode_tag should encode the version transition
    assert report["mode_tag"] == "upgrade:0.0.1→0.2.0"

    # Status is OK or WARN (not FAIL) — fixture is well-formed
    assert report["status"] in ("OK", "WARN"), report
