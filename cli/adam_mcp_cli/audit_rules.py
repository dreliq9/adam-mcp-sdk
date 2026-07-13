"""Mechanical conformance checks against HOUSE_STYLE.md.

Each rule returns a list of findings. Findings have severity OK/WARN/FAIL and a hint
pointing back to the spec section that was violated.
"""

from __future__ import annotations
import ast
from dataclasses import dataclass
import os
from pathlib import Path
from typing import Callable, Iterator
import sys

# Make spec/schemas/ importable
_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "spec"))
from schemas.spec_md_lint import check_spec_md  # noqa: E402
from schemas.llm_guide_lint import check_llm_guide  # noqa: E402


_IGNORED_SOURCE_DIRECTORIES = {
    ".git",
    ".venv",
    "build",
    "dist",
    "node_modules",
    "site-packages",
}


def _project_python_files(project_root: Path) -> Iterator[Path]:
    """Yield project Python files without entering generated or third-party trees."""
    for current_root, directory_names, file_names in os.walk(project_root):
        directory_names[:] = [
            name for name in directory_names if name.casefold() not in _IGNORED_SOURCE_DIRECTORIES
        ]
        root = Path(current_root)
        for file_name in file_names:
            if file_name.endswith(".py"):
                yield root / file_name


@dataclass
class Finding:
    rule: str
    severity: str  # "OK" | "WARN" | "FAIL"
    message: str
    hint: str

    def to_dict(self) -> dict:
        return {
            "rule": self.rule,
            "severity": self.severity,
            "message": self.message,
            "hint": self.hint,
        }


@dataclass(frozen=True)
class AuditRule:
    """A single audit rule.

    rule_id is stable forever once published — never reassigned to a different rule.
    Removals recorded in DECISIONS.md.
    """

    rule_id: str  # e.g. "§3.13"
    spec_section: str  # e.g. "HOUSE_STYLE.md §3.13"
    severity_default: str  # "FAIL" or "WARN"
    description: str  # short human-readable name
    check: Callable[[Path], list[Finding]]


def _is_advisory(project_root: Path) -> bool:
    """Advisory mode: project doesn't depend on adam-mcp-py. Treat findings as WARN at most."""
    pyproject = project_root / "pyproject.toml"
    if not pyproject.exists():
        return True
    return "adam-mcp-py" not in pyproject.read_text(encoding="utf-8")


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
            findings.append(
                Finding(
                    rule=rule,
                    severity="FAIL",
                    message=f"Missing required file: {fname}",
                    hint=f"See HOUSE_STYLE.md {rule}",
                )
            )
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
    for py in _project_python_files(project_root):
        try:
            if "@passthrough" in py.read_text(encoding="utf-8"):
                found = True
                break
        except (UnicodeDecodeError, OSError):
            continue
    if not found:
        return [
            Finding(
                rule="§6.30",
                severity="FAIL",
                message="No @passthrough-decorated tool found anywhere in the project.",
                hint="Add an escape-hatch tool in <package>/mcp/escape_tools.py decorated with @passthrough. See HOUSE_STYLE.md §6.30.",
            )
        ]
    return []


def _check_validates_param_name(project_root: Path) -> list[Finding]:
    """§1.5: every @validates-decorated tool must name its first parameter `input`.

    The `validates` wrapper accepts `input` as its kwarg (matching the JSONSchema
    field name FastMCP generates from the original signature). If the decorated
    function uses a different first-param name, FastMCP introspects *that* name,
    publishes a schema field with the wrong name, and runtime calls FAIL with
    'unexpected keyword argument'.
    """
    findings: list[Finding] = []
    for py in _project_python_files(project_root):
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError, OSError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            for dec in node.decorator_list:
                target = dec.func if isinstance(dec, ast.Call) else dec
                name = (
                    target.attr
                    if isinstance(target, ast.Attribute)
                    else getattr(target, "id", None)
                )
                if name != "validates":
                    continue
                args = node.args.args
                first = args[0].arg if args else None
                if first != "input":
                    findings.append(
                        Finding(
                            rule="§1.5",
                            severity="FAIL",
                            message=(
                                f"{py}:{node.lineno} {node.name}() decorated with @validates "
                                f"but first parameter is {first!r}, not 'input'. "
                                f"FastMCP will publish a schema field named {first!r} "
                                f"while the validates wrapper expects 'input' — every call FAILs."
                            ),
                            hint="Rename the first parameter to `input`. See HOUSE_STYLE.md §1.5.",
                        )
                    )
                break
    return findings


