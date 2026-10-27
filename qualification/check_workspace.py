"""Run the repository gates in the caller's isolated, locked environment."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    if output.is_relative_to(root):
        parser.error("qualification output must be outside the source checkout")
    output.mkdir(parents=True, exist_ok=False)
    temporary = output / "temporary"
    temporary.mkdir()
    env = os.environ.copy()
    env.update(
        TEMP=str(temporary),
        TMP=str(temporary),
        PYTHONDONTWRITEBYTECODE="1",
        PYTHONUTF8="1",
        PYTHONIOENCODING="utf-8",
        ADAM_MCP_OUTPUT_ROOT=str(temporary),
        RUFF_CACHE_DIR=str(output / "ruff-cache"),
    )
    commands = [
        ("lint", [sys.executable, "-m", "ruff", "check", "."]),
        ("format", [sys.executable, "-m", "ruff", "format", "--check", "."]),
    ]
    for name, path in [
        ("library", "python/tests"),
        ("cli", "cli/tests"),
        ("pack", "claude-pack/tests"),
        ("reference", "reference-mcp/adam-greet/tests"),
    ]:
        commands.append(
            (
                name,
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    path,
                    "-q",
                    "-p",
                    "no:cacheprovider",
                    "--basetemp",
                    str(temporary / name),
                ],
            )
        )
    commands.append(
        ("self-check", [sys.executable, "-m", "adam_mcp_cli.main", "audit", "--self-check"])
    )
    results = []
    for name, command in commands:
        log = output / f"{name}.log"
        with log.open("wb") as stream:
            result = subprocess.run(
                command, cwd=root, env=env, stdout=stream, stderr=subprocess.STDOUT, timeout=180
            )
        text = log.read_text(encoding="utf-8", errors="replace")
        counts = {
            key: sum(int(value) for value in re.findall(rf"(\d+) {key}", text))
            for key in ["passed", "failed", "skipped"]
        }
        row = {"name": name, "command": command, "exit_code": result.returncode, "tests": counts}
        results.append(row)
        print(json.dumps(row), flush=True)
        if result.returncode:
            print(text[-8000:], flush=True)
    receipt = {
        "python": sys.version,
        "executable": sys.executable,
        "results": results,
        "passed": all(row["exit_code"] == 0 for row in results),
    }
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    raise SystemExit(0 if receipt["passed"] else 1)


if __name__ == "__main__":
    main()
