"""Structural test for /mcp-upgrade slash command markdown."""

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CMD = REPO / "claude-pack" / "commands" / "mcp-upgrade.md"


def test_mcp_upgrade_command_exists():
    assert CMD.exists(), f"Missing: {CMD}"


def test_mcp_upgrade_has_frontmatter():
    text = CMD.read_text(encoding="utf-8")
    assert text.startswith("---\n"), "Missing YAML frontmatter"
    assert "name: mcp-upgrade" in text
    assert "description:" in text


def test_mcp_upgrade_has_dry_run_gate():
    """Slash command must do a dry-run + ask before mutating."""
    text = CMD.read_text(encoding="utf-8")
    assert "--dry-run" in text, "Missing dry-run gate"


def test_mcp_upgrade_invokes_audit():
    """Slash command must run adam-mcp audit (or use the upgrade Result findings)."""
    text = CMD.read_text(encoding="utf-8")
    assert "adam-mcp upgrade" in text or "adam-mcp audit" in text


def test_mcp_upgrade_has_loop_bound():
    """Slash command must cap re-audit iterations to prevent oscillation."""
    text = CMD.read_text(encoding="utf-8").lower()
    assert "max" in text and ("iteration" in text or "loop" in text or "3" in text)


def test_mcp_upgrade_does_not_auto_commit():
    """Per CLAUDE.md, git operations need explicit approval."""
    text = CMD.read_text(encoding="utf-8").lower()
    # Either explicit "do not commit" instruction, or no git commit mention at all
    forbidden = ["git commit -m", "auto-commit", "automatically commit"]
    for phrase in forbidden:
        assert phrase not in text, f"Slash command must not auto-commit: found '{phrase}'"
