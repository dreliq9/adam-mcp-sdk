"""Qualify installed wheels and a generated project outside the SDK checkout."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib


PROTOCOL_PROBE = r"""
import asyncio
import importlib.metadata as metadata
import json
from pathlib import Path
import sys
from mcp import Client
from mcp.client.stdio import StdioServerParameters, stdio_client

async def probe(module, cwd, tool, arguments, expected):
    rows = []
    for mode in ["auto", "legacy"]:
        params = StdioServerParameters(
            command=sys.executable, args=["-I", "-m", module], cwd=cwd,
            env={"ADAM_MCP_OUTPUT_ROOT": str(Path(cwd) / "output"), "PYTHONUTF8": "1"},
        )
        async with Client(stdio_client(params), mode=mode, read_timeout_seconds=10) as client:
            tools = await client.list_tools()
            assert tool in {entry.name for entry in tools.tools}
            response = await client.call_tool(tool, arguments)
            assert not response.is_error, response
            envelope = response.structured_content["result"]
            assert envelope["status"] == "OK", envelope
            assert envelope["envelope_version"] == 1
            assert expected in envelope["value"], envelope
            assert json.loads(response.content[0].text) == envelope
            rows.append({"module": module, "mode": mode, "status": "passed"})
    return rows

async def main():
    assert metadata.version("adam-mcp-py") == "0.3.3"
    assert metadata.version("adam-mcp-cli") == "0.2.3"
    assert metadata.version("mcp") == "2.0.0"
    rows = await probe("wheel_demo.mcp.server", sys.argv[1], "example_tool", {"input": {"name": "Ada"}}, "hello Ada")
    rows += await probe("adam_greet.mcp.server", sys.argv[1], "compose_greeting", {"input": {"name": "Ada", "formality": 5}}, "Ada")
    print(json.dumps({"protocol_cases": rows, "versions": {name: metadata.version(name) for name in ["adam-mcp-py", "adam-mcp-cli", "mcp", "pydantic"]}}))

asyncio.run(main())
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uv", required=True)
    parser.add_argument("--dist", type=Path, required=True)
    parser.add_argument("--constraints", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    root = Path(__file__).resolve().parents[1]
    if output.is_relative_to(root):
        parser.error("output must be outside the source checkout")
    output.mkdir(parents=True, exist_ok=False)
    outside = output / "outside"
    outside.mkdir()
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env.pop("VIRTUAL_ENV", None)
    env.update(PYTHONUTF8="1", PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    commands = []

    def run(label: str, command: list[str], expected: int = 0) -> str:
        result = subprocess.run(command, cwd=outside, env=env, capture_output=True, timeout=180)
        text = (result.stdout + result.stderr).decode("utf-8", errors="replace")
        (output / f"{label}.log").write_text(text, encoding="utf-8")
        commands.append({"label": label, "command": command, "exit_code": result.returncode})
        if result.returncode != expected:
            raise RuntimeError(f"{label} returned {result.returncode}: {text[-6000:]}")
        return result.stdout.decode("utf-8")

    environment = output / "installed"
    run("venv", [args.uv, "venv", "--python", sys.executable, str(environment)])
    scripts = environment / ("Scripts" if os.name == "nt" else "bin")
    python = scripts / ("python.exe" if os.name == "nt" else "python")
    cli = scripts / ("adam-mcp.exe" if os.name == "nt" else "adam-mcp")
    wheels = sorted(args.dist.resolve().glob("*.whl"))
    assert len(wheels) == 3
    run(
        "install-wheels",
        [
            args.uv,
            "pip",
            "install",
            "--offline",
            "--python",
            str(python),
            "--constraint",
            str(args.constraints.resolve()),
            *map(str, wheels),
        ],
    )
    run("installed-help", [str(cli), "--help"])
    generated = output / "consumer" / "wheel-demo"
    description = 'Installed "wheel" scaffold with a backslash \\ and Unicode ☃'
    run(
        "generate",
        [str(cli), "new", "wheel-demo", "--description", description, "--target", str(generated)],
    )
    project = tomllib.loads((generated / "pyproject.toml").read_text(encoding="utf-8"))
    descriptor = json.loads((generated / "server.json").read_text(encoding="utf-8"))
    assert project["project"]["description"] == descriptor["description"] == description
    assert "mcp==2.0.0" in project["project"]["dependencies"]
    run("audit-generated", [str(cli), "audit", str(generated)])
    run("upgrade-dry-run", [str(cli), "upgrade", str(generated), "--to", "0.3.3", "--dry-run"])
    message = run("self-check-outside-repo", [str(cli), "audit", str(outside), "--self-check"], 1)
    assert "adam-mcp-sdk checkout" in message and "Traceback" not in message
    run(
        "install-generated",
        [
            args.uv,
            "pip",
            "install",
            "--offline",
            "--python",
            str(python),
            "--constraint",
            str(args.constraints.resolve()),
            str(generated),
        ],
    )
    probe = output / "protocol_probe.py"
    probe.write_text(PROTOCOL_PROBE, encoding="utf-8")
    protocol = json.loads(run("stdio-protocol", [str(python), "-I", str(probe), str(outside)]))
    receipt = {
        "status": "passed",
        "commands": commands,
        "wheels": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in wheels},
        "protocol": protocol,
        "checkout_imports": False,
        "registry_installs_offline": True,
        "running_mcps_changed": False,
    }
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps(receipt), flush=True)


if __name__ == "__main__":
    main()
