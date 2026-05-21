"""Tests for adam_mcp_py.Workflow — implements §2.8."""

from adam_mcp_py import Result, Status, Workflow


class GreetWorkflow(Workflow):
    name = "greet"

    def run(self, name: str) -> Result[str]:
        # Simulates orchestrating multiple atomic ops
        step1 = f"hello {name}"
        step2 = step1.upper()
        return Result.ok(value=step2, metrics={"steps": 2})


def test_workflow_run_returns_result():
    wf = GreetWorkflow()
    r = wf.run("Adam")
    assert r.status == Status.OK
    assert r.value == "HELLO ADAM"
    assert r.metrics["steps"] == 2


def test_workflow_has_name():
    wf = GreetWorkflow()
    assert wf.name == "greet"
