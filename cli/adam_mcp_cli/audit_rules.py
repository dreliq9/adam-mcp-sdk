"""Mechanical conformance checks against HOUSE_STYLE.md.

Each rule returns a list of findings. Findings have severity OK/WARN/FAIL and a hint
pointing back to the spec section that was violated.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
import sys

# Make spec/schemas/ importable
_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "spec"))
from schemas.spec_md_lint import check_spec_md  # noqa: E402
from schemas.llm_guide_lint import check_llm_guide  # noqa: E402


@dataclass
class Finding:
    rule: str
    severity: str  # "OK" | "WARN" | "FAIL"
    message: str
    hint: str

    def to_dict(self) -> dict:
        return {"rule": self.rule, "severity": self.severity, "message": self.message, "hint": self.hint}


def _is_advisory(project_root: Path) -> bool:
    """Advisory mode: project doesn't depend on adam-mcp-py. Treat findings as WARN at most."""
    pyproject = project_root / "pyproject.toml"
    if not pyproject.exists():
        return True
    return "adam-mcp-py" not in pyproject.read_text()


def _check_required_files(project_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    required = [
        ("SPEC.md", "§3.13"),
        ("LLM_GUIDE.md", "§3.14"),
        ("CLAUDE.md", "§3.15"),
        ("README.md", "§3.17"),
        ("CHANGELOG.md", "§3.17"),
        ("ROADMAP.md", "§3.17"),
        ("DECISIONS.md", "§3.17"),
        ("AUDIT.md", "§3.16"),
        ("server.json", "§3.17"),
        ("pyproject.toml", "§2.11"),
    ]
    for fname, rule in required:
        if not (project_root / fname).exists():
            findings.append(Finding(
                rule=rule,
                severity="FAIL",
                message=f"Missing required file: {fname}",
                hint=f"See HOUSE_STYLE.md {rule}",
            ))
    return findings


def _check_llm_guide_sections(project_root: Path) -> list[Finding]:
    missing = check_llm_guide(project_root / "LLM_GUIDE.md")
    return [
        Finding(rule="§3.14", severity="FAIL", message=m, hint="See HOUSE_STYLE.md §3.14")
        for m in missing
    ]


def _check_spec_md_sections(project_root: Path) -> list[Finding]:
    missing = check_spec_md(project_root / "SPEC.md")
    return [
        Finding(rule="§3.13", severity="FAIL", message=m, hint="See HOUSE_STYLE.md §3.13")
        for m in missing
    ]


def _check_passthrough_exists(project_root: Path) -> list[Finding]:
    """§6.30: every MCP must have an @passthrough-decorated tool."""
    found = False
    for py in project_root.rglob("*.py"):
        try:
            if "@passthrough" in py.read_text():
                found = True
                break
        except (UnicodeDecodeError, OSError):
            continue
    if not found:
        return [Finding(
            rule="§6.30",
            severity="FAIL",
            message="No @passthrough-decorated tool found anywhere in the project.",
            hint="Add an escape-hatch tool in <package>/mcp/escape_tools.py decorated with @passthrough. See HOUSE_STYLE.md §6.30.",
        )]
    return []


def _check_tool_files_naming(project_root: Path) -> list[Finding]:
    """§2.7: tools live in <package>/mcp/<area>_tools.py. Warn if a server.py has many tools."""
    findings: list[Finding] = []
    for server_py in project_root.rglob("mcp/server.py"):
        text = server_py.read_text()
        decorator_count = text.count(".tool()")
        if decorator_count > 30:
            findings.append(Finding(
                rule="§2.7",
                severity="WARN",
                message=f"{server_py} has {decorator_count} @tool decorations — split into _tools.py files",
                hint="See HOUSE_STYLE.md §2.7.",
            ))
    return findings


ALL_RULES: list[Callable[[Path], list[Finding]]] = [
    _check_required_files,
    _check_llm_guide_sections,
    _check_spec_md_sections,
    _check_passthrough_exists,
    _check_tool_files_naming,
]


def run_all_rules(project_root: Path) -> tuple[list[Finding], str]:
    """Run every rule. Returns (findings, mode) where mode is 'strict' or 'advisory'."""
    advisory = _is_advisory(project_root)
    findings: list[Finding] = []
    for rule in ALL_RULES:
        findings.extend(rule(project_root))
    if advisory:
        findings = [
            Finding(rule=f.rule, severity="WARN" if f.severity == "FAIL" else f.severity,
                    message=f.message, hint=f.hint)
            for f in findings
        ]
    return findings, ("advisory" if advisory else "strict")
