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


def test_registry_contains_all_known_rule_ids():
    """REGISTRY must enumerate every rule the audit currently enforces."""
    from adam_mcp_cli.audit_rules import REGISTRY
    rule_ids = {r.rule_id for r in REGISTRY}
    expected = {"§3.13", "§3.14", "§3.15", "§3.16", "§3.17", "§2.7", "§2.11", "§6.30"}
    missing = expected - rule_ids
    assert not missing, f"REGISTRY missing rule_ids: {missing}"
