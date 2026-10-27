"""Detect workspace manifests and the committed lock drifting apart."""

from pathlib import Path
import tomllib


def test_lock_matches_workspace_versions_and_mcp_requirements():
    root = Path(__file__).resolve().parents[2]
    workspace = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    lock = tomllib.loads((root / "uv.lock").read_text(encoding="utf-8"))
    packages = {package["name"]: package for package in lock["package"]}
    for member in workspace["tool"]["uv"]["workspace"]["members"]:
        project = tomllib.loads((root / member / "pyproject.toml").read_text(encoding="utf-8"))[
            "project"
        ]
        locked = packages[project["name"]]
        assert locked["version"] == project["version"], project["name"]
        assert locked["source"] == {"editable": member}
        for requirement in project["dependencies"]:
            if requirement.startswith("mcp=="):
                assert packages["mcp"]["version"] == requirement.removeprefix("mcp==")
                metadata = locked["metadata"]["requires-dist"]
                assert {"name": "mcp", "specifier": requirement.removeprefix("mcp")} in metadata
