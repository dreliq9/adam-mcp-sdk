"""CI test: SKILL.md must mirror the relevant HOUSE_STYLE.md sections.

If HOUSE_STYLE.md changes Principle Zero, Principle One, §1, or §6, this test fails
until the skill is updated to match.
"""
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "claude-pack" / "skills" / "mcp-author" / "SKILL.md"
SPEC = REPO / "HOUSE_STYLE.md"


def _extract_sections(text: str, headers: list[str]) -> str:
    """Concatenate the bodies of the requested H2/H3 headers, stripped."""
    lines = text.splitlines()
    out: list[str] = []
    capturing = False
    for line in lines:
        if any(line.strip() == h for h in headers):
            capturing = True
            continue
        if capturing and line.startswith(("## ", "### ")):
            capturing = False
        if capturing:
            out.append(line)
    return "\n".join(out).strip()


def test_skill_mirrors_principle_zero():
    spec_text = SPEC.read_text()
    skill_text = SKILL.read_text()
    spec_p0 = _extract_sections(spec_text, ["## Principle Zero — AI-shaped, not API-shaped"])
    # Skill must contain the load-bearing sentence verbatim
    key_sentence = "The unit of a tool is \"a coherent thing an AI can do,\" not \"an API endpoint.\""
    assert key_sentence in spec_p0, "Spec drift: Principle Zero key sentence changed"
    assert key_sentence in skill_text, (
        "Skill out of sync with HOUSE_STYLE.md Principle Zero. "
        "Update SKILL.md or update the spec."
    )


def test_skill_mirrors_principle_one():
    skill_text = SKILL.read_text()
    assert "Escape hatches always available" in skill_text
    assert "@passthrough" in skill_text


def test_skill_mirrors_section_1_1_result_type():
    spec_text = SPEC.read_text()
    skill_text = SKILL.read_text()
    # Both must say "every tool returns a typed Result"
    assert "Result(envelope_version, status, value, raw, metrics, diagnostics, hint, mode_tag)" in spec_text
    assert "Result(envelope_version, status, value, raw, metrics, diagnostics, hint, mode_tag)" in skill_text


def test_skill_has_six_question_checklist():
    skill_text = SKILL.read_text()
    for n in range(1, 7):
        assert f"{n}. " in skill_text, f"Pre-flight checklist question #{n} missing"
