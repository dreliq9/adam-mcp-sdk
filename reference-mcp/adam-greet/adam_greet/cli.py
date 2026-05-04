"""CLI for adam-greet — third interface layer alongside the lib and MCP. Implements §2.5."""
from __future__ import annotations
import json
import sys

from .workflows import MorningBriefingWorkflow


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: adam-greet <name>", file=sys.stderr)
        return 1
    name = sys.argv[1]
    r = MorningBriefingWorkflow().run(name=name)
    print(json.dumps(r.to_dict(), indent=2))
    return 0 if r.status.value == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