def _check_result_keyword_only(project_root: Path) -> list[Finding]:
    """§1.1: Result envelope is kw_only. Positional `Result(...)` construction
    is invalid post-0.3.0 because envelope_version became the first field.

    Catches the 0.3.0 migration: any direct Result(x, y) call with positional
    args is a FAIL. Factory methods (Result.ok/.warn/.fail) and pure-keyword
    direct calls are fine.
    """
    findings: list[Finding] = []
    if _is_advisory(project_root):
        return findings
    for py in _project_python_files(project_root):
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            # Match `Result(...)` direct construction, not `Result.ok(...)` etc.
            if isinstance(func, ast.Name) and func.id == "Result" and node.args:
                findings.append(
                    Finding(
                        rule="§1.1",
                        severity="FAIL",
                        message=f"{py}:{node.lineno} — positional Result(...) construction is invalid (envelope is kw_only post-0.3.0)",
                        hint="Use Result.ok/.warn/.fail factory methods, or pass all args as keywords. See HOUSE_STYLE.md §1.1.",
                    )
                )
    return findings


def _check_tool_files_naming(project_root: Path) -> list[Finding]:
    """§2.7: tools live in <package>/mcp/<area>_tools.py. Warn if a server.py has many tools."""
    findings: list[Finding] = []
    for server_py in project_root.rglob("mcp/server.py"):
        text = server_py.read_text(encoding="utf-8")
        decorator_count = text.count(".tool()")
        if decorator_count > 30:
            findings.append(
                Finding(
                    rule="§2.7",
                    severity="WARN",
                    message=f"{server_py} has {decorator_count} @tool decorations — split into _tools.py files",
                    hint="See HOUSE_STYLE.md §2.7.",
                )
            )
    return findings


REGISTRY: list[AuditRule] = [
    AuditRule(
        "§1.1",
        "HOUSE_STYLE.md §1.1",
        "FAIL",
        "Result envelope construction is keyword-only (catches 0.3.0 migration)",
        _check_result_keyword_only,
    ),
    AuditRule(
        "§3.13",
        "HOUSE_STYLE.md §3.13",
        "FAIL",
        "SPEC.md present + has required sections",
        _check_spec_md_sections,
    ),
    AuditRule(
        "§3.14",
        "HOUSE_STYLE.md §3.14",
        "FAIL",
        "LLM_GUIDE.md present + has required sections",
        _check_llm_guide_sections,
    ),
    AuditRule(
        "§3.15",
        "HOUSE_STYLE.md §3.15",
        "FAIL",
        "Required project files present (CLAUDE.md, README.md, etc.)",
        _check_required_files,
    ),
    AuditRule(
        "§3.16", "HOUSE_STYLE.md §3.16", "FAIL", "AUDIT.md present", _check_required_files
    ),  # same checker covers it
    AuditRule(
        "§3.17",
        "HOUSE_STYLE.md §3.17",
        "FAIL",
        "README/CHANGELOG/ROADMAP/DECISIONS/server.json present",
        _check_required_files,
    ),  # same checker covers it
    AuditRule(
        "§1.5",
        "HOUSE_STYLE.md §1.5",
        "FAIL",
        "@validates-decorated tools name first parameter `input`",
        _check_validates_param_name,
    ),
    AuditRule(
        "§2.7",
        "HOUSE_STYLE.md §2.7",
        "WARN",
        "Tool files split by area (no over-stuffed server.py)",
        _check_tool_files_naming,
    ),
    AuditRule(
        "§2.11", "HOUSE_STYLE.md §2.11", "FAIL", "pyproject.toml exists", _check_required_files
    ),  # same checker covers it
    AuditRule(
        "§6.30",
        "HOUSE_STYLE.md §6.30",
        "FAIL",
        "MCP has @passthrough-decorated escape tool",
        _check_passthrough_exists,
    ),
]


def _unique_preserving_order(items):
    seen = set()
    out = []
    for x in items:
        if id(x) not in seen:
            seen.add(id(x))
            out.append(x)
    return out


ALL_RULES: list[Callable[[Path], list[Finding]]] = _unique_preserving_order(
    [r.check for r in REGISTRY]
)


def run_all_rules(project_root: Path) -> tuple[list[Finding], str]:
    """Run every rule. Returns (findings, mode) where mode is 'strict' or 'advisory'."""
    advisory = _is_advisory(project_root)
    findings: list[Finding] = []
    for rule in ALL_RULES:
        findings.extend(rule(project_root))
    if advisory:
        findings = [
            Finding(
                rule=f.rule,
                severity="WARN" if f.severity == "FAIL" else f.severity,
                message=f.message,
                hint=f.hint,
            )
            for f in findings
        ]
    return findings, ("advisory" if advisory else "strict")
