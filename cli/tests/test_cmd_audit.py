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


def test_self_check_catches_unreferenced_registry_rule(tmp_path: Path, monkeypatch):
    """Self-check fails when REGISTRY has a rule_id that HOUSE_STYLE.md doesn't document."""
    from adam_mcp_cli.main import _self_check_v2
    from adam_mcp_cli.audit_rules import REGISTRY, AuditRule, Finding

    # HOUSE_STYLE.md missing §9.42; CHANGELOG empty
    (tmp_path / "HOUSE_STYLE.md").write_text("# Spec\n\n## §3.13\nSPEC.md required.\n")
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n")
    monkeypatch.setattr("adam_mcp_cli.main._SELF_CHECK_REPO_ROOT", tmp_path)

    # Inject a synthetic rule into the live REGISTRY for the test
    fake_rule = AuditRule("§9.42", "HOUSE_STYLE.md §9.42", "FAIL", "fake", lambda p: [])
    REGISTRY.append(fake_rule)
    try:
        report = _self_check_v2()
    finally:
        REGISTRY.remove(fake_rule)

    assert report["status"] == "FAIL", report
    assert any("§9.42" in f["message"] for f in report["findings"]), report


def test_self_check_catches_orphan_changelog_breaking(tmp_path: Path, monkeypatch):
    """Self-check fails when a CHANGELOG ### Breaking bullet references a non-existent rule_id."""
    from adam_mcp_cli.main import _self_check_v2

    # Build a fake repo root with a synthetic CHANGELOG and HOUSE_STYLE.md
    (tmp_path / "HOUSE_STYLE.md").write_text("# Spec\n\n## §3.13\nSPEC.md required.\n")
    (tmp_path / "CHANGELOG.md").write_text(
        "# Changelog\n\n## [0.2.0] — 2026-05-10\n\n### Breaking\n\n"
        "- **§9.99** — Nonexistent rule.\n  Migration: this should fail self-check.\n"
    )
    monkeypatch.setattr("adam_mcp_cli.main._SELF_CHECK_REPO_ROOT", tmp_path)

    report = _self_check_v2()
    assert report["status"] == "FAIL", report
    assert any("§9.99" in f["message"] for f in report["findings"]), report
