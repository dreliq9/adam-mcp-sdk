"""Tests for `adam-mcp audit`."""
from pathlib import Path
from adam_mcp_cli.cmd_new import scaffold_new_mcp
from adam_mcp_cli.cmd_audit import audit_project


def test_audit_passes_freshly_scaffolded_project(tmp_target: Path):
    scaffold_new_mcp(name="test-mcp", description="x", target_dir=tmp_target)
    report = audit_project(tmp_target)
    assert report["status"] in ("OK", "WARN"), f"Expected OK/WARN, got {report}"
    assert all(f["severity"] != "FAIL" for f in report.get("findings", [])), report


def test_audit_fails_missing_llm_guide(tmp_target: Path):
    scaffold_new_mcp(name="test-mcp", description="x", target_dir=tmp_target)
    (tmp_target / "LLM_GUIDE.md").unlink()
    report = audit_project(tmp_target)
    assert report["status"] == "FAIL"
    assert any("LLM_GUIDE" in f["message"] for f in report["findings"])


def test_audit_fails_missing_passthrough(tmp_target: Path):
    scaffold_new_mcp(name="test-mcp", description="x", target_dir=tmp_target)
    (tmp_target / "test_mcp" / "mcp" / "escape_tools.py").write_text("# no passthrough here\n")
    report = audit_project(tmp_target)
    assert report["status"] == "FAIL"
    assert any("passthrough" in f["message"].lower() for f in report["findings"])


def test_audit_warns_when_advisory_mode_on_external_mcp(tmp_target: Path):
    """An MCP that doesn't import adam-mcp-py runs in advisory mode (WARN, not FAIL)."""
    tmp_target.mkdir(parents=True)
    (tmp_target / "pyproject.toml").write_text('[project]\nname = "external"\nversion = "0.1.0"\n')
    report = audit_project(tmp_target)
    assert report["mode"] == "advisory"
    assert all(f["severity"] != "FAIL" for f in report.get("findings", [])), report
