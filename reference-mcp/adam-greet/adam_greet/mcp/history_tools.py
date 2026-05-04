"""History tools — stateful. Implements §4.19."""
from __future__ import annotations
import json
from adam_mcp_py import Result, validates, output_dir
from ..schema import RecordGreetingInput, RecentGreetingsInput


def _history_file():
    return output_dir("adam-greet") / "history.json"


def _load() -> list[str]:
    f = _history_file()
    if not f.exists():
        return []
    return json.loads(f.read_text())


def _save(items: list[str]) -> None:
    _history_file().write_text(json.dumps(items, indent=2))


@validates(RecordGreetingInput)
def record_greeting(input: RecordGreetingInput) -> Result[None]:
    """Persist a greeting to history. Implements §4.19, §2.10."""
    items = _load()
    items.append(input.greeting)
    _save(items)
    return Result.ok(value=None, metrics={"total": len(items)}, mode_tag="[LOCAL]")


@validates(RecentGreetingsInput)
def recent_greetings(input: RecentGreetingsInput) -> Result[list[str]]:
    """Return the N most recent greetings. Implements §4.19."""
    items = _load()
    return Result.ok(value=items[-input.n :], metrics={"total": len(items)}, mode_tag="[LOCAL]")
