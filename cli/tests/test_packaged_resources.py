"""Release invariants for resources required by an installed CLI wheel."""

from importlib import resources

from adam_mcp_cli.templates_loader import render_tree


def test_audit_schema_modules_are_packaged():
    package = resources.files("adam_mcp_cli.schemas")
    assert package.joinpath("spec_md_lint.py").is_file()
    assert package.joinpath("llm_guide_lint.py").is_file()


def test_scaffold_templates_are_packaged():
    templates = resources.files("adam_mcp_cli").joinpath("templates", "_base")
    required = (
        "pyproject.toml.j2",
        "SPEC.md.j2",
        "server.json.j2",
        "tests/test_core_tools.py.j2",
        "{{name_snake}}/mcp/server.py.j2",
    )
    for relative_path in required:
        resource = templates.joinpath(*relative_path.split("/"))
        assert resource.is_file(), relative_path


def test_render_tree_handles_nested_resources_and_binary_files(tmp_path, monkeypatch):
    class FakeResource:
        def __init__(self, name, *, children=(), text=None, data=None):
            self.name = name
            self._children = tuple(children)
            self._text = text
            self._data = data

        def is_dir(self):
            return bool(self._children)

        def is_file(self):
            return not self._children

        def iterdir(self):
            return iter(self._children)

        def read_text(self, encoding="utf-8"):
            assert encoding == "utf-8"
            return self._text

        def read_bytes(self):
            return self._data

    root = FakeResource(
        "_base",
        children=(
            FakeResource(
                "{{name_snake}}",
                children=(FakeResource("value.txt.j2", text="{{ description }}"),),
            ),
            FakeResource("logo.bin", data=b"\x00\xff"),
        ),
    )
    monkeypatch.setattr("adam_mcp_cli.templates_loader.template_root", lambda: root)

    render_tree(tmp_path, {"name_snake": "demo", "description": "hello"})

    assert (tmp_path / "demo" / "value.txt").read_text() == "hello"
    assert (tmp_path / "logo.bin").read_bytes() == b"\x00\xff"
