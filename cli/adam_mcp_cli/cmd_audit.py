"""`adam-mcp audit` — mechanical conformance check vs HOUSE_STYLE.md."""

from __future__ import annotations
from pathlib import Path
from .audit_rules import run_all_rules


def audit_project(project_root: Path) -> dict:
    """Run all audit rules. Returns a Result-shaped report dict."""
    findings, mode = run_all_rules(project_root)
    fail_count = sum(1 for f in findings if f.severity == "FAIL")
    warn_count = sum(1 for f in findings if f.severity == "WARN")
    if fail_count:
        status = "FAIL"
        hint = f"Fix {fail_count} FAIL findings. See HOUSE_STYLE.md."
    elif warn_count:
        status = "WARN"
        hint = f"{warn_count} WARN finding(s) — review, but project is shippable."
    else:
        status = "OK"
        hint = None
    return {
        "status": status,
        "mode": mode,
        "value": None,
        "metrics": {"findings": len(findings), "fails": fail_count, "warns": warn_count},
        "diagnostics": [f.message for f in findings],
        "findings": [f.to_dict() for f in findings],
        "hint": hint,
    }
